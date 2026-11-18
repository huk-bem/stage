import sys, json, math, struct, wave, subprocess, time, os, tempfile, socket
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
SERVER=os.path.join(os.path.dirname(os.path.abspath(path)),'scripts','tts_server.py')
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)
def free_port():
    s=socket.socket(); s.bind(('127.0.0.1',0)); p=s.getsockname()[1]; s.close(); return p

# Testdatei: 0.6 s Ton, 0.9 s Stille, 0.6 s Ton  (Lippen müssen in der Stille ruhen)
tmp=tempfile.mkdtemp(); clip=os.path.join(tmp,'beispiel.wav'); R=22050
with wave.open(clip,'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(R)
    fr=[]
    for seg,amp in [(0.6,9000),(0.9,0),(0.6,9000)]:
        for i in range(int(seg*R)): fr.append(int(amp*math.sin(2*math.pi*220*i/R)))
    w.writeframes(struct.pack('<%dh'%len(fr),*fr))
CLIP_DUR=2.1

HOOK="""()=>{ window.__plays=[]; const P=HTMLMediaElement.prototype.play; HTMLMediaElement.prototype.play=function(){ window.__plays.push({src:(this.currentSrc||this.src||'').slice(0,12),t:performance.now()}); return P.apply(this,arguments); }; }"""

with App(path,lang='de') as a:
    pg=a.pg; a.ev(HOOK)
    ids=a.ev("scenesTimeline[0].characters.map(c=>c.id)"); L,M=ids
    # ---------- eigene Audiodatei
    pg.set_input_files(f'.speaker-clipfile[data-inst-id="{L}"]',clip); pg.wait_for_function(f"!!findInst('{L}').clip",timeout=5000)
    check(a.ev(f"findInst('{L}').clip.name")=='beispiel.wav' and abs(a.ev(f"findInst('{L}').clip.dur")-CLIP_DUR)<0.05,'Audiodatei geladen, Dauer erkannt '+str(a.ev(f"findInst('{L}').clip.dur")))
    check('beispiel.wav' in a.ev(f"document.querySelector('.speaker-track[data-inst-id=\"{L}\"] .speaker-clipbtn').textContent"),'Dateiname im Button')
    check(a.ev(f"document.querySelector('.speaker-voice[data-inst-id=\"{L}\"]').disabled"),'Stimmenauswahl bei Audiodatei gesperrt')
    pg.fill(f'.speaker-line[data-inst-id="{L}"]','Hallo zusammen.')   # Transkript
    est=a.ev(f"estimateSpeechDuration(findInst('{L}'))")
    check(abs(est-(CLIP_DUR+0.25))<0.3,f'Timeline-Dauer folgt der Datei ({est:.2f} s)')
    a.ev("window.__sp.log.length=0; window.__v.length=0; window.__plays.length=0")
    a.ev("""window.__rest=[]; window.__lt0=performance.now()""")
    pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-play')
    t0=time.time()
    pg.wait_for_function("!Player.running",timeout=15000); el=time.time()-t0
    check(a.ev("__plays.length")==1,'Audiodatei wurde abgespielt')
    check(len([x for x in a.ev("__sp.log")])==0,'dabei keine Browser-Stimme')
    check(abs(el-CLIP_DUR)<0.9,f'Wiedergabe dauert so lang wie die Datei ({el:.2f} s)')
    vs=[x for x in a.ev("__v") if x['id']==L]
    # Zeitfenster der Stille: ca. 0.6–1.5 s nach Start → rest
    t_start=vs[0]['t'] if vs else 0
    seq=[(round((x['t']-t_start)/1000,2),x['v']) for x in vs]
    mid=[v for t,v in seq if 0.75<t<1.35]
    check(len(vs)>3 and 'rest' in [v for t,v in seq if t<2.1],f'Lippen bewegen sich nach Plan {seq[:10]}')
    # Zustand in der Stille: letzte Änderung vor 1.35 s muss rest sein
    before=[v for t,v in seq if t<1.35]
    check(before and before[-1]=='rest','in der Sprechpause der Datei ruhen die Lippen (Lautstärke-Gate)')
    # Ton aus → kein Audio, trotzdem Blase+Lippen
    a.ev(f"findInst('{L}').audio=false; window.__plays.length=0")
    pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-play'); pg.wait_for_function("!Player.running",timeout=15000)
    check(a.ev("__plays.length")==0,'„Ton“ aus: Audiodatei bleibt stumm')
    a.ev(f"findInst('{L}').audio=true")
    # Entfernen
    pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-clipdel')
    check(a.ev(f"findInst('{L}').clip")is None,'Audiodatei entfernen')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))

