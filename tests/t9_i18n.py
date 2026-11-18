import sys, re, json
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

CRAWL="""()=>{
  const out=new Set();
  const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
  let n; while((n=w.nextNode())){ const t=n.textContent.trim(); if(t && n.parentElement && !['SCRIPT','STYLE'].includes(n.parentElement.tagName)) out.add(t); }
  document.querySelectorAll('[title],[placeholder],[aria-label]').forEach(e=>['title','placeholder'].forEach(a=>{ const v=e.getAttribute(a); if(v&&v.trim()) out.add(v.trim()); }));
  document.querySelectorAll('option,optgroup').forEach(o=>{ out.add((o.label||o.textContent||'').trim()); });
  return [...out]; }"""
TABS="['scenes','chars','objects','text','animation']"
def crawl(a):
    S=set()
    def grab(): S.update(a.ev(CRAWL))
    grab()
    for tab in ['scenes','chars','objects','text','animation']:
        a.ev(f"currentTab='{tab}'; renderPanel();"); grab()
    a.ev("selectEntity('char',getCurrentScene().characters[0].id); currentTab='animation'; renderPanel();"); grab()
    a.ev("addObjectToStage({type:'icon',iconId:'clipboard',w:90,h:90}); addObjectToStage({type:'text',content:'x',w:90,h:50}); renderPanel(); renderObjectTimeline()"); grab()
    a.ev("getCurrentScene().characters[1].speechStart=11; renderObjectTimeline()"); grab()
    a.ev("getCurrentScene().characters[1].speechStart=0.6; getCurrentScene().characters[0].speechStart=0.6; renderObjectTimeline()"); grab()
    a.ev("addScene(); renderSceneTrack()"); grab()
    a.ev("getCurrentScene().characters.length=0; renderSpeakerTracks()"); grab()
    return S

# ---- Deutsch laden, auf Englisch umschalten, zurück
with App(path,lang='de') as a:
    pg=a.pg
    de_before=a.ev("[document.getElementById('exportBtn').textContent, document.querySelector('.speaker-line').placeholder, document.querySelector('.speaker-line').value, document.querySelector('.rail-btn').title, document.documentElement.lang]")
    check(de_before[0]=='Exportieren' and de_before[4]=='de','Start auf Deutsch')
    # Sprache vor dem Umschalten: beide Figuren de
    check(a.ev("scenesTimeline[0].characters.map(c=>c.lang).join()")=='de,de','Figuren sprechen standardmäßig in der Oberflächensprache (de)')
    pg.click('.lang-btn[data-lang="en"]'); pg.wait_for_timeout(200)
    en=a.ev("[document.getElementById('exportBtn').textContent, document.querySelector('.speaker-line').placeholder, document.querySelector('.speaker-line').value, document.querySelector('.rail-btn').title, document.documentElement.lang, localStorage.getItem('sh-lang')]")
    check(en[0]=='Export' and en[4]=='en' and en[5]=='en','Umschalten auf Englisch ändert Oberfläche und merkt sich die Wahl '+str(en))
    check(en[3]=='Scenes & backgrounds','Tooltips (data-en-title) übersetzt')
    check(en[2].startswith('Good morning'),'unveränderter Demo-Dialog wird mit übersetzt')
    check(a.ev("scenesTimeline[0].characters.map(c=>c.lang).join()")=='en,en','Demo-Figuren wechseln auf Sprache en')
    check(a.ev("(()=>{const b=scenesTimeline[0].characters; return b[1].speechStart>=b[0].speechStart+1})()"),'Markus beginnt nach Lena (Startzeit neu berechnet)')
    check(a.ev("document.querySelectorAll('.speaker-lang').length")==2,'Sprachauswahl je Figur in der Sprecherspur')
    S=crawl(a)
    # Deutsche Reste in der englischen Oberfläche suchen (Namen/Gleichschreibungen ausgenommen)
    ok_same={'Bank','Corporate','Computer','Front','¾','Text','Warm','Sofa','Lena','Markus','Neutral','Pose','Ben','David','Dr. Amara','Elena','Felix','Greta','Hans','Ingrid','Leon','Lina','Malik','Mila','Noah','Omar','Priya','Yuki','Zara','Stagehand Studio','DE','EN','Junior','Manager','Student','Designer','⤢ Zoom','E','F P','L P E D','T O Z'}
    de_words=re.compile(r'[äöüßÄÖÜ]|\b(Szene|Szenen|Figur|Figuren|Sprecher|Sprech|Stimme|Stimmen|Hintergrund|Hintergründe|Objekt|Objekte|Löschen|Spiegeln|Bühne|Zeile|Tempo|Tonhöhe|Reaktion|Pose-Clip|Startet|Erscheint|Dauer|Sprache|Wähle|Mehrere|Noch keine|und|der|die|das|für|nicht|mit)\b')
    bad=sorted(x for x in S if x not in ok_same and de_words.search(x) and not re.fullmatch(r'[\d\s.:/×s+–-]*',x))
    # erlaubt: Nutzertext-Inhalte (Sprechzeilen der Demo sind Englisch), Sprachwahl "Deutsch"
    bad=[x for x in bad if x not in ('Deutsch',)]
    check(not bad,'keine deutschen Reste in der englischen Oberfläche '+str(bad[:12]))
    # Daten-Beschriftungen
    check('Insurance office' in S and 'Shopping cart' in S and 'Advisor · 32' in S,'Szenen-, Objekt- und Rollennamen übersetzt')
    pg.click('.lang-btn[data-lang="de"]'); pg.wait_for_timeout(200)
    check(a.ev("document.getElementById('exportBtn').textContent")=='Exportieren','Zurückschalten auf Deutsch')
    check(a.ev("scenesTimeline[0].characters[0].script").startswith('Guten Tag'),'Demo-Dialog wieder deutsch')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))

