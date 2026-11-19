import sys
from harness import App, DEFAULT_PATH
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

with App(path,lang='de',viewport=(1400,950)) as a:
    pg=a.pg; msgs=[]; mode={'accept':True}
    pg.on('dialog',lambda d:(msgs.append(d.message),d.accept() if mode['accept'] else d.dismiss()))
    check(pg.locator('.filmstrip-card').count()==1 and pg.locator('.fs-btn').count()==4,'Szene hat 4 Symbole: leer davor, kopieren, leer danach, löschen')
    check(a.ev("document.querySelector('.fs-del').disabled"),'Löschen bei der einzigen Szene gesperrt')
    # leere Szene danach
    pg.click('.filmstrip-card >> nth=0 >> .fs-after'); pg.wait_for_timeout(150)
    sc=a.ev("({n:scenesTimeline.length,cur:currentSceneIndex,c:getCurrentScene().characters.length,o:getCurrentScene().objects.length,bg:getCurrentScene().bgType+':'+getCurrentScene().bgId})")
    check(sc['n']==2 and sc['cur']==1 and sc['c']==0 and sc['o']==0 and sc['bg']=='plain:studio-light',f'leere neutrale Szene danach eingefügt und angewählt {sc}')
    # leere Szene davor (vor Szene 1)
    pg.click('.filmstrip-card >> nth=0 >> .fs-before'); pg.wait_for_timeout(150)
    check(a.ev("scenesTimeline.length")==3 and a.ev("currentSceneIndex")==0 and a.ev("scenesTimeline[1].characters.length")==2 and a.ev("getCurrentScene().characters.length")==0,'leere Szene vor der ersten, Demo-Szene rutscht auf Platz 2')
    # kopieren der Demo-Szene (Platz 2)
    pg.click('.filmstrip-card >> nth=1 >> .fs-copy'); pg.wait_for_timeout(200)
    check(a.ev("scenesTimeline.length")==4 and a.ev("currentSceneIndex")==2 and a.ev("getCurrentScene().characters.length")==2,'Kopie direkt hinter dem Original, mit Figuren')
    check(a.ev("scenesTimeline[2].characters[0].script")==a.ev("scenesTimeline[1].characters[0].script"),'Texte mitkopiert')
    # löschen mit Rückfrage (Szene hat Inhalt)
    pg.click('.filmstrip-card >> nth=2 >> .fs-del'); pg.wait_for_timeout(200)
    check(a.ev("scenesTimeline.length")==3 and any('löschen' in m for m in msgs),'Löschen mit Rückfrage bei Inhalt')
    # leere Szene löschen ohne Rückfrage
    msgs.clear(); pg.click('.filmstrip-card >> nth=0 >> .fs-del'); pg.wait_for_timeout(150)
    check(a.ev("scenesTimeline.length")==2 and not msgs,'leere Szene wird ohne Rückfrage gelöscht')
    # Rückfrage abbrechen
    mode['accept']=False
    pg.click('.filmstrip-card >> nth=0 >> .fs-del'); pg.wait_for_timeout(150)
    mode['accept']=True
    check(a.ev("scenesTimeline.length")==2,'Abbrechen behält die Szene')
    # „+“ am Ende = leere Szene
    pg.click('.filmstrip-add'); pg.wait_for_timeout(150)
    check(a.ev("scenesTimeline.length")==3 and a.ev("currentSceneIndex")==2 and a.ev("getCurrentScene().characters.length")==0,'„+“ am Ende hängt eine leere Szene an')
    # Rückgängig stellt gelöschte Szene wieder her
    a.ev("History.commit()"); pg.click('.filmstrip-card >> nth=0 >> .fs-del'); pg.wait_for_timeout(200); a.ev("History.commit()"); pg.wait_for_timeout(100)
    n=a.ev("scenesTimeline.length"); pg.click('#undoBtn'); pg.wait_for_timeout(300)
    check(a.ev("scenesTimeline.length")==n+1,'Rückgängig bringt die gelöschte Szene zurück')
    # Handy: Symbole erreichbar
    pg.screenshot(path='out/scenes_icons.png',clip={'x':0,'y':560,'width':1400,'height':390})
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
