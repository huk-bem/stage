import sys
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

with App(path,lang='de') as a:
    pg=a.pg
    L=a.ev("scenesTimeline[0].characters[0].id")
    a.ev(f"(()=>{{const i=findInst('{L}'); i.clips=[]; renderObjectTimeline(); }})()")
    # Pose-Clip anlegen: erster Clip = Gehen, Ziel per Pick-Modus setzen
    a.ev(f"addPoseClip(findInst('{L}'))")
    check(a.ev(f"findInst('{L}').clips[0].pose")=='walk' and a.ev(f"!findInst('{L}').clips[0].to"),'neuer Gehen-Clip ohne Ziel')
    check(pg.locator('.pose-target-btn, .bar-btn').count()>=1,'Ziel-Button an Pose-Balken sichtbar')
    a.ev(f"startPick(findInst('{L}'), findInst('{L}').clips[0])")
    check(a.ev("document.body.classList.contains('picking')") and a.ev("document.getElementById('pickBanner').textContent.length")>5,'Pick-Modus mit Hinweis-Banner')
    box=pg.locator('#stage').bounding_box()
    pg.mouse.click(box['x']+box['width']*0.8, box['y']+box['height']*0.85)
    pg.wait_for_timeout(150)
    to=a.ev(f"findInst('{L}').clips[0].to")
    check(to and to['x']>600,f'Gehen-Ziel durch Tipp auf die Bühne gesetzt {to}')
    check(not a.ev("document.body.classList.contains('picking')"),'Pick-Modus beendet')
    check(a.ev("document.querySelectorAll('.mk-pin.walk').length")==1,'Ziel-Pin auf der Bühne')
    # Pin ziehen
    pin=pg.locator('.mk-pin.walk').first.bounding_box()
    pg.mouse.move(pin['x']+8,pin['y']+pin['height']/2); pg.mouse.down(); pg.mouse.move(pin['x']-120,pin['y']+pin['height']/2,steps=6); pg.mouse.up()
    to2=a.ev(f"findInst('{L}').clips[0].to")
    check(to2['x']<to['x']-40,f'Pin lässt sich verschieben {to} → {to2}')
    # Wiedergabe: Figur läuft wirklich zum Ziel
    x0=a.ev(f"charEl('{L}').offsetLeft")
    a.ev(f"findInst('{L}').clips[0].start=0.2; findInst('{L}').clips[0].dur=1.5")
    pg.click("#playAllBtn")
    pg.wait_for_timeout(2300)
    x1=a.ev(f"charEl('{L}').offsetLeft")
    tx=to2['x']-a.ev(f"findInst('{L}').w")/2
    check(abs(x1-tx)<12 or abs(x1-x0)>60,f'Figur ist zum Ziel gelaufen ({x0} → {x1}, Ziel {tx:.0f})')
    pg.wait_for_function("!Player.running",timeout=30000)
    # Zeigen-Clip mit Punktziel
    a.ev(f"(()=>{{const i=findInst('{L}'); i.clips=[{{id:'clp',start:0.2,dur:2,pose:'point',at:{{kind:'pt',x:760,y:200}}}}]; renderObjectTimeline(); renderStageMarkers();}})()")
    check(a.ev("document.querySelectorAll('.mk-pin.point').length")==1,'Zeigen-Pin sichtbar')
    pg.click("#playAllBtn"); pg.wait_for_timeout(1100)
    aim=a.ev(f"(()=>{{const e=charEl('{L}'); return {{cls:e.className, aim:e.style.getPropertyValue('--aim')}}; }})()")
    check('pose-point' in aim['cls'] and aim['aim']!='',f'Arm zielt auf das Ziel {aim}')
    pg.wait_for_function("!Player.running",timeout=30000)
    # Löschen über das ✕
    pg.locator('.mk-pin.point .mk-x').first.click()
    check(a.ev(f"!findInst('{L}').clips[0].at"),'Ziel lässt sich am Pin entfernen')
    # Esc bricht Pick ab
    a.ev(f"startPick(findInst('{L}'), findInst('{L}').clips[0])"); pg.keyboard.press('Escape')
    check(not a.ev("document.body.classList.contains('picking')"),'Esc beendet Pick-Modus')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