# ---------- eigener TTS-Server
port=free_port()
srv=subprocess.Popen([sys.executable,SERVER,'--engine','tone','--port',str(port),'--log-requests'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
try:
    for _ in range(40):
        try: socket.create_connection(('127.0.0.1',port),timeout=0.2).close(); break
        except OSError: time.sleep(0.1)
    with App(path,lang='en') as a:
        pg=a.pg; a.ev(HOOK)
        ids=a.ev("scenesTimeline[0].characters.map(c=>c.id)"); L,M=ids
        pg.click('#voicesBtn'); check(pg.is_visible('#voiceDlg'),'Stimmen-Dialog öffnet')
        pg.fill('#remoteUrl',f'http://127.0.0.1:{port}/tts'); pg.click('#remoteTest')
        pg.wait_for_function("document.getElementById('remoteStatus').className!==''",timeout=10000)
        check(a.ev("document.getElementById('remoteStatus').className")=='ok',f'Verbindungstest ok: {a.ev("document.getElementById(\'remoteStatus\').textContent")}')
        pg.keyboard.press('Escape'); check(not pg.is_visible('#voiceDlg'),'Dialog schließt (Esc), Eingabe wird übernommen')
        check(a.ev("Remote.url").endswith('/tts') and a.ev("JSON.parse(localStorage.getItem('sh-remote')).url").endswith('/tts'),'URL gespeichert')
        opts=a.ev(f"[...document.querySelector('.speaker-voice[data-inst-id=\"{L}\"]').options].map(o=>o.value)")
        check('__remote' in opts,'„Own TTS server“ erscheint in der Stimmenliste')
        pg.select_option(f'.speaker-voice[data-inst-id="{L}"]','__remote'); pg.select_option(f'.speaker-voice[data-inst-id="{M}"]','__remote')
        a.ev("window.__sp.log.length=0; window.__v.length=0; window.__plays.length=0")
        pg.click('#previewSceneBtn'); t0=time.time()
        pg.wait_for_function("!Player.running",timeout=40000); el=time.time()-t0
        plays=a.ev("__plays")
        check(len(plays)==2,f'beide Zeilen kamen vom Server ({len(plays)} Wiedergaben)')
        check(len(a.ev("__sp.log"))==0,'keine Browser-Stimme verwendet')
        check(plays[1]['t']>plays[0]['t']+800,'Zeilen laufen nacheinander (eine Stimme zur Zeit)')
        vs=set(x['v'] for x in a.ev("__v")); check(len(vs)>=4,f'Lippen bewegen sich {sorted(vs)}')
        log=srv.stdout
        # Server-Log lesen (nicht blockierend genug → kurz beenden unten)
        # Dauer der Server-Audio wurde gemessen → Timeline-Schätzung nutzt sie
        est=a.ev(f"estimateSpeechDuration(findInst('{L}'))"); d=a.ev(f"Remote.dur.get(Remote.key(findInst('{L}').script.trim(),'en'))")
        check(d and abs(est-(d+0.25))<0.05,f'Timeline-Dauer aus echter Server-Audiolänge ({est:.2f} s, Audio {d})')
        # Server fällt aus → stummer Takt, kein Hänger
        pg.click('#voicesBtn'); pg.fill('#remoteUrl','http://127.0.0.1:1/tts'); pg.keyboard.press('Escape')
        pg.select_option(f'.speaker-voice[data-inst-id="{L}"]','__remote')
        a.ev("window.__plays.length=0")
        t0=time.time(); pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-play'); pg.wait_for_function("!Player.running",timeout=40000); el=time.time()-t0
        check(a.ev("__plays.length")==0 and el<15,f'Server nicht erreichbar → Wiedergabe endet im stummen Takt ({el:.1f} s)')
        check(not [e for e in a.errs if 'PAGEERR' in e],'keine Seitenfehler '+str([e for e in a.errs if 'PAGEERR' in e]))
finally:
    srv.terminate()
    try: out=srv.communicate(timeout=3)[0]
    except Exception: out=''
reqs=[json.loads(l) for l in out.splitlines() if l.startswith('{')]
check(any(r['lang']=='en' and r['text'].startswith('Good morning') for r in reqs),f'Server erhielt Text + Sprache: {reqs[:2]}')
print('FAILS:',fails)
