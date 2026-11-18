import sys, json, time
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)
OBS="""()=>{ window.__c=[]; window.__t0=null;
  new MutationObserver(ms=>{ ms.forEach(m=>{ if(m.attributeName==='class'&&m.target.classList.contains('stage-character')){ const c=[...m.target.classList].filter(x=>/^(pose|mood)-|^talking$/.test(x)).join(' '); const last=__c.filter(x=>x.id===m.target.dataset.instId).pop(); if(!last||last.c!==c) __c.push({id:m.target.dataset.instId,c,t:performance.now()}); } }); })
   .observe(document.getElementById('stageCharacters'),{subtree:true,attributes:true,attributeFilter:['class']});
  window.__b=[]; new MutationObserver(ms=>{ ms.forEach(m=>m.addedNodes.forEach(n=>{ if(n.classList&&n.classList.contains('bubble')) __b.push({id:n.dataset.instId,txt:n.textContent,t:performance.now()}); })); }).observe(document.getElementById('stageBubbles'),{childList:true});
}"""
with App(path) as a:
    pg=a.pg
    a.ev("window.__v.length=0")
    a.ev(OBS)
    ids=a.ev("scenesTimeline[0].characters.map(c=>c.id)"); L,M=ids
    t_click=a.ev("(()=>{ window.__tclick=performance.now(); document.getElementById('previewSceneBtn').click(); return window.__tclick; })()")
    # Zwischenmessung: Musik & Cursor
    pg.wait_for_timeout(2500)
    rms=a.ev("Music.rms()"); mname=a.ev("Music.name")
    cur=a.ev("[...document.querySelectorAll('.tl-cursor')].filter(c=>c.style.display==='block').length")
    playing=a.ev("document.body.classList.contains('playing')")
    check(playing,'Wiedergabe-Modus aktiv (Bearbeiten gesperrt)')
    check(cur>3,f'Abspiel-Cursor läuft in den Timeline-Zeilen ({cur} Spuren)')
    bub=a.ev("[...document.querySelectorAll('.bubble')].map(b=>({id:b.dataset.instId,on:b.classList.contains('on'),w:b.querySelectorAll('.w.done').length,cur:b.querySelectorAll('.w.cur').length,tot:b.querySelectorAll('.w').length}))")
    check(len(bub)==1 and bub[0]['id']==L and bub[0]['on'] and bub[0]['w']>=1,f'Sprechblase Lena sichtbar, Wörter laufen mit {bub}')
    pg.screenshot(path=OUT+'/shot_play_lena.png')
    # warten bis Szene fertig
    pg.wait_for_function("!Player.running",timeout=30000)
    total=(time.time())
    sp=a.ev("__sp.log"); cl=a.ev("__c"); vs=a.ev("__v"); bubs=a.ev("__b")
    starts=[x for x in sp if x['ev']=='start']; ends=[x for x in sp if x['ev']=='end']
    check(len(starts)==2 and len(ends)==2,f'beide Sprechzeilen gesprochen ({len(starts)} Start, {len(ends)} Ende)')
    check(a.ev("__sp.maxActive")==1,'nie zwei Stimmen gleichzeitig (Browser-Limit sauber über Warteschlange)')
    check(starts[0]['text'].startswith('Guten Tag') and starts[1]['text'].startswith('Danke'),'Reihenfolge Lena → Markus')
    tl0=(starts[0]['t']-t_click)/1000; tm0=(starts[1]['t']-t_click)/1000
    sm=a.ev("scenesTimeline[0].characters[1].speechStart")
    check(0.5<tl0<1.2,f'Lena beginnt bei ca. {tl0:.2f} s (geplant 0,6 s)')
    check(abs(tm0-sm)<0.6 or tm0>sm,f'Markus beginnt bei {tm0:.2f} s (geplant {sm} s)')
    check(starts[0]['voice']!=starts[1]['voice'] and starts[0]['voice'] and starts[1]['voice'],f"unterschiedliche Stimmen automatisch gewählt: {starts[0]['voice']} / {starts[1]['voice']}")
    check('Katja' in (starts[0]['voice'] or '') and 'Conrad' in (starts[1]['voice'] or ''),'Stimme passt zum Figurengeschlecht (Lena=weiblich, Markus=männlich)')
    check(starts[0]['pitch']>1 and starts[1]['pitch']<1,'Tonhöhe je Figur unterschiedlich')
    # Posen / Stimmungen
    lc=[x for x in cl if x['id']==L]; mc=[x for x in cl if x['id']==M]
    wave=[x for x in lc if 'pose-wave' in x['c']]
    check(bool(wave) and 0.1<(wave[0]['t']-t_click)/1000<0.9,'Lena winkt ab ~0,2 s (Pose-Clip)')
    after_wave=[x for x in lc if 'pose-idle' in x['c'] and wave and x['t']>wave[0]['t']]
    check(bool(after_wave) and 1.4<(after_wave[0]['t']-wave[0]['t'])/1000<2.6,'Winken endet nach ~1,8 s')
    joy=[x for x in lc if 'mood-joy' in x['c']]
    check(bool(joy) and abs(joy[0]['t']-starts[0]['t'])<250,'Lenas Reaktion „Freude“ startet exakt mit Sprechbeginn')
    check(any('talking' in x['c'] for x in lc),'Lena „talking“ (Nicken/Gestik) während des Sprechens')
    lis=[x for x in mc if 'mood-listening' in x['c']]
    check(bool(lis) and 0.3<(lis[0]['t']-t_click)/1000<1.2,'Markus hört ab 0,6 s zu (feste Zeit auf der Timeline)')
    mj=[x for x in mc if 'talking' in x['c']]
    check(bool(mj) and abs(mj[0]['t']-starts[1]['t'])<250,'Markus „talking“ beginnt mit seiner Stimme')
    # Lippen
    lv=[x for x in vs if x['id']==L]; mv=[x for x in vs if x['id']==M]
    seqL=[x['v'] for x in lv]
    spoken_L=[x for x in lv if starts[0]['t']-50<=x['t']<=ends[0]['t']+50]
    kinds=set(x['v'] for x in spoken_L)
    check(len(spoken_L)>25 and len(kinds-{'joy','rest'})>=5,f'Lenas Mund wechselt {len(spoken_L)}× zwischen {sorted(kinds)}')
    # Lippen vs. Zeit: Mund darf nach Ende nicht weiter sprechen
    late=[x for x in lv if x['t']>ends[0]['t']+400 and x['v'] in('a','e','i','o','u','mm','fv')]
    check(not late,'Mund schließt nach Sprechende (keine Nachläufer)')
    # Wortsynchronität: Wort-Beginn laut Boundary ≈ Vokalwechsel; prüfe dass 'mm' beim m-Wort auftritt: 'Konto' hat k-o-n-t-o -> o/u; 'Möchte'
    check(len([x for x in mv if x['v']!='rest'])>10,'Markus’ Lippen bewegen sich')
    check(len(bubs)==2 and bubs[0]['id']==L and bubs[1]['id']==M,'Sprechblasen erscheinen für beide Sprecher nacheinander')
    # nach Ende: sauberer Zustand
    check(a.ev("document.body.classList.contains('playing')")==False,'Wiedergabe-Modus beendet')
    check(a.ev("document.querySelectorAll('.bubble').length")==0,'Sprechblasen entfernt')
    st=a.ev("scenesTimeline[0].characters.map(c=>{const e=charEl(c.id);return [e.className.includes('talking'),e.dataset.v]})")
    check(all(not s[0] for s in st),'Figuren nach Wiedergabe im Ruhezustand '+str(st))
    cal=a.ev("Calib")
    check(len(cal)>=1,'Stimmen-Kalibrierung gespeichert '+json.dumps(cal))
    print('rms Musik während Szene:',rms,'Preset',mname)
    check(not a.errs,'keine Konsolenfehler '+str(a.errs[:3]))
print('FAILS:',fails)
