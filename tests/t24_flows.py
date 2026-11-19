import sys
from harness import App, DEFAULT_PATH
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

for lang in ('de','en'):
  for tid,name in (('ads','Online-Werbung'),('tickets','Tickets')):
    with App(path,lang=lang,viewport=(1400,950)) as a:
        pg=a.pg
        n0=a.ev("scenesTimeline.length")
        n=a.ev(f"applyTemplate('{tid}')")
        sc=a.ev("scenesTimeline.slice(%d).map(s=>({lab:s.label,d:s.duration,ch:s.characters.length,sp:s.characters.map(c=>[c.script.length>20,c.tx&&Object.values(c.tx).some(t=>t.script.length>10),c.speechStart]),screen:s.objects.filter(o=>/^ui-(ad|events|seat|pay|eticket)/.test(o.iconId||'')).length,cur:s.objects.filter(o=>o.iconId==='ui-cursor').length,clk:s.objects.filter(o=>o.iconId==='ui-click').length,pt:s.characters.some(c=>c.clips.some(k=>k.pose==='point'&&k.at))}))"%n0)
        check(n==4 and len(sc)==4,f'[{lang}/{tid}] 4 Szenen angelegt')
        check(all(s['ch']==2 and s['screen']==1 and all(x[0] and x[1] for x in s['sp']) for s in sc),f'[{lang}/{tid}] je Szene Bildschirm + 2 Figuren mit Text in beiden Sprachen')
        check(all(s['sp'][1][2]>s['sp'][0][2]+1 for s in sc),f'[{lang}/{tid}] Sprecher nacheinander')
        check(all(6<=s['d']<=40 for s in sc),f'[{lang}/{tid}] Szenenlängen plausibel {[s["d"] for s in sc]}')
        check(all(s['cur']>=0 and s['clk']>=0 for s in sc) and sum(s['clk'] for s in sc)>=4,f'[{lang}/{tid}] Klick-Markierungen vorhanden')
        # Textlängen: nichts läuft aus der Bühne
        for i in range(n):
            a.ev(f"selectScene({n0+i}); refreshAll()"); pg.wait_for_timeout(250)
            a.ev("document.querySelectorAll('.stage-object').forEach(e=>e.style.animation='none')")
            if lang=='de': pg.locator('#stage').screenshot(path=f'out/flow_{tid}_{i+1}.png')
        # Auswahl der kompletten Vorlage spielen: erste Szene kurz abspielen
        a.ev(f"selectScene({n0})"); pg.click('.fs-play >> nth=%d'%n0 if False else '#playAllBtn'); pg.wait_for_timeout(1500); a.ev("Player.stop()")
        # EN: Oberflächentexte im Bildschirm
        if lang=='en':
            svg=a.ev("iconLibrary.find(i=>i.id==='ui-ad-goal').svg"); check('Goal' in svg and 'Ziel' not in svg,f'[en/{tid}] Bildschirm-Texte englisch')
        check(not a.errs,f'[{lang}/{tid}] keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