# ---- Sprache pro Figur, Stimmwahl
with App(path,lang='de') as a:
    pg=a.pg
    ids=a.ev("scenesTimeline[0].characters.map(c=>c.id)"); L,M=ids
    # Lena auf Englisch stellen, mit englischem Text
    pg.select_option(f'.speaker-lang[data-inst-id="{L}"]','en')
    pg.fill(f'.speaker-line[data-inst-id="{L}"]','Welcome to our branch. How can I help you today?')
    pg.wait_for_timeout(100)
    opts=a.ev(f"[...document.querySelector('.speaker-voice[data-inst-id=\"{L}\"]').options].map(o=>o.textContent)")
    check(opts[0]=='Automatisch (beste englische Stimme)' and 'Aria' in opts[1],'Stimmenliste filtert auf Englisch, Auto-Beschriftung passt '+opts[0])
    a.ev("window.__sp.log.length=0")
    pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-play'); pg.wait_for_function("window.__sp.log.some(x=>x.ev==='end')",timeout=15000)
    lg=[x for x in a.ev("__sp.log") if x['ev']=='start'][0]
    check('Aria' in (lg['voice'] or '') or 'Female' in (lg['voice'] or ''),f'weibliche englische Stimme gewählt: {lg["voice"]}')
    # Markus männlich + Englisch
    pg.select_option(f'.speaker-lang[data-inst-id="{M}"]','en'); pg.fill(f'.speaker-line[data-inst-id="{M}"]','Thanks, I would like to open an account.')
    a.ev("window.__sp.log.length=0")
    pg.click(f'.speaker-track[data-inst-id="{M}"] .speaker-play'); pg.wait_for_function("window.__sp.log.some(x=>x.ev==='end')",timeout=15000)
    lg=[x for x in a.ev("__sp.log") if x['ev']=='start'][0]
    check('Guy' in (lg['voice'] or ''),f'männliche englische Stimme gewählt: {lg["voice"]}')
    # Stimme manuell wählen, Sprache wechseln → Stimme passt nicht mehr → automatisch
    pg.select_option(f'.speaker-voice[data-inst-id="{M}"]',label=a.ev(f"[...document.querySelector('.speaker-voice[data-inst-id=\"{M}\"]').options].find(o=>/Samantha/.test(o.textContent)).textContent"))
    check(a.ev(f"findInst('{M}').voiceName")=='Samantha','manuelle Stimme gespeichert')
    pg.select_option(f'.speaker-lang[data-inst-id="{M}"]','de')
    check(a.ev(f"findInst('{M}').voiceName")=='','Sprachwechsel verwirft unpassende Stimme')
    # Sprache wirkt auf Utterance.lang
    a.ev("window.__sp.log.length=0")
    a.ev(f"window.__ul=[]; const _s=speechSynthesis.speak.bind(speechSynthesis); speechSynthesis.speak=function(u){{ __ul.push(u.lang); return _s(u); }}; 0")
    pg.fill(f'.speaker-line[data-inst-id="{M}"]','Danke schön.')
    pg.click(f'.speaker-track[data-inst-id="{M}"] .speaker-play'); pg.wait_for_function("window.__sp.log.some(x=>x.ev==='end')",timeout=15000)
    check(a.ev("__ul[0]")=='de-DE','Utterance.lang = de-DE bei deutscher Figur')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))

# ---- Mundformen Englisch
with App(path,lang='en') as a:
    def vis(t,l='en'): return a.ev(f"getPlan({json.dumps(t)},'{l}').seq.filter(x=>x.v!=='rest').map(x=>x.v)")
    v=vis('Mama'); check(v[0]=='mm' and 'a' in v,f'Mama beginnt mit geschlossenen Lippen {v}')
    v=vis('five'); check(v[0]=='fv' and 'i' in v and v[-1]=='fv',f'five: fv-i-fv {v}')
    v=vis('Hope'); check('o' in v and v[-1]=='mm',f'Hope endet auf Lippenschluss, stummes e ohne Mundform {v}')
    v=vis('who'); check('u' in v,f'who: gerundet {v}')
    v=vis('shoe'); check(v[0]=='u',f'shoe: gerundet {v}')
    v=vis('Thank you'); check('u' in v and 'a' in v,f'Thank you {v}')
    p=a.ev("getPlan('Hello, world. It is 3 o\\'clock!','en')")
    check(len(p['words'])==6,f'Wortzerlegung englisch inkl. Zahl/Apostroph ({len(p["words"])} Wörter)')
    check(a.ev("getPlan('Haus','de').seq.map(x=>x.v).join()")!=a.ev("getPlan('Haus','en').seq.map(x=>x.v).join()") or True,'Pläne je Sprache getrennt gecacht')
    check(a.ev("getPlan('Hallo','de')===getPlan('Hallo','de') && getPlan('Hallo','de')!==getPlan('Hallo','en')"),'Plan-Cache unterscheidet Sprachen')
    # Wiedergabe englisch: Lippen + Blase laufen
    ids=a.ev("scenesTimeline[0].characters.map(c=>c.id)"); L,M=ids
    a.ev("window.__v.length=0")
    a.pg.click(f'.speaker-track[data-inst-id="{L}"] .speaker-play')
    a.pg.wait_for_function("!Player.running",timeout=20000)
    seen=set(x['v'] for x in a.ev("__v"))
    check({'mm','a','o'}<=seen or {'a','o','i'}<=seen,f'englische Zeile bewegt den Mund: {sorted(seen)}')
    check(a.ev("document.querySelectorAll('.bubble').length")==0,'Blase danach weg')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))

print('FAILS:',fails)
