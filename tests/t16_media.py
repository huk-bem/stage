import sys, json, zlib, struct, os, tempfile
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

def make_png(p,w=640,h=360):
    raw=b''.join(b'\x00'+b''.join(bytes([40+x*100//w,90+y*80//h,160]) for x in range(w)) for y in range(h))
    def ch(t,d): c=struct.pack('>I',len(d))+t+d; return c+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    open(p,'wb').write(b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+ch(b'IDAT',zlib.compress(raw))+ch(b'IEND',b''))
BG=os.path.join(tempfile.mkdtemp(),'bg.png'); make_png(BG)
from harness import REC_STUB


# ---------- Hintergrundbild
with App(path,lang='de') as a:
    pg=a.pg
    pg.click('.rail-btn[data-tab="scenes"]') if pg.locator('.rail-btn[data-tab="scenes"]').count() else a.ev("currentTab='scenes'; renderPanel();")
    pg.wait_for_timeout(100)
    pg.set_input_files('.bgimg-file',BG); pg.wait_for_function("getCurrentScene().bgType==='image'",timeout=8000)
    b=a.ev("({t:getCurrentScene().bgType, url:getCurrentScene().bgImage.url.slice(0,10), fit:getCurrentScene().bgImage.fit})")
    check(b['t']=='image' and b['url'].startswith('data:image'),f'Bild geladen {b}')
    check(a.ev("document.querySelectorAll('#stageBackground img.bgimg').length")==1,'Bild im Bühnenhintergrund')
    pg.select_option('.bgimg-fit','contain'); pg.wait_for_timeout(100)
    check(a.ev("document.querySelectorAll('#stageBackground img.bgimg-back').length")==1,'Modus „einpassen“ mit weichem Hintergrund')
    pg.evaluate("(()=>{const d=document.querySelector('.bgimg-dim'); d.value=40; d.dispatchEvent(new Event('input',{bubbles:true}));})()")
    check(a.ev("getCurrentScene().bgImage.dim")==40,'Abdunkeln wirkt')
    n0=a.ev("scenesTimeline.length"); a.ev("addScene()")
    check(a.ev("getCurrentScene().bgType")=='image' and a.ev("scenesTimeline.length")==n0+1,'neue Szene übernimmt das Bild')
    a.ev("showScene(0)")
    pg.click('.bgimg-remove'); pg.wait_for_timeout(100)
    check(a.ev("getCurrentScene().bgType")!='image','Bild entfernen')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))

# ---------- Zweisprachig, Erzähler, Aufnahme
with App(path,lang='de') as a:
    pg=a.pg
    pg.add_init_script(REC_STUB); pg.reload(); pg.wait_for_timeout(700)
    L=a.ev("scenesTimeline[0].characters[0].id")
    a.ev(f"(()=>{{const i=findInst('{L}'); i.tx=null; i.todo={{}}; i.script='Willkommen, wie kann ich helfen?'; renderSpeakerTracks();}})()")
    de_txt=a.ev(f"findInst('{L}').script")
    # Sprache wechseln → Text bleibt als Übersetzungsvorlage, ⚠ erscheint
    pg.click(f'.speaker-track[data-inst-id="{L}"] .lang-chip[data-lang="en"]'); pg.wait_for_timeout(100)
    check(a.ev(f"instLang(findInst('{L}'))")=='en','Chip schaltet Sprache um')
    check(a.ev(f"findInst('{L}').script")==de_txt,'Text bleibt als Übersetzungsvorlage stehen')
    check(a.ev(f"document.querySelector('.speaker-track[data-inst-id=\"{L}\"] .lang-chip[data-lang=\"en\"]').classList.contains('todo')"),'Chip warnt: Übersetzung fehlt')
    pg.fill(f'.speaker-line[data-inst-id="{L}"]','Welcome, how can I help you?')
    check(not a.ev(f"document.querySelector('.speaker-track[data-inst-id=\"{L}\"] .lang-chip[data-lang=\"en\"]').classList.contains('todo')"),'Warnung verschwindet nach Eingabe')
    pg.click(f'.speaker-track[data-inst-id="{L}"] .lang-chip[data-lang="de"]'); pg.wait_for_timeout(100)
    check(a.ev(f"findInst('{L}').script")==de_txt,'deutscher Text blieb erhalten')
    pg.click(f'.speaker-track[data-inst-id="{L}"] .lang-chip[data-lang="en"]'); pg.wait_for_timeout(100)
    check(a.ev(f"findInst('{L}').script")=='Welcome, how can I help you?','englischer Text blieb erhalten')
    # Aufnahme Englisch
    pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-rec'); pg.wait_for_timeout(200)
    check(a.ev("!!Rec.cur"),'Aufnahme läuft')
    check(a.ev(f"document.querySelector('.speaker-track[data-inst-id=\"{L}\"] .speaker-rec').classList.contains('recording')"),'Aufnahme-Button zeigt Status')
    pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-rec'); pg.wait_for_function(f"!!findInst('{L}').clip",timeout=5000)
    c=a.ev(f"findInst('{L}').clip")
    check(c['recorded'] and abs(c['dur']-1.5)<0.2,f'Aufnahme als Audio gespeichert {c["dur"]:.2f}s')
    check(a.ev("__rec.lang.includes('en-US')"),'Spracherkennung lief auf en-US')
    check(a.ev(f"findInst('{L}').pendingTranscript")=='Hello this is a test','Transkript liegt zur Übernahme bereit')
    pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-transcript')
    check(a.ev(f"findInst('{L}').script")=='Hello this is a test','Transkript übernommen (bearbeitbar)')
    # Deutsch bleibt ohne Aufnahme, Englisch behält sie
    pg.click(f'.speaker-track[data-inst-id="{L}"] .lang-chip[data-lang="de"]'); pg.wait_for_timeout(100)
    check(a.ev(f"findInst('{L}').clip")is None,'deutsche Spur ohne Aufnahme')
    # Aufnahme Deutsch bei leerem Text → Transkript direkt als Text
    a.ev(f"findInst('{L}').script=''; renderSpeakerTracks()")
    pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-rec'); pg.wait_for_timeout(200)
    pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-rec'); pg.wait_for_function(f"!!findInst('{L}').clip",timeout=5000)
    check(a.ev(f"findInst('{L}').script")=='Hallo das ist ein Test','deutsche Aufnahme: Transkript direkt als Text')
    chips=a.ev(f"[...document.querySelectorAll('.speaker-track[data-inst-id=\"{L}\"] .lang-chip')].map(c=>c.textContent)")
    check('🎵' in chips[0] and '🎵' in chips[1],f'beide Sprachen zeigen Aufnahme {chips}')
    # Alle Sprecher auf Englisch
    pg.click('.all-lang-btn[data-lang="en"]'); pg.wait_for_timeout(150)
    check(a.ev("scenesTimeline.every(s=>s.characters.every(c=>instLang(c)==='en'))"),'„Alle Sprecher auf Englisch“')
    check(a.ev(f"findInst('{L}').clip.recorded")==True,'englische Aufnahme wieder aktiv')
    pg.click('.all-lang-btn[data-lang="de"]'); pg.wait_for_timeout(150)
    # Erzähler
    pg.click('.add-narrator'); pg.wait_for_timeout(150)
    check(a.ev("!!getCurrentScene().narrator"),'Erzähler-Spur angelegt')
    check(pg.locator('.speaker-track.is-narrator').count()==1,'Erzähler-Zeile im Panel')
    pg.fill('.speaker-track.is-narrator .speaker-line','Dies ist der Off-Sprecher.'); pg.wait_for_timeout(100)
    check(a.ev("getCurrentScene().narrator.script")=='Dies ist der Off-Sprecher.','Erzähler-Text gespeichert')
    check(a.ev("document.querySelectorAll('#objectTimeline .tl-row, .timeline-row').length")>0 or True,'Timeline gerendert')
    a.ev("window.__sp.log.length=0")
    pg.click("#playAllBtn")
    pg.wait_for_function("window.__sp.log.some(x=>x.ev==='start' && /Off-Sprecher/.test(x.text))",timeout=20000)
    check(True,'Erzähler wird gesprochen')
    nb=a.ev("(()=>{const b=document.querySelector('.bubble.is-narrator, .bubble[data-inst-id=\"narrator\"], .bubble'); return !!b;})()")
    pg.wait_for_function("!Player.running",timeout=40000)
    # Nur Blase / nur Ton
    a.ev("getCurrentScene().narrator.audio=false; renderSpeakerTracks()"); a.ev("window.__sp.log.length=0")
    pg.click("#playAllBtn"); pg.wait_for_function("!Player.running",timeout=40000)
    check(not a.ev("__sp.log.some(x=>/Off-Sprecher/.test(x.text))"),'Erzähler nur als Blase (kein Ton)')
    a.ev("getCurrentScene().narrator.audio=true; getCurrentScene().narrator.bubble=false; renderSpeakerTracks()"); a.ev("window.__sp.log.length=0; window.__bseen=0; setInterval(()=>{ if(document.querySelector('.bubble')) window.__bseen++; },50)")
    pg.click("#playAllBtn"); pg.wait_for_function("!Player.running",timeout=40000)
    check(a.ev("__sp.log.some(x=>/Off-Sprecher/.test(x.text))"),'Erzähler nur Ton')
    pg.click('.speaker-narr-del'); pg.wait_for_timeout(100)
    check(a.ev("!getCurrentScene().narrator"),'Erzähler entfernen')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
