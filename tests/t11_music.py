import sys, math, struct, wave, subprocess, tempfile, os, shutil
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

tmp=tempfile.mkdtemp(); wav=os.path.join(tmp,'lied.wav'); R=22050
with wave.open(wav,'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(R)
    w.writeframes(struct.pack('<%dh'%(R*2),*[int(9000*math.sin(2*math.pi*330*i/R)) for i in range(R*2)]))   # 2,0 s
mp4=None
if shutil.which('ffmpeg'):
    mp4=os.path.join(tmp,'clip.mp4')
    r=subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','color=c=blue:s=64x64:d=1.5','-f','lavfi','-i','sine=frequency=440:duration=1.5','-shortest','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',mp4],capture_output=True)
    if r.returncode!=0: mp4=None

with App(path,lang='de') as a:
    pg=a.pg
    a.ev("""()=>{ window.__plays=[]; const P=HTMLMediaElement.prototype.play; HTMLMediaElement.prototype.play=function(){ window.__plays.push({src:(this.src||'').slice(0,5),loop:this.loop}); return P.apply(this,arguments); }; }; 0""")
    opts=a.ev("[...document.querySelectorAll('.timeline-bar select')].map(s=>[...s.options].map(o=>o.value))")
    mus=[o for o in opts if 'soft' in o][0]
    check('__upload' in mus,'Musik-Auswahl enthält „Eigene Datei laden“')
    # --- Datei laden (WAV)
    pg.evaluate("musicPickScene=getCurrentScene(); musicInput(); 0")
    pg.set_input_files('#musicFileInput',wav); pg.wait_for_function("musicLib.length===1",timeout=6000)
    sc="getCurrentScene()"
    check(a.ev(sc+".bgMusic")=='lib:m1','Szene verwendet geladene Datei')
    check(abs(a.ev("musicLib[0].dur")-2.0)<0.05,'Dauer erkannt '+str(a.ev("musicLib[0].dur")))
    check(a.ev("[...document.querySelectorAll('.timeline-bar select option')].some(o=>o.textContent.includes('lied'))"),'Dateiname in der Auswahl')
    check(a.ev("!!document.querySelector('.music-vol') && !!document.querySelector('.music-loop') && !!document.querySelector('.music-duck')"),'Regler Lautstärke/Schleife/Absenken sichtbar')
    # --- Abspielen: Pegel, Schleife, Absenken
    pg.wait_for_timeout(900)
    check(a.ev("Music.fileEl!==null && !Music.fileEl.paused"),'Datei läuft in der Vorschau')
    r1=a.ev("Music.rms()"); check(r1>0.01,f'Musik hörbar (RMS {r1:.3f})')
    check(a.ev("Music.fileEl.loop===true"),'Schleife standardmäßig an')
    a.ev("Music.stop()")
    a.ev("getCurrentScene().musicVol=80; Music.setOpts(getCurrentScene()); Music.play(getCurrentScene().bgMusic); 0")
    pg.wait_for_timeout(1200); loud=a.ev("Music.rms()")
    a.ev("Music.duck(true)"); pg.wait_for_timeout(1500); duck=a.ev("Music.rms()")
    check(duck<loud*0.6,f'Absenken beim Sprechen ({loud:.3f} → {duck:.3f})')
    a.ev("Music.duck(false)"); a.ev("getCurrentScene().musicDuck=false; Music.setOpts(getCurrentScene()); Music.duck(true)"); pg.wait_for_timeout(1500)
    nod=a.ev("Music.rms()"); check(nod>duck*1.3,f'Absenken abschaltbar ({duck:.3f} → {nod:.3f})')
    a.ev("Music.duck(false); getCurrentScene().musicDuck=true; Music.setOpts(getCurrentScene()); Music.stop()")
    # --- Wiedergabe der Szene mit Datei; Schleife bei kürzerer Datei als Szene
    a.ev("getCurrentScene().duration=5; 0")
    a.ev("document.getElementById('previewSceneBtn').click()"); pg.wait_for_timeout(2600)
    check(a.ev("Music.fileEl!==null && !Music.fileEl.paused"),'Szenen-Wiedergabe spielt die Datei (über Dateilänge hinaus, Schleife)')
    pg.wait_for_function("!Player.running",timeout=20000); pg.wait_for_timeout(700)
    check(a.ev("Music.fileEl===null && Music.name==='none'"),'Musik endet mit der Szene')
    # --- Entfernen
    a.ev("getCurrentScene().bgMusic='none'; renderObjectTimeline(); 0")
    check(a.ev("!document.querySelector('.music-vol')"),'Regler verschwinden bei „Keine“')
    # --- MP4 (nur wenn ffmpeg vorhanden und der Browser die Codecs kann)
    if mp4:
        can=a.ev("document.createElement('video').canPlayType('video/mp4; codecs=\"avc1.42E01E, mp4a.40.2\"')")
        if can:
            pg.evaluate("musicPickScene=getCurrentScene(); 0"); pg.set_input_files('#musicFileInput',mp4)
            pg.wait_for_function("musicLib.length===2",timeout=6000)
            check(a.ev("musicLib[1].kind")=='video' and abs(a.ev("musicLib[1].dur")-1.5)<0.2,'MP4 geladen, Tonspur-Dauer erkannt')
        else:
            print('SKIP MP4: dieser Browser (Playwright-Chromium) hat keine AAC/H.264-Codecs; MP4 daher nicht getestet')
    else:
        print('SKIP MP4: kein ffmpeg')
    # --- Fehlerfall: kaputte Datei
    bad=os.path.join(tmp,'kaputt.mp3'); open(bad,'wb').write(b'nope'*50)
    pg.on('dialog',lambda d:d.accept())
    n0=a.ev("musicLib.length"); pg.evaluate("musicPickScene=getCurrentScene(); 0"); pg.set_input_files('#musicFileInput',bad); pg.wait_for_timeout(1500)
    check(a.ev("musicLib.length")==n0,'kaputte Datei wird abgelehnt, nichts hinzugefügt')
    errs=[e for e in a.errs if 'Failed to load resource' not in e and 'MEDIA' not in e.upper()]
    check(not errs,'keine Konsolenfehler '+str(errs))
print('FAILS:',fails)
