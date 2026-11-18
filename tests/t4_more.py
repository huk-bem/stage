import sys, json, time
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

# ---- A: Musik-Presets liefern hörbares Signal, Ducking, Stopp
with App(path) as a:
    pg=a.pg
    levels={}
    for name in ['soft','energetic','corporate','tension']:
        a.ev(f"scenesTimeline[0].bgMusic='{name}'; scenesTimeline[0].characters.forEach(c=>c.script=''); scenesTimeline[0].duration=4; renderObjectTimeline();")
        a.ev("document.getElementById('previewSceneBtn').click()")
        pg.wait_for_timeout(1700)
        mx=0
        for i in range(12):
            mx=max(mx,a.ev("Music.rms()")); pg.wait_for_timeout(60)
        levels[name]=mx
        pg.wait_for_function("!Player.running",timeout=10000)
        pg.wait_for_timeout(900)
        after=max(a.ev("Music.rms()") for _ in range(3))
        check(mx>0.004,f'Musik „{name}“ erzeugt Signal (RMS {mx:.4f}) und endet danach (RMS {after:.4f})')
        check(after<mx*0.3 or after<0.002,f'Musik „{name}“ klingt nach Szenenende aus')
    # Ducking
    a.ev("scenesTimeline[0].bgMusic='soft'; scenesTimeline[0].duration=10; scenesTimeline[0].characters[0].script='Das ist ein etwas längerer Satz, damit die Musik leiser werden kann.'; scenesTimeline[0].characters[0].speechStart=3.5; scenesTimeline[0].characters[1].script=''; renderObjectTimeline();")
    a.ev("document.getElementById('previewSceneBtn').click()"); pg.wait_for_timeout(2600)
    lv0=max(a.ev("Music.rms()") for _ in range(10) if not pg.wait_for_timeout(50))
    pg.wait_for_timeout(2600)   # Sprecher aktiv
    duck=a.ev("Music.duckOn"); lv1=max(a.ev("Music.rms()") for _ in range(10) if not pg.wait_for_timeout(50))
    check(duck and lv1<lv0*0.7,f'Musik wird beim Sprechen leiser (Ducking): {lv0:.4f} → {lv1:.4f}')
    a.ev("Player.stop()"); pg.wait_for_timeout(1000)
    check(not a.ev("Music.timer") and max(a.ev("Music.rms()") for _ in range(3))<0.002,'Stopp beendet die Musik sofort')
    check(not a.errs,'keine Konsolenfehler (Musik) '+str(a.errs[:3]))

# ---- B: Überschneidung gleicher Startzeit → Warteschlange; Szene wartet aufs Sprechende
with App(path) as a:
    pg=a.pg
    a.ev("scenesTimeline[0].duration=3; scenesTimeline[0].characters[0].speechStart=0.5; scenesTimeline[0].characters[1].speechStart=0.5; renderObjectTimeline(); renderSpeakerTracks();")
    check('überschneiden' in a.ev("document.getElementById('timelineHint').textContent") or 'verlängert' in a.ev("document.getElementById('timelineHint').textContent"),'Warnhinweis bei gleichzeitigen Sprechern')
    check(a.ev("document.querySelectorAll('.timeline-bar.warn').length")>=2,'überschneidende Balken rot markiert')
    a.ev("window.__t=performance.now(); document.getElementById('previewSceneBtn').click()")
    pg.wait_for_function("!Player.running",timeout=40000)
    sp=a.ev("__sp.log"); st=[x for x in sp if x['ev']=='start']; en=[x for x in sp if x['ev']=='end']
    check(len(st)==2 and a.ev("__sp.maxActive")==1 and en[0]['t']<=st[1]['t'],'gleiche Startzeit: zweite Zeile wartet, kein Überlappen')
    dur=(en[-1]['t']-a.ev("__t"))/1000
    check(dur>3.5,f'Szene (3 s) wartet bis Sprechende ({dur:.1f} s) statt abzuschneiden')

# ---- C: Engine ohne Wortgrenzen (iOS/Google-Stimmen) → Lippen laufen trotzdem passend
with App(path) as a:
    pg=a.pg
    a.ev("__sp.boundaries=false")
    a.ev("scenesTimeline[0].characters[1].script=''; renderObjectTimeline();")
    a.ev("Player.startLine(scenesTimeline[0].characters[0])")
    pg.wait_for_function("!Player.running",timeout=30000)
    vs=[x for x in a.ev("__v") if x['id']==a.ev("scenesTimeline[0].characters[0].id")]
    kinds=set(x['v'] for x in vs)
    check(len(vs)>25 and len(kinds-{'joy','rest'})>=5,f'ohne Wortgrenzen: Mund wechselt {len(vs)}× ({sorted(kinds)})')
    # Sprechzeit vs Plan: letzter Nicht-Ruhe-Mund nahe Sprechende
    sp=a.ev("__sp.log"); en=[x for x in sp if x['ev']=='end'][-1]['t']; stt=[x for x in sp if x['ev']=='start'][0]['t']
    act=[x['t'] for x in vs if x['v'] in('a','e','i','o','u','mm','fv') and stt<=x['t']<=en+200]
    check(act and (en-act[-1])<900,f'Mundbewegung endet {(en-act[-1]):.0f} ms vor Stimmenende (Kalibrierung)')
    # zweiter Durchlauf: Kalibrierung verbessert Schätzung
    est1=a.ev("estimateSpeechDuration(scenesTimeline[0].characters[0])"); real=(en-stt)/1000
    check(abs(est1-real)<0.9,f'Dauer-Schätzung nach Kalibrierung ({est1:.2f} s) ≈ real ({real:.2f} s)')

