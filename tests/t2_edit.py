import sys, json
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)
def bar_box(pg, row_label, idx=0):
    pg.evaluate("(l)=>{const r=[...document.querySelectorAll('.timeline-grid-row')].find(r=>r.querySelector('.timeline-row-label').title===l); r.scrollIntoView({block:'center'});}", row_label)
    return pg.evaluate("""([lbl,idx])=>{ const rows=[...document.querySelectorAll('.timeline-grid-row')].filter(r=>r.querySelector('.timeline-row-label').title===lbl);
       const r=rows[0]; const bars=r.querySelectorAll('.timeline-bar'); const b=bars[idx]; const x=b.getBoundingClientRect(), t=r.querySelector('.timeline-row-track').getBoundingClientRect();
       return {x:x.x,y:x.y,w:x.width,h:x.height,tx:t.x,tw:t.width}; }""",[row_label,idx])
def drag(pg, x0,y0,dx):
    pg.mouse.move(x0,y0); pg.mouse.down(); 
    for i in range(1,9): pg.mouse.move(x0+dx*i/8,y0)
    pg.mouse.up(); pg.wait_for_timeout(120)
with App(path) as a:
    pg=a.pg
    pg.evaluate("document.querySelector('.timeline-panel').scrollTop=0")
    # --- Sprache verschieben: Markus-Sprache bar nach links ziehen
    before=a.ev("scenesTimeline[0].characters[1].speechStart")
    bb=bar_box(pg,'Markus · Sprache'); dx=-(bb['tw']*2.0/12)    # -2 s
    drag(pg,bb['x']+bb['w']/2,bb['y']+bb['h']/2,dx)
    after=a.ev("scenesTimeline[0].characters[1].speechStart")
    check(abs((before-after)-2.0)<0.25,f'Sprachbalken Markus per Maus um 2 s nach links gezogen ({before}→{after})')
    check(a.ev("document.querySelector('.speaker-start[data-inst-id=\"'+scenesTimeline[0].characters[1].id+'\"]').value")==f'{after:.1f}','Startfeld in der Sprecherspur folgt dem Balken')
    # --- Startfeld → Balken
    a.ev("(()=>{const i=document.querySelectorAll('.speaker-start')[1]; i.value='7.5'; i.dispatchEvent(new Event('input',{bubbles:true}));})()")
    check(a.ev("scenesTimeline[0].characters[1].speechStart")==7.5,'Startfeld setzt speechStart (Zahl→Timeline)')
    bb=bar_box(pg,'Markus · Sprache'); 
    check(abs((bb['x']-bb['tx'])/bb['tw']*12-7.5)<0.3,'Balkenposition entspricht 7,5 s')
    # --- Pose-Clip hinzufügen / verschieben / Dauer / löschen
    n0=len(a.ev("scenesTimeline[0].characters[1].clips"))
    pg.evaluate("[...document.querySelectorAll('.timeline-grid-row')].find(r=>r.querySelector('.timeline-row-label').title==='Markus · Pose').querySelector('.timeline-add').click()")
    n1=len(a.ev("scenesTimeline[0].characters[1].clips"))
    check(n1==n0+1,'„＋ Pose“ legt einen Clip an')
    bb=bar_box(pg,'Markus · Pose'); s0=a.ev("scenesTimeline[0].characters[1].clips[0].start")
    drag(pg,bb['x']+10,bb['y']+bb['h']/2,bb['tw']*3/12)  # linker Rand = Greiffläche (rechts: Pose-Wahl und Ziel-Button)
    s1=a.ev("scenesTimeline[0].characters[1].clips[0].start")
    check(abs((s1-s0)-3)<0.3,f'Pose-Clip um 3 s nach rechts verschoben ({s0}→{s1})')
    bb=bar_box(pg,'Markus · Pose'); d0=a.ev("scenesTimeline[0].characters[1].clips[0].dur")
    hx=bb['x']+bb['w']-3
    drag(pg,hx,bb['y']+bb['h']/2,bb['tw']*1.5/12)
    d1=a.ev("scenesTimeline[0].characters[1].clips[0].dur")
    check(d1>d0+1.0,f'Pose-Clip Dauer über rechten Griff verlängert ({d0}→{d1})')
    # Pose per Select ändern + löschen
    pg.evaluate("""()=>{const r=[...document.querySelectorAll('.timeline-grid-row')].find(r=>r.querySelector('.timeline-row-label').title==='Markus · Pose'); const s=r.querySelector('select'); s.value='explain'; s.dispatchEvent(new Event('change',{bubbles:true}));}""")
    check(a.ev("scenesTimeline[0].characters[1].clips[0].pose")=='explain','Pose-Clip Typ per Auswahl geändert')
    pg.evaluate("""()=>{const r=[...document.querySelectorAll('.timeline-grid-row')].find(r=>r.querySelector('.timeline-row-label').title==='Markus · Pose'); const s=r.querySelector('select'); s.value='__del'; s.dispatchEvent(new Event('change',{bubbles:true}));}""")
    check(len(a.ev("scenesTimeline[0].characters[1].clips"))==n0,'Pose-Clip über „Entfernen“ gelöscht')
    # --- Reaktion: gekoppelt → ziehen entkoppelt
    check(a.ev("scenesTimeline[0].characters[0].reactionAuto")==True,'Lena-Reaktion startet gekoppelt an Sprechbeginn')
    bb=bar_box(pg,'Lena · Reaktion'); drag(pg,bb['x']+bb['w']*0.4,bb['y']+bb['h']/2,bb['tw']*2/12)
    check(a.ev("scenesTimeline[0].characters[0].reactionAuto")==False and a.ev("scenesTimeline[0].characters[0].reactionStart")>1.5,'Reaktionsbalken ziehen → feste Zeit (entkoppelt)')
    pg.evaluate("""()=>{const r=[...document.querySelectorAll('.timeline-grid-row')].find(r=>r.querySelector('.timeline-row-label').title==='Lena · Reaktion'); const s=r.querySelector('select'); s.value='__couple'; s.dispatchEvent(new Event('change',{bubbles:true}));}""")
    check(a.ev("scenesTimeline[0].characters[0].reactionAuto")==True,'Reaktion wieder an Sprechbeginn koppelbar')
    # --- Objekt hinzufügen: bleibt bis Szenenende, Start/Dauer ziehbar
    a.ev("addObjectToStage({type:'icon',iconId:'clipboard',w:90,h:90})")
    check(a.ev("scenesTimeline[0].objects[0].timelineDuration")==None,'neues Objekt bleibt standardmäßig bis Szenenende sichtbar')
    lbl=a.ev("[...document.querySelectorAll('.timeline-row-label')].map(l=>l.title).filter(t=>t==='Klemmbrett')[0]")
    bb=bar_box(pg,'Klemmbrett'); drag(pg,bb['x']+bb['w']*0.5,bb['y']+bb['h']/2,bb['tw']*4/12)
    check(abs(a.ev("scenesTimeline[0].objects[0].timelineStart")-4)<0.3,'Objekt-Balken auf 4 s verschoben')
    bb=bar_box(pg,'Klemmbrett'); drag(pg,bb['x']+bb['w']-3,bb['y']+bb['h']/2,-bb['tw']*3/12)
    dd=a.ev("scenesTimeline[0].objects[0].timelineDuration")
    check(dd is not None and dd<5.5,f'Objekt-Dauer verkürzt ({dd}) → verschwindet nach der Zeit')
    # --- Figur auf Bühne ziehen (skaliert)
    st=a.ev("(()=>{const e=document.querySelector('.stage-character'); const r=e.getBoundingClientRect(); return {x:r.x,y:r.y,w:r.width,h:r.height,ix:scenesTimeline[0].characters[0].x,k:STAGE_K}})()")
    pg.mouse.move(st['x']+st['w']/2,st['y']+st['h']/2); pg.mouse.down(); pg.mouse.move(st['x']+st['w']/2+60,st['y']+st['h']/2); pg.mouse.move(st['x']+st['w']/2+120,st['y']+st['h']/2); pg.mouse.up()
    nx=a.ev("scenesTimeline[0].characters[0].x"); vis=a.ev("document.querySelector('.stage-character').style.left")
    check(abs((nx-st['ix'])-120/st['k'])<3 and vis==f'{nx}px'.replace('.0px','px') or abs(float(vis[:-2])-nx)<0.01,f'Figur auf der Bühne ziehbar (Δ={nx-st["ix"]:.0f} logisch bei Skalierung {st["k"]:.2f})')
    # --- Blickrichtung/Dialog
    a.ev("selectEntity('char',scenesTimeline[0].characters[0].id); currentTab='animation'; renderPanel();")
    a.ev("[...document.querySelectorAll('.pose-btn')].find(b=>b.dataset.val==='side').click()")
    check(a.ev("scenesTimeline[0].characters[0].facing")=='side' and a.ev("document.querySelector('.stage-character svg').classList.contains('view-side')"),'Blickrichtung „Seite“ wirkt auf der Bühne')
    a.ev("[...document.querySelectorAll('.pose-btn')].find(b=>b.dataset.val==='dialog').click()")
    f0=a.ev("scenesTimeline[0].characters.map(c=>[c.facing,c.flipped])"); print(f0)
    check(f0[0][1]!=f0[1][1],'„Dialog: einander zuwenden“ → eine Figur gespiegelt')
    a.ev("[...document.querySelectorAll('.pose-btn')].find(b=>b.dataset.val==='front').click()")
    check(a.ev("document.querySelector('.stage-character svg').classList.contains('view-front')"),'Blickrichtung „Front“ wirkt')
    # --- Szenenlänge-Hinweis
    a.ev("scenesTimeline[0].characters[1].speechStart=11; renderObjectTimeline()")
    check('verlängert' in a.ev("document.getElementById('timelineHint').textContent"),'Hinweis, wenn Sprache über Szenenende hinausgeht')
    a.ev("document.querySelector('#timelineHint button').click()")
    check(a.ev("scenesTimeline[0].duration")>12,'Button verlängert die Szene')
    # --- Szenen hinzufügen / wechseln
    a.ev("addScene()"); check(a.ev("scenesTimeline.length")==2 and a.ev("currentSceneIndex")==1,'zweite Szene anlegen')
    a.ev("addCharacterToStage('amara')"); check(a.ev("getCurrentScene().characters.length")==1,'Figur in Szene 2 platzieren')
    a.ev("selectScene(0)"); check(a.ev("document.querySelectorAll('.stage-character').length")==2,'Szene 1 bleibt unverändert')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs[:3]))
print('FAILS:',fails)
