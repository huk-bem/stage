import sys
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)
with App(path,viewport=(1400,900)) as a:
    pg=a.pg
    L,M=a.ev("scenesTimeline[0].characters.map(c=>c.id)")
    # Optionen im Sprecher-Bereich
    check(a.ev("document.querySelectorAll('.speaker-bstyle').length")>=2,'Button „Blase gestalten“ je Sprecher')
    check(a.ev("document.querySelectorAll('.speaker-look').length")>=2,'Auswahl „Figurenstil“ je Sprecher')
    # Standard = bisheriges Aussehen
    a.ev("()=>{ const i=scenesTimeline[0].characters[0]; Bubble.show(i,{text:'Hallo liebe Welt',plan:{words:[{s:0,e:5},{s:6,e:11},{s:12,e:16}]}}); 0 }")
    pg.wait_for_timeout(350)
    cls=a.ev("document.querySelector('.bubble').className")
    check('bs-box' in cls and 'tl-point' in cls and 'rv-hl' in cls,'Standardblase unverändert (Rechteck, Spitze, Hervorheben) '+cls)
    check(a.ev("document.querySelectorAll('.bubble .w').length")==3,'Wörter als Spans')
    a.ev("()=>{ Bubble.clear(); 0 }")
    # Presets: jede Vorlage baut, hat Form-Klasse, keine NaN
    res=a.ev("""()=>BB_PRESETS.map(p=>{ const st=Object.assign({},BB_DEFAULT,p[3]); const b=buildBubbleEl(st,'Hallo Welt',[{s:0,e:5},{s:6,e:10}],{name:'X'}); return [p[0], b.className, b.querySelectorAll('.w').length, !!b.querySelector('svg.bb-bg'), b.style.getPropertyValue('--bff').length>0]; })""")
    check(len(res)==11 and all(r[2]==2 and r[4] for r in res),'alle 11 Vorlagen bauen eine Blase')
    check(all(r[3]==(r[0] in ('thought','shout')) for r in res),'SVG-Hintergrund nur bei Wolke/Zacken')
    # pro Figur unterschiedlich
    a.ev(f"""()=>{{ const cs=scenesTimeline[0].characters; cs[0].bs=Object.assign({{}},BB_DEFAULT,BB_PRESETS.find(p=>p[0]==='shout')[3]); cs[1].bs=Object.assign({{}},BB_DEFAULT,BB_PRESETS.find(p=>p[0]==='retro')[3]);
      cs.forEach(c=>Bubble.show(c,{{text:'Test Text hier',plan:{{words:[{{s:0,e:4}},{{s:5,e:9}},{{s:10,e:14}}]}}}})); 0 }}""")
    pg.wait_for_timeout(400)
    info=a.ev("[...document.querySelectorAll('.bubble')].map(b=>({id:b.dataset.instId,c:b.className,fs:getComputedStyle(b).fontSize,bg:b.style.getPropertyValue('--bg')}))")
    d={x['id']:x for x in info}
    check('bs-burst' in d[L]['c'] and 'bs-square' in d[M]['c'] and 'rv-type' in d[M]['c'],'Blasenstil gilt je Figur getrennt')
    check(d[L]['fs']=='24px' and d[M]['fs']=='16px','Schriftgröße je Figur '+d[L]['fs']+'/'+d[M]['fs'])
    # Schreibmaschine: noch nicht gesprochene Wörter unsichtbar
    a.ev(f"()=>{{ Bubble.update(scenesTimeline[0].characters[1],1); 0 }}")
    vis=a.ev("[...document.querySelectorAll('.bubble[data-inst-id=\"%s\"] .w')].map(w=>getComputedStyle(w).visibility)"%M)
    check(vis==['visible','visible','hidden'],'Schreibmaschine zeigt nur gesprochene Wörter '+str(vis))
    # in der Bühne und innerhalb der Grenzen
    box=a.ev("[...document.querySelectorAll('.bubble')].map(b=>({l:b.offsetLeft,t:b.offsetTop,w:b.offsetWidth,h:b.offsetHeight}))")
    check(all(b['l']>=0 and b['l']+b['w']<=960 and b['t']>=0 for b in box),'Blasen liegen innerhalb der Bühne '+str(box))
    a.ev("()=>{ Bubble.clear(); 0 }")
    # Untertitel-Balken unten mittig
    a.ev("()=>{ const i=scenesTimeline[0].characters[0]; i.bs=Object.assign({},BB_DEFAULT,BB_PRESETS.find(p=>p[0]==='subtitle')[3]); Bubble.show(i,{text:'Untertitel unten',plan:{words:[{s:0,e:9},{s:10,e:16}]}}); 0 }")
    pg.wait_for_timeout(350)
    bx=a.ev("(()=>{ const b=document.querySelector('.bubble'); return {l:b.offsetLeft,w:b.offsetWidth,t:b.offsetTop,h:b.offsetHeight,name:!!b.querySelector('.bb-name')}; })()")
    check(abs((bx['l']+bx['w']/2)-480)<4 and bx['t']+bx['h']>440,'Untertitel: mittig unten '+str(bx))
    check(bx['name'],'Untertitel: Sprechername angezeigt')
    a.ev("()=>{ Bubble.clear(); 0 }")
    # Reaktion → Zacken
    a.ev("()=>{ const i=scenesTimeline[0].characters[0]; i.bs=Object.assign({},BB_DEFAULT,{auto:true}); i.reaction='anger'; 0 }")
    rm=a.ev("Object.keys(MOOD_V)")
    check('anger' in rm,'Reaktionen vorhanden')
    # Dialog
    a.ev("()=>{ const i=scenesTimeline[0].characters[0]; i.bs=null; openBubbleDlg(i); 0 }")
    check(a.ev("!!document.querySelector('#bubbleDlg')"),'Dialog öffnet')
    check(a.ev("document.querySelectorAll('#bubbleDlg .bb-chip').length")==11,'11 Vorlagen im Dialog')
    a.ev("document.querySelector('#bubbleDlg .bb-chip[data-preset=thought]').click()")
    check(a.ev("document.querySelector('#bubbleDlg .bb-prev .bubble').className.includes('bs-cloud')"),'Vorlage wählen → Vorschau zeigt Wolke')
    a.ev("()=>{ const s=document.querySelector('#bubbleDlg select[data-k=font]'); s.value='serif'; s.dispatchEvent(new Event('change',{bubbles:true})); const r=document.querySelector('#bubbleDlg input[data-k=size]'); r.value='26'; r.dispatchEvent(new Event('input',{bubbles:true})); const b=document.querySelector('#bubbleDlg input[data-k=bold]'); b.checked=true; b.dispatchEvent(new Event('change',{bubbles:true})); 0 }")
    st=a.ev("scenesTimeline[0].characters[0].bs")
    check(st['font']=='serif' and st['size']==26 and st['bold'] and st['preset']=='custom' and st['shape']=='cloud','Schrift/Größe/Fett gespeichert, Vorlage „eigen“ '+str(st))
    pv=a.ev("(()=>{ const b=document.querySelector('#bubbleDlg .bb-prev .bubble'); return [b.classList.contains('b-bold'), b.style.getPropertyValue('--bfs')]; })()")
    check(pv==[True,'26px'],'Live-Vorschau folgt '+str(pv))
    pg.screenshot(path=OUT+'/shot_bubble_dialog.png')
    # auf alle übertragen
    a.ev("document.querySelector('#bubbleDlg .bb-all').click()")
    check(a.ev("scenesTimeline[0].characters.every(c=>c.bs&&c.bs.font==='serif'&&c.bs.shape==='cloud')"),'„Auf alle übertragen“')
    a.ev("document.querySelector('#bubbleDlg .bb-reset').click()")
    check(a.ev("scenesTimeline[0].characters[0].bs.shape")=='box' and a.ev("scenesTimeline[0].characters[1].bs.shape")=='cloud','Zurücksetzen nur bei dieser Figur')
    a.ev("document.querySelector('#bubbleDlg .bb-close').click()")
    check(a.ev("!document.querySelector('#bubbleDlg')"),'Dialog schließt')
    # Speichern/Laden
    js=a.ev("JSON.stringify(scenesTimeline[0].characters.map(c=>c.bs))")
    check('cloud' in js,'Blasenstil im Szenenzustand enthalten')
    # Figurenstil
    for lk in ['std','ink','toon','chibi']:
        a.ev(f"()=>{{ const s=document.querySelector('.speaker-look'); s.value='{lk}'; s.dispatchEvent(new Event('change',{{bubbles:true}})); 0 }}")
        pg.wait_for_timeout(100)
        check(a.ev("scenesTimeline[0].characters[0].look")==lk,f'Figurenstil {lk} gesetzt')
    ink=a.ev("charEl(scenesTimeline[0].characters[0].id).querySelector('svg').innerHTML.includes('#2A2230')")
    sc=a.ev("charEl(scenesTimeline[0].characters[0].id).querySelector('svg').innerHTML.includes('scale(1.4')")
    check(ink and sc,'Chibi: Kontur + Riesenkopf gerendert')
    # EN
    a.ev("()=>{ const i=scenesTimeline[0].characters[0]; openBubbleDlg(i); 0 }")
    check(a.ev("document.querySelector('#bubbleDlg h3').textContent.length")>5,'Dialogtitel vorhanden')
    check(len(a.errs)==0,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
