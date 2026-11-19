import sys
from harness import App, DEFAULT_PATH
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

with App(path,lang='de',viewport=(1400,950)) as a:
    pg=a.pg
    pg.click('.rail-btn[data-tab="scenes"]'); pg.wait_for_timeout(200)
    check(pg.locator('.pal-card').count()==10,'10 Farbpaletten im Szenen-Tab')
    check(a.ev("document.querySelectorAll('.bg-card').length")==8,'Palettenfarben erscheinen nicht in der Liste der einfachen Hintergründe')
    # Demo-Szene: Textobjekt + Blasen
    a.ev("addObjectToStage({type:'text',content:'Titel',color:'#ffffff',w:300,h:60,x:40,y:20}); refreshAll()")
    pg.click('.pal-p6 .pal-apply'); pg.wait_for_timeout(300)
    r=a.ev("(()=>{ const s=getCurrentScene(), t=s.objects.find(o=>o.type==='text'), c=s.characters[0]; return {bg:s.bgId,tc:t.color,fill:c.bs.fill,ink:c.bs.color,bgEl:document.getElementById('stageBg')?document.getElementById('stageBg').style.background:'' , cr:[contrastOf(mixHex('#343841','#F3E5C0',.5),t.color),contrastOf(c.bs.fill,c.bs.color)]}; })()")
    check(r['bg']=='pg-343841-F3E5C0','Hintergrund = Verlauf aus Farbe 1→2 '+r['bg'])
    check(r['fill']=='#DCC2B1' and r['cr'][1]>=7,'Sprechblasen: hellste Paletten-Farbe, Schrift gut lesbar (Kontrast %.1f)'%r['cr'][1])
    check(r['cr'][0]>=4.5,'Text auf dem Hintergrund lesbar (Kontrast %.1f)'%r['cr'][0])
    check('linear-gradient' in a.ev("document.querySelector('.filmstrip-thumb').style.background"),'Filmstreifen zeigt den neuen Hintergrund')
    pg.screenshot(path='out/palette_p6.png')
    # einzelne Farbe
    pg.click('.pal-p2 .pal-sw >> nth=1'); pg.wait_for_timeout(200)
    check(a.ev("getCurrentScene().bgId")=='pc-64C0D7','Klick auf eine Farbe setzt nur den Hintergrund')
    # alle Szenen
    a.ev("duplicateScene(0); selectScene(0)"); pg.wait_for_timeout(200)
    pg.check('.pal-opt-all'); pg.click('.pal-p8 .pal-apply'); pg.wait_for_timeout(300)
    check(a.ev("scenesTimeline.every(s=>s.bgId==='pg-74D1D6-F2EF6E')"),'„alle Szenen“ wendet die Palette überall an')
    # nur Hintergrund
    pg.uncheck('.pal-opt-text'); pg.uncheck('.pal-opt-bubble'); a.ev("getCurrentScene().objects.find(o=>o.type==='text').color='#123456'"); pg.click('.pal-p3 .pal-apply'); pg.wait_for_timeout(200)
    check(a.ev("getCurrentScene().objects.find(o=>o.type==='text').color")=='#123456','ohne Haken bleiben Texte unverändert')
    # Projekt speichern/laden
    r=a.ev("(async()=>{ const o=await Project.serialize(false); Project.load(o.text); return [scenesTimeline[0].bgId, !!bgById(scenesTimeline[0].bgId), document.getElementById('stageBg')?1:0]; })()")
    check(r[0]=='pg-F0D457-AED651' and r[1],'Projekt speichern/laden behält die Palettenfarbe')
    # Rückgängig
    a.ev("History.commit()"); b=a.ev("getCurrentScene().bgId"); pg.click('.pal-p9 .pal-apply'); pg.wait_for_timeout(200); pg.click('#undoBtn'); pg.wait_for_timeout(300)
    check(a.ev("getCurrentScene().bgId")==b,'Rückgängig stellt die vorige Palette wieder her')
    # EN
check(True,'')
with App(path,lang='en',viewport=(1400,950)) as a:
    a.pg.click('.rail-btn[data-tab="scenes"]'); a.pg.wait_for_timeout(200)
    check('colour palettes' in a.ev("document.getElementById('panelBody')?document.getElementById('panelBody').innerText:document.body.innerText").lower() ,'EN: Überschrift „Colour palettes“')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
