#!/usr/bin/env python3
"""
Lädt die in voices/manifest.json empfohlenen Piper-Stimmen nach voices/  (Modell + Konfiguration + Modellkarte).
Downloads the Piper voices listed in voices/manifest.json into voices/ (model + config + model card).

  python scripts/fetch_voices.py              # alle empfohlenen / all recommended
  python scripts/fetch_voices.py de_DE-thorsten-medium

Hinweis: Dieses Skript lief in der Entwicklungsumgebung NICHT (kein Zugriff auf huggingface.co) – bitte lokal ausführen
und die ausgegebene Lizenzzeile der Modellkarte prüfen. / This script could NOT be run in the development sandbox
(no access to huggingface.co) – run it locally and check the licence line it prints.
"""
import json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://huggingface.co/rhasspy/piper-voices/resolve/main/"


def fetch(url, dest):
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    if os.path.exists(dest):
        print("  vorhanden / exists:", os.path.relpath(dest, ROOT)); return
    print("  lade / downloading:", url)
    with urllib.request.urlopen(url, timeout=60) as r, open(dest + ".part", "wb") as f:
        while True:
            chunk = r.read(1 << 20)
            if not chunk: break
            f.write(chunk)
    os.replace(dest + ".part", dest)


def main():
    man = json.load(open(os.path.join(ROOT, "voices", "manifest.json"), encoding="utf-8"))
    want = set(sys.argv[1:])
    for v in man["voices"]:
        if want and v["id"] not in want: continue
        print(v["id"], "–", v["dataset_license"], "/", v["training"])
        for ext in (".onnx", ".onnx.json"):
            fetch(BASE + v["path"] + "/" + v["id"] + ext, os.path.join(ROOT, "voices", v["id"] + ext))
        card = os.path.join(ROOT, "voices", v["id"] + ".MODEL_CARD.txt")
        fetch(BASE + v["path"] + "/MODEL_CARD", card)
        text = open(card, encoding="utf-8", errors="replace").read()
        print("  Modellkarte / model card:", " | ".join(l.strip() for l in text.splitlines() if re.search(r"(?i)licen|finetuned|trained", l)))
    print("\nStart:  python scripts/tts_server.py --model de=voices/de_DE-thorsten-medium.onnx --model en=voices/en_US-ljspeech-high.onnx")
    print("Piper installieren / install Piper:  pip install piper-tts")


if __name__ == "__main__":
    try:
        main()
    except OSError as e:                      # URLError ist ein OSError
        sys.exit("Download fehlgeschlagen / download failed: %s\nNetzwerk/Proxy prüfen oder die Dateien manuell von %s laden." % (e, BASE))
