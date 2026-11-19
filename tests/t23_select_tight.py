import sys
from harness import App, DEFAULT_PATH
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

with App(path,lang='de',viewport=(1400,950)) as a:
    pg=a.pg; pg.on('dialog',lambda d:d.accept())
    # vier kurze Szenen ohne Sprache
    a.ev("scenesTimeline.splice(0,scenesTimeline.length); for(let i=0;i<4;i++){ const s=makeScene({label:'S'+(i+1),duration:1.2}); scenesTimeline.push(s);} selectScene(0); refreshAll(); History.reset();")
    check(pg.locator('.filmstrip-card .fs-sel input').count()==4 and pg.locator('.fs-play').count()==4,'jede Szene hat Häkchen und Abspiel-Symbol')
    check(a.ev("document.getElementById('playSelBtn').disabled"),'„Auswahl“ ist ohne Häkchen gesperrt')
    pg.check('.filmstrip-card >> nth=1 >> .fs-sel input'); pg.check('.filmstrip-card >> nth=3 >> .fs-sel input')
    check(a.ev("selectedSceneIdx().join()")=='1,3' and '(2)' in a.ev("document.getElementById('playSelBtn').textContent"),'Auswahl 2+4 gemerkt, Knopf zeigt (2)')
    pg.click('#playSelBtn'); pg.wait_for_timeout(300)
    check(a.ev("Player.kind")=='sel' and a.ev("Player.order.join()")=='1,3','Auswahl-Wiedergabe spielt nur Szene 2 und 4')
    seen=set(); 
    for _ in range(20):
        if a.ev("Player.running"): seen.add(a.ev("currentSceneIndex"))
        pg.wait_for_timeout(250)
    check(seen>={1,3} and 0 not in seen and 2 not in seen and not a.ev("Player.running"),'Szenen 1 und 3 werden übersprungen, Wiedergabe endet '+str(sorted(seen)))
    check(a.ev("currentSceneIndex")==0,'danach wieder die ursprüngliche Szene angewählt')
    # Pause/Weiter behält die Auswahl
    pg.click('#playSelBtn'); pg.wait_for_timeout(200); pg.click('#pauseBtn'); pg.wait_for_timeout(100)
    check(a.ev("Player.paused&&Player.paused.order.join()")=='1,3','Pause merkt sich die Auswahl'); pg.click('#pauseBtn'); pg.wait_for_timeout(200)
    check(a.ev("Player.order.join()")=='1,3','Weiter setzt die Auswahl fort'); a.ev("Player.stop()")
    # einzelne Szene über das Symbol
    pg.click('.filmstrip-card >> nth=2 >> .fs-play'); pg.wait_for_timeout(250)
    check(a.ev("Player.kind")=='scene' and a.ev("Player.order.join()")=='2' and a.ev("currentSceneIndex")==2,'▶ an der Szene spielt genau diese Szene'); a.ev("Player.stop()")
    # Export-Umfang
    check(abs(a.ev("Exporter.totalDur('sel')")-2.4)<0.01 and a.ev("Exporter.sceneList('sel').length")==2,'Export-Umfang „Auswahl“ summiert nur angehakte Szenen')
    pg.click('#exportBtn') if pg.locator('#exportBtn').count() else pg.click('text=Exportieren'); pg.wait_for_timeout(300)
    opts=a.ev("[...document.querySelectorAll('.dyn-dlg select')[0].options].map(o=>o.value).join()")
    check(opts=='all,scene,sel' and a.ev("document.querySelectorAll('.dyn-dlg select')[0].value")=='sel','Export-Dialog bietet „Auswahl“ an und wählt sie vor ('+opts+')')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(100)

    # ---- Leerraum entfernen
    a.ev("""(()=>{ scenesTimeline.splice(0,scenesTimeline.length); const s=makeScene({label:'T',duration:30}); scenesTimeline.push(s); selectScene(0); const A=addCharacterToStage('lena'), B=addCharacterToStage('markus');
      A.script='Hallo und willkommen.'; B.script='Danke, schön hier zu sein.'; A.speechStart=3; B.speechStart=16; A.clips=[{id:'x1',start:3,dur:2,pose:'wave'}]; B.clips=[{id:'x2',start:16,dur:2,pose:'point'}];
      s.objects.push({id:'o9',type:'text',content:'Titel',x:10,y:10,w:100,h:40,timelineStart:16,timelineDuration:null}); refreshAll(); History.reset(); window.__A=A; window.__B=B; })()""")
    ds=a.ev("estimateSpeechDuration(__A)")
    before=a.ev("({d:getCurrentScene().duration,idle:sceneIdleInfo(getCurrentScene()).idle})")
    pg.click('.tight-btn'); pg.wait_for_timeout(200)
    check('Spart ca.' in a.ev("document.querySelector('.tight-out').textContent"),'Dialog zeigt Vorschau der Zeitersparnis')
    pg.select_option('.tight-scope','scene'); pg.click('.tight-go'); pg.wait_for_timeout(300)
    r=a.ev("({d:getCurrentScene().duration,a:__A.speechStart,b:__B.speechStart,ca:__A.clips[0].start,cb:__B.clips[0].start,obj:getCurrentScene().objects[0].timelineStart})")
    check(abs(r['a']-0.4)<0.11,'Anfangspause auf 0,4 s gekürzt '+str(r))
    check(abs(r['b']-(r['a']+ds+0.6))<0.15,'Pause zwischen den Sprechern auf 0,6 s gekürzt')
    check(abs(r['ca']-r['a'])<0.11 and abs(r['cb']-r['b'])<0.11 and abs(r['obj']-r['b'])<0.11,'Posen-Clips und Objekte wandern mit den Sprechern')
    check(r['d']<before['d']-10,'Szene wesentlich kürzer ('+str(before['d'])+' → '+str(r['d'])+')')
    check(a.ev("estimateSpeechDuration(__B)+__B.speechStart+0.7")<=r['d']+0.01,'Szene endet nicht vor dem letzten Satz')
    # nichts mehr zu kürzen
    check(a.ev("tightenScene(JSON.parse(JSON.stringify(getCurrentScene())))")<0.6,'zweiter Durchlauf spart (fast) nichts mehr')
    # Überlappende Sprecher bleiben überlappend
    a.ev("__B.speechStart=__A.speechStart+0.5; tightenScene(getCurrentScene()); window.__ov=__B.speechStart-__A.speechStart")
    check(abs(a.ev("__ov")-0.5)<0.11,'überlappende Sprecher bleiben überlappend')
    # Szene ohne Sprache
    a.ev("(()=>{ const s=makeScene({label:'leer',duration:12}); scenesTimeline.push(s); })()")
    a.ev("tightenScene(scenesTimeline[1])"); check(a.ev("scenesTimeline[1].duration")==4,'Szene ohne Sprache wird auf 4 s begrenzt')
    # Rückgängig
    d1=a.ev("getCurrentScene().duration"); a.ev("History.commit()")
    a.ev("tightenScene(scenesTimeline[1])")
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
