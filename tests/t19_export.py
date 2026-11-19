import sys, os, json, subprocess, tempfile, shutil
from harness import App, DEFAULT_PATH, REC_STUB
path=sys.argv[1] if len(sys.argv)>1 else DEFAULT_PATH
fails=[]
def check(cond,msg):
    print(('PASS ' if cond else 'FAIL ')+msg)
    if not cond: fails.append(msg)

# ---------- Untertitel + Dialog (ohne Aufnahme)
with App(path,lang='de') as a:
    pg=a.pg
    pg.click('#exportBtn'); pg.wait_for_timeout(200)
    check(pg.locator('.dyn-dlg').count()==1,'Export-Dialog öffnet sich')
    fm=a.ev("Exporter.formats().map(f=>f[0])")
    check('mp4' in fm and any(x.startswith('webm') for x in fm),f'Formate: MP4 und WebM verfügbar {fm}')
    opts=a.ev("[...document.querySelectorAll('.dyn-dlg select')].map(s=>[...s.options].map(o=>o.value))")
    check(len(opts)==5 and 'hi' in opts[4] and 'tiny' in opts[4] and '1920x1080' in opts[2],'Auswahl: Umfang, Format, Auflösung, Bildrate, Qualität')
    t0=a.ev("document.querySelector('.exp-info').textContent")
    pg.select_option('.dyn-dlg select >> nth=4','tiny'); t1=a.ev("document.querySelector('.exp-info').textContent")
    import re
    mb=lambda t: float(re.search(r'([\d.]+) MB',t).group(1))
    check(mb(t1)<mb(t0),f'stärkere Kompression → kleinere Datei ({t0.split("·")[1].strip()} → {t1.split("·")[1].strip()})')
    check('stumm' in a.ev("document.querySelector('.exp-warn').textContent") or a.ev("document.querySelector('.exp-tabaudio').checked"),'Hinweis/Haken zu Browserstimmen')
    with pg.expect_download() as dl: pg.click('.exp-sub-srt-de')
    f=os.path.join(tempfile.mkdtemp(),'u.srt'); dl.value.save_as(f); srt=open(f,encoding='utf-8').read()
    check(srt.startswith('1\n00:00:00,') and ' --> ' in srt and 'Guten Tag' in srt and 'Konto' in srt,'SRT Deutsch mit Zeiten und beiden Sprechern')
    cues=re.findall(r'(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)',srt)
    sec=lambda h,m,s,ms:int(h)*3600+int(m)*60+int(s)+int(ms)/1000
    c0=(sec(*cues[0][:4]),sec(*cues[0][4:])); c1=(sec(*cues[1][:4]),sec(*cues[1][4:]))
    check(c0[1]>c0[0] and c1[0]>=c0[1] and c1[0]>c0[0],f'Zeiten aufsteigend, keine Überlappung {c0} {c1}')
    with pg.expect_download() as dl: pg.click('.exp-sub-vtt-en')
    f=os.path.join(tempfile.mkdtemp(),'u.vtt'); dl.value.save_as(f); vtt=open(f,encoding='utf-8').read()
    check(vtt.startswith('WEBVTT') and 'Good morning' in vtt and '.' in vtt.split('-->')[0],'VTT Englisch (Demo hält beide Sprachen)')
    check(not a.errs,'keine Konsolenfehler '+str(a.errs))

# ---------- echter Export (Tab-Aufnahme: Fenster unter Xvfb nötig)
if os.environ.get('DISPLAY'):
    with App(path,lang='de',capture=True,viewport=(1280,800)) as a:
        pg=a.pg; pg.set_default_timeout(120000)
        # kurze Szene: 3 s, nur ein Satz
        a.ev("(()=>{ const s=scenesTimeline[0]; s.duration=3; s.characters[1].script=''; s.characters[0].script='Hallo Welt.'; s.characters[0].speechStart=0.3; s.characters[0].clips=[]; renderSpeakerTracks(); renderObjectTimeline(); })()")
        pg.click('#exportBtn')
        pg.select_option('.dyn-dlg select >> nth=1','mp4'); pg.select_option('.dyn-dlg select >> nth=2','960x540'); pg.select_option('.dyn-dlg select >> nth=3','24'); pg.select_option('.dyn-dlg select >> nth=4','low')
        pg.uncheck('.exp-tabaudio')
        pg.click('.exp-go')
        pg.wait_for_selector('.exp-save',timeout=120000)
        st=a.ev("document.querySelector('.exp-status').textContent"); print('STATUS',st)
        check('MP4' in st and '960×540' in st,'Export fertig als MP4 960×540 '+st)
        check(a.ev("Exporter.last.cropped")==True,'Ausschnitt exakt auf die Bühne (CropTarget)')
        with pg.expect_download() as dl: pg.click('.exp-save')
        vf=os.path.join(tempfile.mkdtemp(),'v.mp4'); dl.value.save_as(vf); sz=os.path.getsize(vf)
        check(sz>5000,f'Datei gespeichert ({sz/1024:.0f} KB)')
        if shutil.which('ffprobe'):
            pr=json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',vf],capture_output=True,text=True).stdout or '{}')
            vs=[x for x in pr.get('streams',[]) if x['codec_type']=='video']; au=[x for x in pr.get('streams',[]) if x['codec_type']=='audio']
            check(vs and vs[0]['codec_name']=='h264' and vs[0]['width']==960 and vs[0]['height']==540,f'ffprobe: H.264 960×540 {vs[0]["codec_name"] if vs else None}')
            d=float(pr['format'].get('duration',0)); check(2.5<d<8,f'ffprobe: Dauer plausibel ({d:.1f} s)')
            check(bool(au),'ffprobe: Tonspur vorhanden (Mix)')
            # Bild prüfen: Frame aus der Mitte
            fr=os.path.join(OUT:=os.path.join(os.path.dirname(os.path.abspath(__file__)),'out'),'export_frame.png'); subprocess.run(['ffmpeg','-y','-v','error','-ss','1.5','-i',vf,'-frames:v','1',fr])
            check(os.path.exists(fr),'Frame aus dem Video extrahiert (out/export_frame.png)')
        else: print('ffprobe nicht vorhanden – Containerprüfung übersprungen')
        check(a.ev("Exporter.last.cues.length")>=1 and a.ev("Exporter.last.cues[0].text")=='Hallo Welt.','echte Untertitel-Zeiten mitgeschrieben')
        check(not a.ev("document.body.classList.contains('exporting')"),'Oberfläche nach Export wiederhergestellt')
        # Abbruch mit Esc
        pg.evaluate("document.querySelector('.dyn-dlg').remove()")
        check(not a.errs,'keine Konsolenfehler '+str(a.errs))
else:
    print('SKIP echter Export: kein DISPLAY (starte mit xvfb-run -a)')
print('FAILS:',fails)
