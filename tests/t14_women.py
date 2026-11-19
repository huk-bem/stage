import sys, io
from harness import App, DEFAULT_PATH, OUT
from PIL import Image
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)
def hexrgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def close(a,b,t=18): return all(abs(x-y)<=t for x,y in zip(a,b))
with App(path,viewport=(900,700)) as a:
    pg=a.pg
    fem=a.ev("characters.filter(c=>c.female).map(c=>[c.id,c.hair,c.skin,c.hairStyle])")
    check(len(fem)>=9,f'{len(fem)} Frauenfiguren')
    a.ev("""()=>{ Player.stop(); const ov=document.createElement('div'); ov.id='qa'; ov.style.cssText='position:fixed;left:0;top:0;width:900px;height:700px;background:#fff;z-index:9999'; document.body.appendChild(ov); 0 }""")
    for id_,hair,skin,style in fem:
        for look in ['std','toon']:
            a.ev("""([id,look])=>{ const ov=document.getElementById('qa'); ov.innerHTML='<div class="stage-character pose-idle mood-none" id="qa1" style="position:absolute;left:100px;top:100px;width:400px;height:680px">'+characterSVG(characters.find(c=>c.id===id),'qq','front',{look:look})+'</div>'; 0 }""",[id_,look]) if False else a.pg.evaluate("""([id,look])=>{ const ov=document.getElementById('qa'); ov.innerHTML='<div class="stage-character pose-idle mood-none" id="qa1" style="position:absolute;left:100px;top:10px;width:400px;height:680px">'+characterSVG(characters.find(c=>c.id===id),'qq','front',{look:look})+'</div>'; return 0 }""",[id_,look])
            pg.wait_for_timeout(120)
            png=pg.screenshot(clip={'x':100,'y':10,'width':400,'height':680})
            im=Image.open(io.BytesIO(png)).convert('RGB')
            # SVG-Koordinate (x,y) → Pixel: 2 px je Einheit (400×680 für 200×340); Look 'toon' skaliert den Kopf (Hals bleibt)
            hc=hexrgb(hair)
            # Hals/Brust unter dem Kinn, mittig: nicht Haarfarbe
            ok=True; who=[]
            for y in ((96,106) if look=='std' else (100,108)):
                px=im.getpixel((200,int(y*2)))
                if close(px,hc,14) and hair.lower() not in ('#d9d9d9',): ok=False; who.append((y,px))
            check(ok,f'{id_} ({style}, {look}): Haar verdeckt Hals/Brust nicht {who}')
    # Ohren: bei Bob/Wellig/Lang keine, sonst klein
    r=a.ev("""()=>characters.filter(c=>c.female).map(c=>{ const s=characterSVG(c,'e'+c.id,'front'); const ears=(s.match(/<ellipse cx="[0-9.]+" cy="57" rx="4.1" ry="6.2"/g)||[]).length; return [c.hairStyle,ears]; })""")
    check(all((e==0) if st in ('bob','wavy','long') else (e==2) for st,e in r),'Ohren: verdeckt bei langem Haar, sonst klein (2) '+str(r))
    # keine Hörner: keine spitzen Haarkappen-Enden mehr (alte Kappe)
    s=a.ev("hairFront('bob','#664422').front+hairFront('ponytail','#664422').front")
    check('M72 54 C66 25' not in s,'alte spitze Haarkappe entfernt')
    # Körper: Frauen schmaler in den Schultern
    r=a.ev("(()=>{ const f=characters.find(c=>c.female&&c.build==='slim'), m=characters.find(c=>!c.female&&c.build==='slim'); return [buildOf(f).sw, buildOf(m).sw, buildOf(f).ww<buildOf(f).hw]; })()")
    check(r[0]<r[1] and r[2],'Frauen: schmalere Schultern, Taille '+str(r))
    # alle Figuren/Ansichten/Looks ohne NaN
    bad=a.ev("""()=>{ const b=[]; for(const ch of characters) for(const f of ['front','threeq','side','back']) for(const l of ['std','ink','toon','chibi']){ const s=characterSVG(ch,'z'+ch.id+f+l,f,{look:l}); if(/NaN|undefined/.test(s)) b.push(ch.id+f+l); } return b; }""")
    check(not bad,'keine NaN in allen Ansichten/Looks '+str(bad))
    check(len(a.errs)==0,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
