#!/usr/bin/env python3
"""
Kleiner lokaler TTS-Server für Stagehand Studio  /  Tiny local TTS server for Stagehand Studio.

DE: Das Tool schickt pro Sprechzeile  POST {"text": "...", "lang": "de|en", "voice": "..."}  und erwartet
    eine Audiodatei (WAV) zurück. Dieser Server übersetzt das in einen Aufruf von Piper (https://github.com/OHF-Voice/piper1-gpl)
    – oder liefert mit --engine tone einen Testton (zum Ausprobieren der Anbindung ohne Stimmmodell).
EN: The tool sends  POST {"text","lang","voice"}  for every spoken line and expects audio (WAV) back. This server
    forwards it to Piper – or returns a test tone with --engine tone (to try the integration without a voice model).

Beispiele / Examples
  python scripts/tts_server.py --model de=voices/de_DE-thorsten-medium.onnx --model en=voices/en_US-lessac-medium.onnx
  python scripts/tts_server.py --engine tone            # nur Testton / test tone only

In Stagehand Studio:  Kopfzeile „Stimmen“ → URL  http://localhost:5002/tts  eintragen, dann pro Figur
„Eigener TTS-Server“ als Stimme wählen.  /  Top bar “Voices” → enter the URL, then choose “Own TTS server” per figure.

Lizenzhinweis / Licence note: Sprachmodelle haben eigene Lizenzen (teils nicht-kommerziell) – siehe docs/VOICES.md.
"""
import argparse, io, json, math, os, struct, subprocess, sys, tempfile, wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs


def tone_wav(text, rate=22050):
    """Testton: Dauer ~ Textlänge, Silben-artig moduliert, mit Pause bei Satzzeichen."""
    words = text.split()
    samples = []
    for w in words:
        n = max(1, len(w))
        dur = 0.09 * n + 0.05
        for i in range(int(dur * rate)):
            t = i / rate
            env = 0.5 * (1 - math.cos(2 * math.pi * min(1.0, t / dur)))
            f = 180 + 40 * math.sin(2 * math.pi * 3.5 * t)
            samples.append(int(9000 * env * math.sin(2 * math.pi * f * t)))
        gap = 0.25 if w[-1] in ".!?,;:" else 0.07
        samples.extend([0] * int(gap * rate))
    if not samples:
        samples = [0] * int(0.2 * rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(rate)
        wf.writeframes(struct.pack("<%dh" % len(samples), *samples))
    return buf.getvalue()


def piper_wav(text, model, speaker=None):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "out.wav")
        cmd = [sys.executable, "-m", "piper", "-m", model, "-f", out]
        if speaker is not None:                       # Mehrsprecher-Modelle (z. B. libritts): Feld „Stimmenname“ = Sprecher-Nr.
            cmd += ["-s", str(speaker)]
        subprocess.run(cmd, input=text.encode("utf-8"), check=True, stdout=subprocess.DEVNULL)
        with open(out, "rb") as f:
            return f.read()


class Handler(BaseHTTPRequestHandler):
    models = {}
    engine = "piper"
    log_requests = False

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")   # Chrome: öffentliche Seite → localhost

    def do_OPTIONS(self):
        self.send_response(204); self._cors(); self.end_headers()

    def _reply_error(self, code, msg):
        body = msg.encode("utf-8")
        self.send_response(code); self._cors()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def _speak(self, text, lang, voice):
        text = (text or "").strip()
        if not text:
            return self._reply_error(400, "empty text")
        if self.log_requests:
            print(json.dumps({"text": text, "lang": lang, "voice": voice}, ensure_ascii=False), flush=True)
        try:
            if self.engine == "tone":
                wav = tone_wav(text)
            else:
                model = self.models.get(voice) or self.models.get(lang) or next(iter(self.models.values()), None)   # Name > Sprache > erste Stimme
                if not model:
                    return self._reply_error(500, "no model configured (use --model de=... --model en=...)")
                wav = piper_wav(text, model, voice if (voice or "").isdigit() else None)
        except Exception as e:                                   # noqa
            return self._reply_error(500, "synthesis failed: %s" % e)
        self.send_response(200); self._cors()
        self.send_header("Content-Type", "audio/wav")
        self.send_header("Content-Length", str(len(wav))); self.end_headers(); self.wfile.write(wav)

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            d = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._reply_error(400, "invalid JSON")
        self._speak(d.get("text"), d.get("lang", "de"), d.get("voice", ""))

    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query)
        if u.path == "/health":
            body = b"ok"; self.send_response(200); self._cors(); self.send_header("Content-Length", "2"); self.end_headers(); self.wfile.write(body); return
        self._speak((q.get("text") or [""])[0], (q.get("lang") or ["de"])[0], (q.get("voice") or [""])[0])

    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=5002)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--engine", choices=["piper", "tone"], default="piper")
    ap.add_argument("--model", action="append", default=[], metavar="NAME=PFAD.onnx",
                    help="Stimme je Sprache oder Name, z. B. de=voices/de_DE-thorsten-medium.onnx")
    ap.add_argument("--log-requests", action="store_true")
    a = ap.parse_args()
    Handler.engine = a.engine; Handler.log_requests = a.log_requests
    for m in a.model:
        k, _, v = m.partition("=")
        Handler.models[k] = v
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print("TTS server on http://%s:%d/tts  (engine: %s)" % (a.host, a.port, a.engine), flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
