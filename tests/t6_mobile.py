import sys, json
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)
with App(path,viewport=(390,844),mobile=True) as a:
    pg=a.pg
    pg.screenshot(path=OUT+'/m1_load.png')
    ov=a.ev("({sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth})")
    check(ov['sw']<=ov['cw']+1,f"kein horizontaler Seiten-Überlauf ({ov})")
    k=a.ev("STAGE_K"); check(0.3<k<0.45,f'Bühne skaliert auf Handybreite (Faktor {k:.2f})')
    # Charaktere-Tab öffnen, Figur hinzufügen per Tap
    pg.tap('.rail-btn[data-tab="chars"]'); pg.wait_for_timeout(400)
    pg.screenshot(path=OUT+'/m2_chars.png')
    n0=a.ev("getCurrentScene().characters.length")
    pg.tap('.char-card >> nth=3'); pg.wait_for_timeout(300)
    check(a.ev("getCurrentScene().characters.length")==n0+1,'Figur per Tippen in die Bühne gesetzt')
    pg.tap('#sidebarCloseBtn'); pg.wait_for_timeout(300)
    # Animation-Tab
    pg.tap('.rail-btn[data-tab="animation"]'); pg.wait_for_timeout(400)
    pg.screenshot(path=OUT+'/m3_anim.png')
    pg.tap('.pose-btn[data-val="side"]'); pg.wait_for_timeout(200)
    check(a.ev("getCurrentScene().characters.slice(-1)[0].facing")=='side','Blickrichtung per Tipp geändert')
    pg.tap('#sidebarCloseBtn'); pg.wait_for_timeout(300)
    # Timeline scrollen & Touch-Drag eines Sprachbalkens (CDP touch)
    box=a.ev("""()=>{const r=[...document.querySelectorAll('.timeline-grid-row')].find(r=>r.querySelector('.timeline-row-label').title==='Lena · Sprache'); r.scrollIntoView({block:'center'}); const b=r.querySelector('.timeline-bar').getBoundingClientRect(), t=r.querySelector('.timeline-row-track').getBoundingClientRect(); return {x:b.x,y:b.y,w:b.width,h:b.height,tw:t.width}}""")
    s0=a.ev("scenesTimeline[0].characters[0].speechStart")
    cdp=pg.context.new_cdp_session(pg)
    x=box['x']+box['w']/2; y=box['y']+box['h']/2
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
    for i in range(1,9): cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':x+i*box['tw']*1.0/12/8*8/8*1,'y':y}]})
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]}); pg.wait_for_timeout(200)
    s1=a.ev("scenesTimeline[0].characters[0].speechStart")
    check(s1>s0+0.5,f'Sprachbalken per Finger verschiebbar ({s0}→{s1})')
    # Figur per Finger ziehen
    st=a.ev("(()=>{const e=document.querySelector('.stage-character'); const r=e.getBoundingClientRect(); return {x:r.x+r.width/2,y:r.y+r.height/2,ix:getCurrentScene().characters[0].x}})()")
    cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':st['x'],'y':st['y']}]})
    for i in range(1,6): cdp.send('Input.dispatchTouchEvent',{'type':'touchMove','touchPoints':[{'x':st['x']+i*10,'y':st['y']}]})
    cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]}); pg.wait_for_timeout(200)
    nx=a.ev("getCurrentScene().characters[0].x")
    check(abs(nx-st['ix'])>60,f'Figur per Finger verschiebbar (Δ={nx-st["ix"]:.0f} logisch)')
    # Abspielen
    pg.evaluate("window.scrollTo(0,0)"); pg.tap('#previewSceneBtn'); pg.wait_for_timeout(2400)
    pg.screenshot(path=OUT+'/m4_play.png')
    check(a.ev("Player.running")==True and len(a.ev("[...document.querySelectorAll('.bubble.on')]"))>=0,'Wiedergabe auf dem Handy startet')
    pg.tap('#stopSceneBtn'); pg.wait_for_timeout(300)
    check(not a.ev("Player.running"),'Stopp per Tippen')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs[:3]))
print('FAILS:',fails)
