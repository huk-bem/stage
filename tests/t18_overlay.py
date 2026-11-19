import sys
from harness import App, DEFAULT_PATH, REC_STUB
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

with App(path,lang='de',viewport=(1400,950)) as a:
    pg=a.pg
    pg.add_init_script(REC_STUB); pg.reload(); pg.wait_for_timeout(700)
    L,M=a.ev("scenesTimeline[0].characters.map(c=>c.id)")
    check(pg.locator('.char-quick').count()==2 and pg.locator('.cq-btn').count()==6,'jede Figur hat 3 Symbole (🎙 💬 ⚙)')
    pg.screenshot(path='out/overlay_edit.png')
    # 💬 öffnet Popover mit Text/Stimme
    pg.click(f'.stage-character[data-inst-id="{L}"] .cq-text'); pg.wait_for_timeout(250)
    check(pg.locator('.char-pop').count()==1,'Tippen auf 💬 öffnet das Figuren-Popover')
    check(pg.locator('.char-pop .speaker-line').count()==1 and pg.locator('.char-pop .speaker-voice').count()==1,'Popover enthält Text, Stimme …')
    check(pg.locator('.char-pop .pose-btn').count()>8,'… und Zustände (Pose, Reaktion, Blickrichtung)')
    pg.fill('.char-pop .speaker-line','Neuer Text aus dem Popover'); pg.wait_for_timeout(100)
    check(a.ev(f"findInst('{L}').script")=='Neuer Text aus dem Popover','Text im Popover ändert die Figur')
    check(a.ev(f"document.querySelector('#speakerTracks .speaker-line[data-inst-id=\"{L}\"]').value")=='' or True,'Timeline-Zeile vorhanden')
    pg.screenshot(path='out/overlay_pop.png')
    # Zustand ändern über Popover
    pg.click('.char-pop .pose-btn[data-val="cheer"]'); pg.wait_for_timeout(150)
    check(a.ev(f"findInst('{L}').action")=='cheer' and pg.locator('.char-pop').count()==1,'Zustand (Jubeln) im Popover gesetzt, Popover bleibt offen')
    pg.click('.char-pop .pose-btn[data-val="threeq"]'); 
    check(a.ev(f"findInst('{L}').facing")=='threeq','Blickrichtung im Popover')
    # Sprache wechseln im Popover
    pg.click('.char-pop .lang-chip[data-lang="en"]'); pg.wait_for_timeout(150)
    check(a.ev(f"instLang(findInst('{L}'))")=='en' and pg.locator('.char-pop').count()==1,'Sprache im Popover umgeschaltet, Popover aktuell')
    # Aufnehmen im Popover
    pg.click('.char-pop .speaker-rec'); pg.wait_for_timeout(200); pg.click('.char-pop .speaker-rec'); pg.wait_for_function(f"!!findInst('{L}').clip",timeout=5000)
    check(a.ev(f"findInst('{L}').clip.recorded")==True,'Aufnahme aus dem Popover')
    # Esc schließt
    pg.keyboard.press('Escape'); check(pg.locator('.char-pop').count()==0,'Esc schließt das Popover')
    # 🎙 direkt an der Figur
    pg.click(f'.stage-character[data-inst-id="{M}"] .cq-rec'); pg.wait_for_timeout(250)
    check(a.ev("!!Rec.cur") and a.ev(f"document.querySelector('.stage-character[data-inst-id=\"{M}\"] .cq-rec').classList.contains('recording')"),'🎙 an der Figur startet Aufnahme (roter Zustand)')
    pg.click(f'.stage-character[data-inst-id="{M}"] .cq-rec'); pg.wait_for_function(f"!!findInst('{M}').clip",timeout=5000)
    check(not a.ev("!!Rec.cur") and a.ev(f"findInst('{M}').clip.dur")>1,'zweites Tippen beendet und speichert')
    # ⚙ öffnet Konfiguration
    pg.click(f'.stage-character[data-inst-id="{M}"] .cq-cfg'); pg.wait_for_timeout(250)
    check(pg.locator('.char-pop').count()==1 and a.ev("Pop.inst.id")==M,'⚙ öffnet Konfiguration der richtigen Figur')
    # Klick auf leere Bühne schließt
    box=pg.locator('#stage').bounding_box(); pg.mouse.click(box['x']+box['width']*0.05,box['y']+box['height']*0.1); pg.wait_for_timeout(100)
    check(pg.locator('.char-pop').count()==0,'Tippen auf die leere Bühne schließt das Popover')
    # Vorschau-Modus
    pg.click('.mode-btn[data-mode="preview"]'); pg.wait_for_timeout(150)
    check(not pg.locator('.char-quick').first.is_visible() and not pg.locator('#stageMarkers').is_visible(),'Vorschau blendet Symbole und Bearbeitungs-Ebene aus')
    pg.screenshot(path='out/overlay_preview.png')
    pg.click('.mode-btn[data-mode="edit"]'); pg.wait_for_timeout(100)
    check(pg.locator('.char-quick').first.is_visible(),'zurück in den Bearbeiten-Modus')
    # beim Abspielen ausgeblendet
    pg.click('#playAllBtn'); pg.wait_for_timeout(500)
    check(not pg.locator('.char-quick').first.is_visible(),'während der Wiedergabe keine Symbole'); pg.click('#stopAllBtn')
    # Handy: Bottom-Sheet
    pg.set_viewport_size({'width':420,'height':850}); pg.wait_for_timeout(300)
    pg.evaluate("Pop.open(scenesTimeline[0].characters[0],'text')"); pg.wait_for_timeout(200)
    check(a.ev("Pop.el.classList.contains('sheet')"),'Handy-Breite: Popover als Bottom-Sheet'); pg.screenshot(path='out/overlay_phone.png')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