# ---- D: Stimme fällt aus (Fehler) / Ton aus → stummer Takt statt Hängen
with App(path) as a:
    pg=a.pg
    a.ev("__sp.fail=true; scenesTimeline[0].characters[1].script=''; scenesTimeline[0].duration=5;")
    a.ev("Player.startLine(scenesTimeline[0].characters[0])")
    t0=time.time(); pg.wait_for_function("!Player.running",timeout=30000)
    check(a.ev("document.querySelectorAll('.bubble').length")==0 and (time.time()-t0)>2,'Sprachfehler: Animation läuft im Takt weiter und endet sauber')
    a.ev("__sp.fail=false; scenesTimeline[0].characters[0].audio=false; __sp.log.length=0")
    a.ev("Player.startLine(scenesTimeline[0].characters[0])"); pg.wait_for_function("!Player.running",timeout=30000)
    check(len(a.ev("__sp.log"))==0,'„Ton aus“: kein Sprechen, Lippen und Blase trotzdem')
    check(not a.errs,'keine Konsolenfehler (Ausfälle) '+str(a.errs[:3]))

# ---- E: Gesamtfilm mit 2 Szenen, Übergang, Szene 2 hat andere Figur & Objekt mit Dauer
with App(path) as a:
    pg=a.pg
    a.ev("scenesTimeline[0].duration=8; scenesTimeline[0].characters[0].speechStart=0.3; scenesTimeline[0].characters[1].speechStart=5.5; scenesTimeline[0].characters[1].clips=[]; renderObjectTimeline();")
    a.ev("addScene()"); a.ev("scenesTimeline[1].duration=5; scenesTimeline[1].transitionOut='fade'")
    amara=a.ev("addCharacterToStage('amara').id"); a.ev("(()=>{const c=getCurrentScene().characters[0]; c.script='Ihre Daten sind bei uns sicher.'; c.speechStart=1; c.facing='side'; c.action='walk'; c.clips=[{id:'x1',start:0.5,dur:2,pose:'walk'}]; c.x=80; renderCharacters(); renderSpeakerTracks(); renderObjectTimeline();})()")
    a.ev("addObjectToStage({type:'icon',iconId:'clipboard',w:90,h:90}); getCurrentScene().objects[0].timelineStart=1; getCurrentScene().objects[0].timelineDuration=1.5; getCurrentScene().objects[0].effect='pop'; renderObjectTimeline();")
    a.ev("selectScene(0)")
    a.ev("window.__t=performance.now(); document.getElementById('playAllBtn').click()")
    pg.wait_for_timeout(1000)
    check(a.ev("Player.kind")=='all' and a.ev("currentSceneIndex")==0,'Gesamtfilm startet in Szene 1')
    pg.wait_for_function("currentSceneIndex===1 && Player.running",timeout=30000)
    t_sw=(time.time())
    check(a.ev("(performance.now()-window.__t)/1000")>8,'Szenenwechsel erst nach Szene 1 inkl. Sprechende')
    pg.wait_for_timeout(900)
    # Objekt in Szene 2: bei 1s erscheint; nach 2.5s weg
    op=lambda: a.ev("(()=>{const e=document.querySelector('.stage-object'); return e?getComputedStyle(e).opacity:null})()")
    check(float(op())<0.05,'Objekt in Szene 2 vor seinem Einsatz unsichtbar') 
    pg.wait_for_timeout(1000)
    check(float(op())>0.9,'Objekt erscheint zur eingestellten Zeit (Pop)')
    # Amara läuft: Position ändert sich
    x0=a.ev("document.querySelector('.stage-character').getBoundingClientRect().x"); pg.wait_for_timeout(900); x1=a.ev("document.querySelector('.stage-character').getBoundingClientRect().x")
    check(x1-x0>8,f'Gehen bewegt die Figur über die Bühne (Δx={x1-x0:.0f}px bei Seitenansicht)')
    pg.wait_for_timeout(1300)
    check(float(op())<0.1,'Objekt verschwindet nach seiner Dauer (1,5 s)')
    pg.wait_for_function("!Player.running",timeout=30000)
    check(a.ev("currentSceneIndex")==0,'nach dem Film springt die Ansicht zurück in die ursprünglich gewählte Szene')
    check(a.ev("scenesTimeline[1].characters[0].x")==80,'Figurenposition nach Wegstrecke zurückgesetzt')
    check(a.ev("__sp.maxActive")==1,'durchgehend nie zwei Stimmen gleichzeitig')
    # Stopp mitten im Film
    a.ev("document.getElementById('playAllBtn').click()"); pg.wait_for_timeout(1500); a.ev("document.getElementById('stopAllBtn').click()"); pg.wait_for_timeout(300)
    check(not a.ev("Player.running") and a.ev("__sp.active")==0 and not a.ev("Speech.busy()") and a.ev("document.querySelectorAll('.bubble').length")==0,'Stopp mitten im Film räumt alles auf (Stimme, Blase, Zustand)')
    # schnelles Doppelstarten
    a.ev("document.getElementById('playAllBtn').click(); document.getElementById('playAllBtn').click(); document.getElementById('previewSceneBtn').click();")
    pg.wait_for_timeout(1200); a.ev("Player.stop()")
    check(not a.errs,'keine Konsolenfehler (Gesamtfilm) '+str(a.errs[:3]))
print('FAILS:',fails)
