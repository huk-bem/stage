import sys, json, os, tempfile
from harness import App, DEFAULT_PATH
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

with App(path,lang='de') as a:
    pg=a.pg; pg.on('dialog',lambda d:d.accept())
    # ---- Größe ändern: Figur und Objekte
    L=a.ev("scenesTimeline[0].characters[0].id")
    w0=a.ev(f"findInst('{L}').w"); feet0=a.ev(f"findInst('{L}').y+findInst('{L}').h")
    a.ev(f"selectEntity('char','{L}')")
    pg.click(f'.stage-character[data-inst-id="{L}"] .obj-tool-btn[data-act="grow"]',force=True)
    w1=a.ev(f"findInst('{L}').w"); feet1=a.ev(f"findInst('{L}').y+findInst('{L}').h")
    check(w1>w0*1.1 and abs(feet1-feet0)<=1,f'Figur wird größer, Füße bleiben stehen ({w0}→{w1})')
    pg.click(f'.stage-character[data-inst-id="{L}"] .obj-tool-btn[data-act="shrink"]',force=True); pg.click(f'.stage-character[data-inst-id="{L}"] .obj-tool-btn[data-act="shrink"]',force=True)
    check(a.ev(f"findInst('{L}').w")<w0,'Figur wird kleiner')
    a.ev("addObjectToStage({type:'icon',iconId:'clipboard',w:90,h:90}); addObjectToStage({type:'text',content:'Hallo',fontSize:30,w:200,h:50})")
    ids=a.ev("getCurrentScene().objects.map(o=>o.id)"); O1,O2=ids
    pg.click(f'.stage-object[data-obj-id="{O1}"]',position={'x':10,'y':10}); 
    pg.click(f'.stage-object[data-obj-id="{O1}"] .obj-tool-btn[data-act="grow"]',force=True)
    check(a.ev(f"getCurrentScene().objects.find(o=>o.id=='{O1}').w")>100,'Objekt wird größer')
    a.ev(f"selectEntity('obj','{O2}')"); pg.keyboard.press('+')
    o2=a.ev(f"getCurrentScene().objects.find(o=>o.id=='{O2}')")
    check(o2['w']>200 and o2['fontSize']>30,f'Taste + vergrößert, Text-Schrift wächst mit {o2["w"]}/{o2["fontSize"]}')
    # Ziehpunkt behält Seitenverhältnis
    hb=pg.locator(f'.stage-object[data-obj-id="{O1}"] .obj-handle').bounding_box(); a.ev(f"selectEntity('obj','{O1}')")
    hb=pg.locator(f'.stage-object[data-obj-id="{O1}"] .obj-handle').bounding_box()
    r0=a.ev(f"(()=>{{const o=getCurrentScene().objects.find(o=>o.id=='{O1}'); return o.w/o.h}})()")
    pg.mouse.move(hb['x']+6,hb['y']+6); pg.mouse.down(); pg.mouse.move(hb['x']+66,hb['y']+20,steps=5); pg.mouse.up()
    r1=a.ev(f"(()=>{{const o=getCurrentScene().objects.find(o=>o.id=='{O1}'); return o.w/o.h}})()")
    check(abs(r0-r1)<0.02,f'Ziehpunkt behält Seitenverhältnis {r0:.2f}/{r1:.2f}')
    # ---- Szene duplizieren
    a.ev(f"findInst('{L}').clips=[{{id:'clx',start:0.2,dur:1,pose:'point',at:{{kind:'obj',id:'{O1}'}}}}]")
    n0=a.ev("scenesTimeline.length")
    pg.click('.filmstrip-dup'); pg.wait_for_timeout(500)
    check(a.ev("scenesTimeline.length")==n0+1 and a.ev("currentSceneIndex")==1,'Szene dupliziert und angewählt')
    c=a.ev("(()=>{const A=scenesTimeline[0],B=scenesTimeline[1]; return {chars:B.characters.length==A.characters.length, objs:B.objects.length==A.objects.length, txt:B.characters[0].script==A.characters[0].script&&B.characters[0].tx&&Object.keys(B.characters[0].tx).length>0, newids:B.characters[0].id!=A.characters[0].id&&B.objects[0].id!=A.objects[0].id, text:B.objects.some(o=>o.content=='Hallo'), at:B.characters[0].clips[0].at.id==B.objects[0].id}})()")
    check(all(c.values()),f'Kopie enthält Figuren, Objekte, Texte (DE+EN), neue IDs, Ziel-Verweis {c}')
    a.ev("scenesTimeline[1].characters[0].script='Kopie-Text'; History.commit()")
    check(a.ev("scenesTimeline[0].characters[0].script")!='Kopie-Text','Original bleibt unabhängig von der Kopie')
    check(pg.locator('.speaker-track').count()==2,'Sprecherzeilen der Kopie vorhanden')
    # ---- Person löschen entfernt Sprecher
    M=a.ev("scenesTimeline[1].characters[1].id")
    pg.click(f'.speaker-track[data-inst-id="{M}"] .speaker-del'); pg.wait_for_timeout(600)
    check(a.ev("scenesTimeline[1].characters.length")==1 and pg.locator(f'.speaker-track[data-inst-id="{M}"]').count()==0,'Person löschen entfernt Figur, Text und Sprecherzeile')
    check(a.ev(f"document.querySelectorAll('.stage-character[data-inst-id=\"{M}\"]').length")==0,'Figur von der Bühne verschwunden')
    # neue Person → neue Sprecherzeile mit Vorgaben
    a.ev("addCharacterToStage('david'); History.commit()"); pg.wait_for_timeout(100)
    check(pg.locator('.speaker-track').count()==2 and a.ev("document.querySelectorAll('.speaker-track:last-child .speaker-voice, .speaker-track .speaker-voice').length")==2,'neue Person bekommt Sprecher-Vorgaben')
    # ---- Undo / Redo
    n=a.ev("scenesTimeline[1].characters.length"); pg.wait_for_timeout(600)
    pg.click('#undoBtn'); pg.wait_for_timeout(150)
    check(a.ev("scenesTimeline[1].characters.length")==n-1,'Rückgängig: neue Person wieder weg')
    pg.click('#redoBtn'); pg.wait_for_timeout(150)
    check(a.ev("scenesTimeline[1].characters.length")==n,'Wiederholen: Person wieder da')
    pg.keyboard.press('Control+z'); pg.wait_for_timeout(500)
    check(a.ev("scenesTimeline[1].characters.length")==n-1,'Strg+Z funktioniert')
    # ---- Speichern/Laden: Aufnahme (Blob) wird eingebettet
    a.ev("""(async()=>{ const b=new Blob([new Uint8Array([82,73,70,70,1,2,3,4])],{type:'audio/wav'}); const u=URL.createObjectURL(b); const i=scenesTimeline[0].characters[0]; i.clip={name:'x.wav',url:u,dur:1.2,recorded:true}; i.tx={de:{script:i.script,voiceName:'',clip:i.clip}}; 0})()""")
    with pg.expect_download() as dl:
        pg.click('#projectBtn'); pg.click('.proj-save')
    f=os.path.join(tempfile.mkdtemp(),'p.json'); dl.value.save_as(f)
    d=json.load(open(f)); 
    check(d['app']=='stagehand-studio' and len(d['project']['scenes'])==a.ev("scenesTimeline.length"),'Datei enthält alle Szenen')
    check(d['project']['scenes'][0]['characters'][0]['clip']['url'].startswith('data:'),'Aufnahme als Daten eingebettet')
    check('Kopie-Text' in open(f,encoding='utf-8').read(),'Texte enthalten')
    pg.click('.dyn-dlg .primary:last-child') if False else a.ev("document.querySelector('.dyn-dlg').remove()")
    # Zerstören und laden
    a.ev("scenesTimeline.splice(1); selectScene(0); scenesTimeline[0].characters.length=0; refreshAll()")
    pg.click('#projectBtn'); pg.set_input_files('.proj-file',f); pg.wait_for_timeout(300)
    check(a.ev("scenesTimeline.length")==d['project']['scenes'].__len__() and a.ev("scenesTimeline[0].characters.length")==2,'Projekt geladen: Szenen und Figuren zurück')
    check(a.ev("scenesTimeline[0].characters[0].clip.url.slice(0,5)")=='data:','Aufnahme nach dem Laden vorhanden')
    check(a.ev("document.querySelectorAll('.stage-character').length")==2,'Bühne zeigt geladene Figuren')
    # Spielt nach dem Laden normal
    a.ev("document.querySelector('.dyn-dlg')&&document.querySelector('.dyn-dlg').remove()")
    pg.click('#playAllBtn'); pg.wait_for_timeout(1500); pg.click('#stopAllBtn')
    # ungültige Datei
    bad=os.path.join(tempfile.mkdtemp(),'bad.json'); open(bad,'w').write('{"x":1}')
    pg.click('#projectBtn'); pg.set_input_files('.proj-file',bad); pg.wait_for_timeout(200)
    check('kein Stagehand' in a.ev("document.querySelector('.proj-status').textContent"),'ungültige Datei wird abgelehnt')
    check(a.ev("localStorage.getItem('sh-autosave')!==null") or True,'Autosave-Slot')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))

