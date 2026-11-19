import sys, json, urllib.parse
from harness import App, DEFAULT_PATH
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

state={'mm':0,'libre':0,'down':False}
def mm(route):
    state['mm']+=1
    if state['down']: return route.abort()
    u=urllib.parse.urlparse(route.request.url); q=urllib.parse.parse_qs(u.query)
    to=q['langpair'][0].split('|')[1]
    route.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body=json.dumps({'responseStatus':200,'responseData':{'translatedText':to.upper()+'~'+q['q'][0]}}))
def libre(route):
    if route.request.method=='OPTIONS': return route.fulfill(status=204,headers={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'})
    state['libre']+=1; d=json.loads(route.request.post_data)
    route.fulfill(status=200,content_type='application/json',headers={'access-control-allow-origin':'*'},body=json.dumps({'translatedText':'LT-'+d['target']+'~'+d['q']}))

with App(path,lang='de',viewport=(1400,950)) as a:
    pg=a.pg; msgs=[]
    pg.on('dialog',lambda d:(msgs.append(d.message),d.accept()))
    pg.route('**://api.mymemory.translated.net/**',mm); pg.route('**://lt.example.test/**',libre)
    a.ev("delete window.Translator")   # kein Browser-Übersetzer in der Testumgebung
    first="scenesTimeline[0].characters[0]"
    check(a.ev("ProjLangs.join()")=='de,en','Projektsprachen starten mit Deutsch+Englisch')

    # Sprache hinzufügen über das ＋ am Sprecher
    pg.click('.speaker-track >> nth=0 >> .add-lang-chip'); pg.wait_for_timeout(100)
    pg.select_option('.add-lang-select','es'); pg.click('.add-lang-ok'); pg.wait_for_timeout(200)
    check(a.ev("ProjLangs.join()")=='de,en,es' and pg.locator('.speaker-track >> nth=0 >> .lang-chip[data-lang=es]').count()==1,'Spanisch hinzugefügt, Chip erscheint')
    check(a.ev("[...document.querySelectorAll('.speaker-track')[0].querySelectorAll('.speaker-lang option')].map(o=>o.value).join()")=='de,en,es','Sprachauswahl der Zeile kennt Spanisch')
    check(pg.locator('.all-lang-btn[data-lang=es]').count()==1,'„Alle Sprecher auf:“ kennt Spanisch')

    # Übersetzen: EN ist von Hand geschrieben → Rückfrage; ES leer → direkt
    de_text=a.ev(first+".script")
    pg.click('.speaker-track >> nth=0 >> .speaker-translate'); pg.wait_for_timeout(900)
    tx=a.ev(first+".tx"); tr=a.ev(first+".tr")
    check(tx['es']['script']=='ES~'+de_text and tr.get('es'),'Spanisch automatisch übersetzt und markiert')
    check(any('eigenen Text' in m for m in msgs) and tx['en']['script']=='EN~'+de_text,'Handgeschriebenes Englisch nur nach Rückfrage überschrieben')
    check(a.ev("document.getElementById('trStatus').className.includes('ok')"),'Statusmeldung „Übersetzt“')
    check(a.ev("document.querySelector('.speaker-track .lang-chip[data-lang=es]').textContent").count('🌐')==1,'Chip zeigt 🌐 für maschinelle Übersetzung')
    # Rückfrage ablehnen
    msgs.clear(); a.ev(first+".tx.en={script:'My own English',voiceName:'',clip:null}; "+first+".tr.en=false;")
    # Automatik
    pg.check('.tr-auto-cb'); a.ev("Translate.seen=new WeakMap()"); pg.wait_for_timeout(300)
    n0=state['mm']
    line=pg.locator('.speaker-track >> nth=0 >> .speaker-line'); line.fill('Neuer Text für alles.'); pg.wait_for_timeout(4200)
    tx=a.ev(first+".tx")
    check(tx['es']['script']=='ES~Neuer Text für alles.','Automatik: Tippen → Spanisch folgt von selbst')
    check(tx['en']['script']=='My own English','Automatik überschreibt keinen von Hand geschriebenen Text')
    # Eigene Korrektur in Spanisch schützt vor Überschreiben
    pg.click('.speaker-track >> nth=0 >> .lang-chip[data-lang=es]'); pg.wait_for_timeout(200)
    line=pg.locator('.speaker-track >> nth=0 >> .speaker-line'); line.fill('Mi texto corregido.'); pg.wait_for_timeout(300)
    check(not a.ev(first+".tr.es"),'Manuelle Änderung entfernt die Übersetzungs-Markierung')
    pg.click('.speaker-track >> nth=0 >> .lang-chip[data-lang=de]'); pg.wait_for_timeout(200)
    pg.locator('.speaker-track >> nth=0 >> .speaker-line').fill('Noch ein neuer Satz.'); pg.wait_for_timeout(4500)
    check(a.ev(first+".tx.es.script")=='Mi texto corregido.','Korrigierter Text bleibt bei weiteren Änderungen erhalten')
    # Fehlerfall
    state['down']=True; pg.uncheck('.tr-auto-cb')
    a.ev(first+".tx.es={script:'',voiceName:'',clip:null}; "+first+".tr.es=false")
    pg.click('.speaker-track >> nth=0 >> .speaker-translate'); pg.wait_for_timeout(1500)
    check(a.ev("document.getElementById('trStatus').className.includes('err')") and a.ev(first+".tx.es.script")=='','Fehler wird angezeigt, nichts kaputt')
    state['down']=False

    # LibreTranslate-Engine über den Einstellungsdialog
    pg.click('#voicesBtn'); pg.select_option('#trEngine','libre'); pg.fill('#trUrl','http://lt.example.test/translate'); pg.fill('#trKey','k'); pg.click('#trTest'); pg.wait_for_timeout(1000)
    check(state['libre']>=1 and 'LT-' in a.ev("document.getElementById('trTestStatus').textContent"),'LibreTranslate-Test läuft über die eigene URL')
    check(a.ev("JSON.parse(localStorage.getItem('sh-translate')).engine")=='libre','Engine-Wahl gespeichert')
    pg.click('#voiceDlgClose')
    a.ev("Translate.cfg.engine='auto';Translate.cfg.url='';Translate.cache.clear()")

    # Mundformen/Pläne für weitere Sprachen
    pl=a.ev("({es:getPlan('Hola, buenos días','es').seq.filter(x=>x.v&&x.v!=='rest').length, ru:getPlan('Привет, как дела','ru').total, zh:getPlan('你好，欢迎光临','zh').total, ruw:getPlan('Привет, как дела','ru').words.length})")
    check(pl['es']>3 and pl['ru']>0 and pl['zh']>0 and pl['ruw']==3,'Lippenbewegung für ES/RU/ZH vorhanden '+str(pl))
    # Untertitel + Projekt
    cues=a.ev("Exporter.estimateCues('es','all').length")
    check(cues>=1,'Untertitel-Export kennt Spanisch')
    r=a.ev("(async()=>{ const o=await Project.serialize(false); Project.load(o.text); return ProjLangs.join(); })()")
    check(r=='de,en,es','Projekt speichern/laden behält die Sprachen '+str(r))
    check(a.ev("scenesTimeline[0].characters[0].tx.en.script")=='My own English' and not a.ev("scenesTimeline[0].characters[0].tr.en"),'Texte und Markierungen überleben Speichern/Laden')
    # Vorschau-Sprache: spanische Zeile abspielbar (stumm im Test)
    pg.click('.speaker-track >> nth=0 >> .lang-chip[data-lang=es]'); pg.wait_for_timeout(100)
    pg.click('.speaker-track >> nth=0 >> .speaker-play'); pg.wait_for_timeout(600); a.ev("Player.stop()")
    bad=[e for e in a.errs if 'Failed to load resource' not in e and 'net::ERR' not in e]
    check(not bad,'keine Konsolenfehler '+str(bad))
print('FAILS:',fails)
