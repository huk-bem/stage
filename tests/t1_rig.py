import sys, json
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)
with App(path) as a:
    # 1. Haken pro Figur und Ansicht
    res=a.ev("""()=>{
      const out=[]; const host=document.createElement('div'); host.style.cssText='position:absolute;left:-9999px;width:200px;height:340px'; document.body.appendChild(host);
      for(const ch of characters) for(const f of ['front','threeq','side','back']){
        host.innerHTML='<div class="stage-character pose-idle" data-inst-id="x" style="width:200px;height:340px;position:absolute">'+characterSVG(ch,'t'+ch.id+f,f)+'</div>';
        const q=s=>host.querySelectorAll(s).length;
        out.push({id:ch.id,f,torso:q('.torso'),head:q('.head-group'),armM:q('.arm-main'),armO:q('.arm-off'),legM:q('.leg-main'),legO:q('.leg-off'),
          vm:q('.vm'), mouth:q('.mouth'), brows:q('.brow-left')+q('.brow-right'), eyes:q('.eye-g')});
      } host.remove(); return out; }""")
    bad=[r for r in res if not(r['torso']==1 and r['head']==1 and r['armM']==1 and r['armO']==1 and r['legM']==1 and r['legO']==1)]
    check(len(res)==80 and not bad, f'Rig-Haken (Torso/Kopf/Arme/Beine) bei {len(res)} Figur×Ansicht-Kombinationen vollständig'+(' '+str(bad[:3]) if bad else ''))
    badm=[r for r in res if r['f']!='back' and r['vm']!=11]
    check(not badm, 'alle 11 Mundformen in Front/¾/Seite vorhanden'+(' '+str(badm[:3]) if badm else ''))
    backm=[r for r in res if r['f']=='back' and r['vm']!=0]
    check(not backm,'Rückansicht hat (richtig) keinen Mund')
    # 2. Visemen: genau eine sichtbar
    vis=a.ev("""()=>{
      const V=['rest','joy','anger','surprise','mm','a','e','i','o','u','fv']; const out=[];
      const ch=characters[0];
      for(const f of ['front','threeq','side']){
        const host=document.getElementById('stageCharacters'); host.innerHTML='<div class="stage-character" data-inst-id="zz" style="position:absolute;width:200px;height:340px">'+characterSVG(ch,'v'+f,f)+'</div>';
        const el=host.firstChild;
        for(const v of V){ el.dataset.v=v; const shown=[...el.querySelectorAll('.vm')].filter(g=>getComputedStyle(g).display!=='none').map(g=>g.getAttribute('class').replace('vm vm-',''));
          out.push({f,v,shown}); }
      } return out; }""")
    badv=[x for x in vis if x['shown']!=[x['v']]]
    check(not badv,'je data-v genau eine Mundform sichtbar (33 Fälle)'+(' '+str(badv[:3]) if badv else ''))
    # 3. Posen laufen (Animation oder Transform aktiv) je Ansicht
    pose=a.ev("""()=>{
      const out=[]; const ch=characters[2]; const host=document.getElementById('stageCharacters');
      const poses=['idle','walk','point','wave','explain','cheer'];
      for(const f of ['front','threeq','side','back']) for(const p of poses){
        host.innerHTML='<div class="stage-character pose-'+p+' mood-none" data-inst-id="zz" style="position:absolute;width:200px;height:340px">'+characterSVG(ch,'p'+f+p,f)+'</div>';
        const el=host.firstChild, g=s=>el.querySelector(s), cs=n=>getComputedStyle(n);
        const info=n=>({an:cs(n).animationName, tf:cs(n).transform});
        out.push({f,p,armM:info(g('.arm-main')),armO:info(g('.arm-off')),legM:info(g('.leg-main')),legO:info(g('.leg-off')),torso:info(g('.torso'))});
      } return out; }""")
    def active(i): return i['an']!='none' or i['tf'] not in('none','matrix(1, 0, 0, 1, 0, 0)')
    for r in pose:
        if r['p']=='walk': ok=active(r['legM']) and active(r['legO']) and active(r['armM'])
        elif r['p'] in('point',): ok=active(r['armM'])
        elif r['p'] in('wave','cheer','explain'): ok=active(r['armM'])
        else: ok=not active(r['legM']) and r['armM']['an'] in ('none','armIdleA')   # Ruhe: nur dezentes Mitschwingen der Arme
        if not ok: fails.append('pose '+str(r)); print('FAIL pose',r['f'],r['p'],r['armM'],r['legM'])
    print('PASS Posen-Matrix 4 Ansichten x 6 Posen' if not [f for f in fails if f.startswith('pose')] else 'FAIL Posen-Matrix')
    # 4. Stimmungen wirken auf Kopf
    mood=a.ev("""()=>{
      const out={}; const ch=characters[0]; const host=document.getElementById('stageCharacters');
      for(const m of ['none','joy','anger','surprise','news','listening']){
        host.innerHTML='<div class="stage-character mood-'+m+'" data-inst-id="zz" style="position:absolute;width:200px;height:340px">'+characterSVG(ch,'m'+m,'front')+'</div>';
        const h=host.firstChild.querySelector('.head-group'), b=host.firstChild.querySelector('.brow-left'); const cs=getComputedStyle(h), cb=getComputedStyle(b);
        out[m]={rotate:cs.rotate,translate:cs.translate,scale:cs.scale,browT:cb.translate,browR:cb.rotate};
      } return out; }""")
    check(mood['none']['translate'] in('none','0px') and mood['joy']['translate']!=mood['none']['translate'] and mood['anger']['rotate']!='none' and mood['surprise']['scale']!='none' and mood['listening']['rotate']!='none','Stimmungen verändern Kopf/Brauen (Reaktionen sichtbar)')
    print(json.dumps(mood)[:400])
    check(not a.errs,'keine Konsolenfehler '+str(a.errs[:3]))
print('FAILS:',fails)