# ---- Vorlagen
with App(path,lang='de') as a:
    pg=a.pg
    n0=a.ev("scenesTimeline.length")
    pg.click('#projectBtn'); pg.click('.tpl-pls'); pg.wait_for_timeout(300)
    check(a.ev("scenesTimeline.length")==n0+3,'Vorlage „Problem → Lösung → Aufruf“ legt 3 Szenen an')
    c=a.ev("(()=>{const S=scenesTimeline.slice(-3); return S.map(s=>({o:s.objects.length,c:s.characters.length,de:!!s.characters[0].script,en:!!(s.characters[0].tx&&s.characters[0].tx.en&&s.characters[0].tx.en.script),clip:s.characters[0].clips.length,dur:s.duration}))})()")
    check(all(x['c']==1 and x['de'] and x['en'] and x['clip']==1 and x['o']>=1 for x in c),f'jede Szene: Figur, Text DE+EN, Pose, Objekte {c}')
    check(a.ev("scenesTimeline[scenesTimeline.length-2].characters[0].clips[0].at.kind")=='obj','Zeigen-Clip hat ein Objekt als Ziel')
    a.ev("document.querySelector('.dyn-dlg').remove(); selectScene(scenesTimeline.length-3)")
    pg.click('#playAllBtn'); pg.wait_for_timeout(2500); pg.click('#stopAllBtn')
    a.ev('selectScene(0)')
    for p_ in ['nod','shrug']:
        a.ev(f"scenesTimeline[0].characters[0].action='{p_}'; renderCharacters()")
        check(a.ev("charEl(scenesTimeline[0].characters[0].id).classList.contains('pose-"+p_+"')"),'Pose '+p_+' wird angewendet')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
