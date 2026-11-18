import sys, json
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)
for boundaries in (True,False):
  with App(path) as a:
    pg=a.pg
    a.ev(f"__sp.boundaries={'true' if boundaries else 'false'}; __sp.speed=70")
    text='Mama Opa Mia fuhr Auto. Wo bist du?'
    a.ev("scenesTimeline[0].characters[1].script=''; scenesTimeline[0].characters[0].script=%s; scenesTimeline[0].characters[0].reaction='none'; renderSpeakerTracks(); renderObjectTimeline();"%json.dumps(text))
    if not boundaries:
        # einmal kalibrieren, dann messen
        a.ev("Player.startLine(scenesTimeline[0].characters[0])"); pg.wait_for_function("!Player.running",timeout=30000); a.ev("__v.length=0; __sp.log.length=0")
    L=a.ev("scenesTimeline[0].characters[0].id")
    a.ev("Player.startLine(scenesTimeline[0].characters[0])"); pg.wait_for_function("!Player.running",timeout=30000)
    sp=a.ev("__sp.log"); st=[x for x in sp if x['ev']=='start'][-1]['t']; en=[x for x in sp if x['ev']=='end'][-1]['t']
    vs=[x for x in a.ev("__v") if x['id']==L and x['t']>=st-5]
    import re
    words=[(m.group(),m.start()) for m in re.finditer(r'\S+',text)]
    ms=70
    res=[]
    for w,i in words:
        t0=st+i*ms; t1=t0+(len(w))*ms     # Wortfenster laut Engine
        seg=[x['v'] for x in vs if t0-15<=x['t']<t1+15]
        res.append((w,seg))
    print(('mit' if boundaries else 'ohne')+' Wortgrenzen:',res)
    expect={'Mama':{'mm','a'},'Opa':{'o','mm','a'},'Mia':{'mm','i','a'},'fuhr':{'fv','u'},'Auto.':{'a','u','e','o'},'Wo':{'fv','o'},'bist':{'mm','i'},'du?':{'u'}}
    ok=0
    for w,seg in res:
        e=expect[w]
        if e<=set(seg) or len(e&set(seg))>=max(1,len(e)-1): ok+=1
        else: print('   Abweichung bei',w,seg,'erwartet',e)
    check(ok>=len(res)-1 if boundaries else ok>=len(res)-3,f"{'mit' if boundaries else 'ohne'} Wortgrenzen: {ok}/{len(res)} Wörter zeigen die passenden Mundformen im richtigen Zeitfenster")
    check(not a.errs,'keine Konsolenfehler')
print('FAILS:',fails)
