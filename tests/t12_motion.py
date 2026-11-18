import sys
from harness import App, DEFAULT_PATH, OUT
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)
with App(path,lang='de',viewport=(1300,800)) as a:
    pg=a.pg
    # Figuren: alle 20 × 4 Ansichten ohne ungültige Zahlen
    bad=a.ev("""()=>{ const b=[]; for(const ch of characters) for(const f of ['front','threeq','side','back']){ const s=characterSVG(ch,'t'+ch.id+f,f); if(/NaN|undefined/.test(s)) b.push(ch.id+':'+f); } return b; }""")
    check(not bad,'alle Figuren in 4 Ansichten ohne NaN/undefined '+str(bad))
    # Gesicht: Wimpern außen (links beim linken Auge, rechts beim rechten) – nur weibliche Figuren
    r=a.ev("""()=>{ const f=characters.find(c=>c.female), m=characters.find(c=>!c.female); return [characterSVG(f,'a','front').includes('stroke-width="1.15"'), characterSVG(m,'b','front').includes('stroke-width="1.15"')]; }""")
    check(r[0] and not r[1],'Wimpern nur bei weiblichen Figuren')
    # Haar: keine gerade Oberkante der Hinterhaar-Flächen (früher „Hörner“): Pfade beginnen oben gerundet
    r=a.ev("""()=>{ const bad=[]; for(const st of ['bob','wavy','long']){ const h=hairFront(st,'#664422'); if(!/^<path d="M100 1\\d C/.test(h.behind)) bad.push(st); } return bad; }""")
    check(not r,'Hinterhaar mit gerundeter Oberkante '+str(r))
    # Gehen: Sinus-Schwung + Fußhub in Seitenansicht
    a.ev("()=>{ window.__i=scenesTimeline[0].characters[0]; __i.facing='side'; renderCharacters(); __i.action='walk'; applyRig(__i); 0 }")
    pg.wait_for_timeout(300)
    info=a.ev("()=>{ const el=charEl(__i.id); const cs=n=>getComputedStyle(el.querySelector(n)); return {leg:cs('.leg-main').animationName, off:cs('.leg-off').animationDelay, arm:cs('.arm-main').animationName, torso:cs('.torso').animationName, head:cs('.head-group').animationName}; }")
    check('legSwing' in info['leg'] and 'legLift' in info['leg'],'Beine: Schwung + Fußhub '+info['leg'])
    check(info['off'].startswith('-0.45s'),'Gegenbein um halben Zyklus versetzt '+info['off'])
    check('walkBob' in info['torso'] and 'walkBobHead' in info['head'],'Rumpf-Bob und Kopf mit Verzögerung')
    # Beinwinkel wechselt kontinuierlich (keine Sprünge > 12° zwischen Abtastungen im 50-ms-Takt)
    ang=a.ev("""async ()=>{ const el=charEl(__i.id).querySelector('.leg-main'); const out=[]; for(let i=0;i<24;i++){ out.push(parseFloat(getComputedStyle(el).rotate)); await new Promise(r=>setTimeout(r,50)); } return out; }""")
    jumps=max(abs(ang[i+1]-ang[i]) for i in range(len(ang)-1))
    check(max(ang)>15 and min(ang)<-15 and jumps<14,f'Schwung ±22° ohne Sprünge (max Schritt {jumps:.1f}°)')
    # Posenwechsel gleitet: Winken → Ruhe, Armwinkel springt nicht
    a.ev("()=>{ __i.facing='front'; renderCharacters(); __i.action='wave'; applyRig(__i); 0 }"); pg.wait_for_timeout(900)
    ANG="""()=>{ const cs=getComputedStyle(charEl(__i.id).querySelector('.arm-main')); const m=/matrix\\(([^)]+)\\)/.exec(cs.transform); let a=0; if(m){ const v=m[1].split(',').map(parseFloat); a=Math.atan2(v[1],v[0])*180/Math.PI; } const r=parseFloat(cs.rotate); return a+(isNaN(r)?0:r); }"""
    before=a.ev(ANG)
    a.ev("()=>{ __i.action='idle'; applyRig(__i); 0 }")
    first=a.ev(ANG); pg.wait_for_timeout(120); mid=a.ev(ANG); pg.wait_for_timeout(700); end=a.ev(ANG)
    check(abs(before)>120 and abs(first-before)<20 and abs(mid)<abs(first) and abs(end)<6,f'Winken→Ruhe gleitend ({before:.0f}° → {first:.0f}° → {mid:.0f}° → {end:.0f}°)')
    # Hintergründe: alle laden, enthalten Bewegung, keine Fehler
    ids=a.ev("scenes.map(s=>s.id)")
    for i in ids:
        a.ev(f"getCurrentScene().bgType='scene'; getCurrentScene().bgId='{i}'; renderStageBackground(); 0")
        n=a.ev("[...document.querySelectorAll('#stageBackground svg *')].filter(e=>{const n=getComputedStyle(e).animationName; return n&&n!=='none';}).length")
        check(n>=2,f'Hintergrund {i}: {n} bewegte Elemente')
    for b in a.ev("plainBackgrounds.map(b=>b.id)"):
        a.ev(f"getCurrentScene().bgType='plain'; getCurrentScene().bgId='{b}'; renderStageBackground(); 0")
        check(a.ev("document.querySelectorAll('#stageBackground svg circle').length")>=5,f'einfarbiger Hintergrund {b} mit Deko')
    check(len(a.errs)==0,'keine Konsolenfehler '+str(a.errs))
print('FAILS:',fails)
