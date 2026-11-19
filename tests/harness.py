import os, json
HERE=os.path.dirname(os.path.abspath(__file__))
DEFAULT_PATH=os.path.join(HERE,'..','index.html')
OUT=os.path.join(HERE,'out'); os.makedirs(OUT,exist_ok=True)
def launch_kwargs():
    kw={'args':['--no-sandbox','--autoplay-policy=no-user-gesture-required']}
    exe=os.environ.get('CHROME_PATH') or ('/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None)
    if exe: kw['executable_path']=exe
    return kw
from playwright.sync_api import sync_playwright
STUB = r"""
(()=>{
  const voices=[
   {name:'Microsoft Katja Online (Natural) - German (Germany)',lang:'de-DE',localService:false,voiceURI:'katja'},
   {name:'Microsoft Conrad Online (Natural) - German (Germany)',lang:'de-DE',localService:false,voiceURI:'conrad'},
   {name:'Google Deutsch',lang:'de-DE',localService:false,voiceURI:'gde'},
   {name:'Samantha',lang:'en-US',localService:true,voiceURI:'sam'},
   {name:'Microsoft Aria Online (Natural) - English (United States)',lang:'en-US',localService:false,voiceURI:'aria'},
   {name:'Microsoft Guy Online (Natural) - English (United States)',lang:'en-US',localService:false,voiceURI:'guy'},
   {name:'Google UK English Female',lang:'en-GB',localService:false,voiceURI:'gukf'}];
  window.__sp={log:[],active:0,maxActive:0,boundaries:true,speed:40,fail:false,noStart:false};
  class U{constructor(t){this.text=t;this.rate=1;this.pitch=1;this.volume=1;this.voice=null;this.lang='';}}
  window.SpeechSynthesisUtterance=U;
  let cur=null, timers=[]; const queue=[];
  const synth={ get speaking(){return !!cur;}, paused:false, pending:false,
    getVoices(){return voices;},
    speak(u){ if(u.text.trim()===''){ setTimeout(()=>u.onend&&u.onend({}),0); return;} queue.push(u); pump(); },
    cancel(){ timers.forEach(clearTimeout); timers=[]; if(cur){const c=cur;cur=null; __sp.active--; c.onerror&&c.onerror({error:'canceled'});} queue.length=0; },
    pause(){},resume(){},addEventListener(){}, removeEventListener(){} };
  function pump(){ if(cur||!queue.length) return; const u=queue.shift(); cur=u;
    if(__sp.fail){ setTimeout(()=>{ cur=null; u.onerror&&u.onerror({error:'synthesis-failed'}); pump(); },10); return; }
    if(__sp.noStart) return;
    setTimeout(()=>{ if(cur!==u) return; __sp.active++; __sp.maxActive=Math.max(__sp.maxActive,__sp.active);
      __sp.log.push({text:u.text,t:performance.now(),voice:u.voice&&u.voice.name,rate:u.rate,pitch:u.pitch,ev:'start'});
      u.onstart&&u.onstart({});
      const ms=__sp.speed/(u.rate||1);
      if(__sp.boundaries) [...u.text.matchAll(/\S+/g)].forEach(m=>timers.push(setTimeout(()=>{ if(cur===u) u.onboundary&&u.onboundary({name:'word',charIndex:m.index,charLength:m[0].length}); }, m.index*ms)));
      timers.push(setTimeout(()=>{ if(cur===u){ cur=null; __sp.active--; __sp.log.push({text:u.text,t:performance.now(),ev:'end'}); u.onend&&u.onend({}); pump(); } }, u.text.length*ms+100));
    },120); }
  Object.defineProperty(window,'speechSynthesis',{value:synth,configurable:true});
  // Mund-Mitschnitt
  window.__v=[];
  document.addEventListener('DOMContentLoaded',()=>{
    new MutationObserver(ms=>{ ms.forEach(m=>{ if(m.type==='attributes'&&m.attributeName==='data-v'){ __v.push({id:m.target.dataset.instId,v:m.target.dataset.v,t:performance.now()}); } }); })
      .observe(document.getElementById('stageCharacters'),{subtree:true,attributes:true,attributeFilter:['data-v']});
  });
})();
"""
REC_STUB=r"""
(()=>{
  function wav(sec){ const R=8000,n=Math.floor(R*sec),b=new ArrayBuffer(44+n*2),v=new DataView(b);
    const s=(o,t)=>{for(let i=0;i<t.length;i++)v.setUint8(o+i,t.charCodeAt(i));};
    s(0,'RIFF');v.setUint32(4,36+n*2,true);s(8,'WAVEfmt ');v.setUint32(16,16,true);v.setUint16(20,1,true);v.setUint16(22,1,true);v.setUint32(24,R,true);v.setUint32(28,R*2,true);v.setUint16(32,2,true);v.setUint16(34,16,true);s(36,'data');v.setUint32(40,n*2,true);
    for(let i=0;i<n;i++) v.setInt16(44+i*2,Math.round(6000*Math.sin(i*0.2)),true); return new Blob([b],{type:'audio/wav'}); }
  window.__rec={calls:0,lang:[]};
  Object.defineProperty(navigator,'mediaDevices',{value:{getUserMedia:async()=>({getTracks:()=>[{stop(){}}]})},configurable:true});
  class MR{ constructor(s,o){this.state='inactive';this.mimeType='audio/wav';}
    start(){this.state='recording';} stop(){ this.state='inactive'; setTimeout(()=>{ this.ondataavailable&&this.ondataavailable({data:wav(1.5)}); this.onstop&&this.onstop(); },20); } }
  MR.isTypeSupported=t=>t==='audio/wav'||t==='audio/webm';
  window.MediaRecorder=MR;
  class SR{ constructor(){ __rec.calls++; }
    start(){ __rec.lang.push(this.lang); setTimeout(()=>{ this.onresult&&this.onresult({results:[Object.assign([{transcript:this.lang==='en-US'?'Hello this is a test':'Hallo das ist ein Test'}],{isFinal:true})]}); },60); }
    stop(){ this.onend&&this.onend(); } }
  window.SpeechRecognition=SR;
})();
"""
class App:
    def __init__(self, path, viewport=(1400,900), stub=True, mobile=False, lang='de', capture=False):
        self.path=os.path.abspath(path); self.viewport=viewport; self.stub=stub; self.mobile=mobile; self.lang=lang
        self.errs=[]; self.capture=capture
    def __enter__(self):
        self.pw=sync_playwright().start()
        kw0=launch_kwargs()
        if self.capture:   # Tab-Aufnahme braucht ein Fenster (unter Xvfb) und diese Schalter
            kw0['headless']=False; kw0['args']+=['--auto-accept-this-tab-capture','--auto-select-tab-capture-source-by-title=Stagehand','--disable-gpu-sandbox','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']
        self.b=self.pw.chromium.launch(**kw0)
        kw={'viewport':{'width':self.viewport[0],'height':self.viewport[1]},'locale':'de-DE' if self.lang=='de' else 'en-US'}
        if self.mobile: kw.update({'has_touch':True,'is_mobile':True,'device_scale_factor':2})
        self.ctx=self.b.new_context(**kw)
        self.pg=self.ctx.new_page()
        self.pg.add_init_script("try{localStorage.setItem('sh-lang','%s')}catch(e){}"%self.lang)
        if self.stub: self.pg.add_init_script(STUB)
        self.pg.on('pageerror',lambda e:self.errs.append('PAGEERR '+str(e)))
        self.pg.on('console',lambda m:self.errs.append('CONSOLE '+m.type+': '+m.text) if m.type=='error' else None)
        self.pg.goto('file://'+self.path); self.pg.wait_for_timeout(600)
        return self
    def __exit__(self,*a):
        self.b.close(); self.pw.stop()
    def ev(self,js): return self.pg.evaluate(js)
