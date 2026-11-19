import sys
from harness import App, DEFAULT_PATH
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

with App(path,lang='de') as a:
    pg=a.pg
    L,M=a.ev("scenesTimeline[0].characters.map(c=>c.id)")
    # ---- Auto-Timing
    a.ev(f"findInst('{L}').speechStart=5; findInst('{M}').speechStart=5.2; scenesTimeline[0].duration=30; renderSpeakerTracks()")
    pg.click('.auto-time'); pg.wait_for_timeout(150)
    r=a.ev(f"(()=>{{const l=findInst('{L}'),m=findInst('{M}'); return {{ls:l.speechStart, le:l.speechStart+estimateSpeechDuration(l), ms:m.speechStart, dur:scenesTimeline[0].duration, mend:m.speechStart+estimateSpeechDuration(m)}}}})()")
    check(abs(r['ls']-0.5)<0.01 and r['ms']>=r['le']+0.3,f'Zeilen nacheinander ohne Überlappung {r}')
    check(r['dur']>=r['mend'] and r['dur']<=r['mend']+2.5,f'Szenenlänge passt zur Sprechdauer ({r["dur"]} s)')
    # alle Szenen
    a.ev("addScene(); getCurrentScene().duration=40; addCharacterToStage('david'); getCurrentScene().characters[0].script='Test eins zwei drei.'; showScene(0)")
    pg.click('.auto-time-all'); pg.wait_for_timeout(100)
    check(a.ev("scenesTimeline[1].duration")<20,'„alle Szenen“ passt auch Szene 2 an')
    a.ev("deleteScene(1)")
    # ---- Start ab Position (Szenen-Lineal)
    a.ev("scenesTimeline[0].duration=12; renderObjectTimeline()")
    a.ev(f"findInst('{L}').clips=[{{id:'k1',start:0.5,dur:1.5,pose:'walk',to:{{x:700,y:470}}}}]; findInst('{L}').speechStart=0.2; findInst('{M}').speechStart=9; renderObjectTimeline()")
    a.ev("window.__sp.log.length=0")
    pg.locator('#objRuler').click(position={'x':436,'y':6}); pg.wait_for_timeout(500)
    check(a.ev("Player.running"),'Klick ins Lineal startet die Wiedergabe')
    t=a.ev("(performance.now()-Player.sceneT0)/1000")
    check(5.3<t<7.5,f'Start bei ca. 6 s (Zeit {t:.1f})')
    x=a.ev(f"charEl('{L}').offsetLeft"); check(abs(x-(700-a.ev(f"findInst('{L}').w")/2))<6,f'abgeschlossenes Gehen: Figur steht schon am Ziel ({x})')
    check(not a.ev("__sp.log.some(x=>/Guten Tag/.test(x.text))"),'Zeile davor wird nicht mehr gesprochen')
    # ---- Pause/Weiter
    pg.click('#pauseBtn'); pg.wait_for_timeout(200)
    check(not a.ev("Player.running") and a.ev("!!Player.paused") and a.ev("document.getElementById('pauseBtn').textContent").startswith('▶'),'Pause hält an, Knopf wird „Weiter“')
    t0=a.ev("Player.paused.t"); check(5.3<t0<9,f'Pausenzeit gemerkt ({t0:.1f})')
    pg.click('#pauseBtn'); pg.wait_for_timeout(400)
    check(a.ev("Player.running") and a.ev("(performance.now()-Player.sceneT0)/1000")>=t0-0.1,'Weiter setzt an derselben Stelle fort')
    pg.click('#stopAllBtn'); pg.wait_for_timeout(200)
    check(not a.ev("Player.running") and not a.ev("!!Player.paused"),'Stopp beendet alles')
    # ---- Gesamtfilm-Lineal
    a.ev("addScene(); getCurrentScene().duration=8; showScene(0)")
    pg.locator('.master-ruler-wrap').click(position={'x':780,'y':8}); pg.wait_for_timeout(400)
    check(a.ev("Player.running && Player.order[Player.pos]")==1,'Klick ins Gesamt-Lineal springt in Szene 2')
    pg.click('#stopAllBtn')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))

# ---- Kamera
with App(path,lang='de') as a:
    pg=a.pg
    L,M=a.ev("scenesTimeline[0].characters.map(c=>c.id)")
    pg.click('.timeline-add >> nth=0') if False else None
    a.ev("addCameraClip(); addCameraClip()")
    cams=a.ev("getCurrentScene().camera.map(c=>[c.target,c.zoom,c.start,c.dur])")
    check(len(cams)==2 and cams[0][0]=='char:'+L and cams[1][0]=='wide','Kamera-Clips angelegt (Zoom auf Figur, dann Gesamtbild)')
    check(pg.locator('.cam-zoom').count()==2,'Kamera-Zeile mit Zoom-Knopf in der Timeline')
    a.ev(f"(()=>{{const c=getCurrentScene().camera; c[0].start=0.3; c[0].dur=0.4; c[0].zoom=2.4; c[1].start=3.5; c[1].dur=0.5; renderObjectTimeline();}})()")
    a.ev(f"findInst('{L}').speechStart=0.5")
    pg.click('#previewSceneBtn'); pg.wait_for_timeout(1500)
    tr=a.ev("document.getElementById('stageCam').style.transform")
    check('scale(2.4)' in tr,f'während der Wiedergabe wird gezoomt {tr}')
    bb=a.ev("(()=>{const b=document.querySelector('.bubble'); const s=document.getElementById('stage').getBoundingClientRect(); if(!b) return null; const r=b.getBoundingClientRect(); return r.left>=s.left-2&&r.right<=s.right+2&&r.top>=s.top-2&&r.bottom<=s.bottom+2})()")
    check(bb in (True,None),f'Sprechblase bleibt im Bild beim Zoomen ({bb})')
    pg.wait_for_timeout(3000); tr2=a.ev("document.getElementById('stageCam').style.transform")
    check(tr2.startswith('translate(0.0px,0.0px) scale(1)') or tr2=='none' or 'scale(1)' in tr2,f'Gesamtbild-Clip fährt zurück {tr2}')
    pg.click('#stopAllBtn'); pg.wait_for_timeout(100)
    check(a.ev("document.getElementById('stageCam').style.transform")=='none','nach Stopp wieder normale Ansicht')
    # Kopie der Szene übernimmt die Kamera mit neuer Figur
    a.ev("duplicateScene(0)")
    cp=a.ev("(()=>{const B=scenesTimeline[1]; return B.camera[0].target==='char:'+B.characters[0].id})()")
    check(cp,'Szenenkopie: Kamera zeigt auf die kopierte Figur')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
