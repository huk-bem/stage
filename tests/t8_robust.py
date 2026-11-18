import time
from harness import App, DEFAULT_PATH, OUT, launch_kwargs
fails=[]
def check(c,m):
    print(('PASS ' if c else 'FAIL ')+m)
    if not c: fails.append(m)
# A: echte (leere) Chrome-Sprachausgabe ohne Stimmen → darf nicht hängen
with App(DEFAULT_PATH,stub=False) as a:
    pg=a.pg
    a.ev("scenesTimeline[0].characters[1].script=''; scenesTimeline[0].duration=6; renderObjectTimeline()")
    t=time.time(); a.ev("document.getElementById('previewSceneBtn').click()")
    pg.wait_for_function("!Player.running",timeout=40000)
    check(True,f'ohne verfügbare Stimme endet die Wiedergabe sauber ({time.time()-t:.1f} s)')
    check(a.ev("document.querySelector('.speaker-voice').options.length")>=1,'Stimmenliste leer-sicher (Automatisch)')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs[:3]))
# B: gar keine Web-Speech-API
from playwright.sync_api import sync_playwright
import os
with sync_playwright() as p:
    b=p.chromium.launch(**launch_kwargs())
    pg=b.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script("delete window.speechSynthesis; delete window.SpeechSynthesisUtterance; Object.defineProperty(window,'localStorage',{get(){throw new Error('blocked')}});")
    pg.goto('file://'+os.path.abspath(DEFAULT_PATH)); pg.wait_for_timeout(500)
    pg.evaluate("scenesTimeline[0].characters[1].script=''; scenesTimeline[0].duration=5; renderObjectTimeline()")
    t=time.time(); pg.evaluate("document.getElementById('previewSceneBtn').click()")
    pg.wait_for_function("!Player.running",timeout=40000)
    check(not errs,f'ohne Web-Speech-API und ohne localStorage läuft alles im stummen Takt ({time.time()-t:.1f} s) {errs[:2]}')
    # viele Figuren: Renderkosten
    ms=pg.evaluate("""()=>{ const ids=characters.map(c=>c.id); for(let i=0;i<10;i++) addCharacterToStage(ids[i]); const t=performance.now(); for(let i=0;i<10;i++) renderCharacters(); return (performance.now()-t)/10; }""")
    check(ms<80,f'12 Figuren auf der Bühne: Neuaufbau {ms:.1f} ms')
    b.close()
print('FAILS:',fails)
