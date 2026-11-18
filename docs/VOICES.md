# Stimmen / Voices

**DE** · [English below](#english)

## Deutsch

Stagehand Studio kennt drei Stimmquellen. Pro Figur wählbar, Sprache je Figur Deutsch oder Englisch:

| Quelle | Qualität | Aufwand | Besonderheiten |
|---|---|---|---|
| **Browser-/Systemstimmen** (Web Speech API) | je nach Gerät: Edge „Natural“-Stimmen und Apple „Premium/Siri“ sind gut, iOS-Standardstimmen eher schwach | keiner | immer nur eine Stimme gleichzeitig; Chrome-„Google“-Stimmen laufen online und liefern keine Wortgrenzen |
| **Eigene Audiodatei** pro Sprechzeile | beliebig – z. B. aus einem hochwertigen TTS-Dienst oder selbst gesprochen | Datei erzeugen und hochladen | Sprechtext dient als Transkript für Blase und Lippen; Mundbewegung folgt dem Text-Plan und ruht in Sprechpausen der Datei |
| **Eigener TTS-Server** (z. B. Piper) | gut bis sehr gut, offline, Stimme frei wählbar | Server lokal starten (`scripts/tts_server.py`) | Tool sendet `POST {"text","lang","voice"}`, Antwort = WAV/MP3; Dauer wird gemessen, die Timeline passt sich an |

### Was ich nicht getestet habe

Die Entwicklungsumgebung hatte keinen Zugriff auf huggingface.co. **Es wurden keine Stimmmodelle heruntergeladen oder angehört.** Getestet ist die Anbindung (Server-Protokoll, Audio-Wiedergabe, Lippen-Takt, Ausfallverhalten) mit einem Testton-Server (`--engine tone`). Die Klangqualität der Piper-Stimmen und `scripts/fetch_voices.py` sind ungetestet – bitte lokal ausprobieren.

### Lizenzstatus der empfohlenen Piper-Stimmen

Gelesen aus den Modellkarten (`MODEL_CARD`) im Repository [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices). Das ist keine Rechtsberatung – vor kommerzieller Nutzung die Karten und Datensatz-Lizenzen selbst prüfen.

| Stimme | Sprache | Daten-Lizenz | Training | Einschätzung |
|---|---|---|---|---|
| [`de_DE-thorsten-medium`](https://huggingface.co/rhasspy/piper-voices/blob/main/de/de_DE/thorsten/medium/MODEL_CARD) | de | CC0 | Fine-Tuning der Basis *rdh* (nl_BE, CC0) | unkritisch, **empfohlen für Deutsch** |
| [`en_US-ljspeech-high`](https://huggingface.co/rhasspy/piper-voices/raw/main/en/en_US/ljspeech/high/MODEL_CARD) | en | Public Domain | von Grund auf trainiert (LJ Speech) | unkritisch, **empfohlen für Englisch** (eine weibliche Stimme) |
| [`en_US-libritts-high`](https://huggingface.co/rhasspy/piper-voices/blob/refs%2Fpr%2F11/en/en_US/libritts/high/MODEL_CARD) | en | CC BY 4.0 | von Grund auf trainiert | viele Sprecher (auch männlich); **Namensnennung nötig** |
| [`de_DE-thorsten-high`](https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/de/de_DE/thorsten/high/MODEL_CARD) | de | CC0 | Fine-Tuning der **Lessac**-Stimme | Lessac-Lizenz (Blizzard 2013) kann mitgelten → bei kommerzieller Nutzung meiden/klären |
| [`en_US-lessac-high`](https://huggingface.co/rhasspy/piper-voices/blob/v1.0.0/en/en_US/lessac/high/MODEL_CARD) | en | Blizzard-2013-Lizenz (eigene Bedingungen) | von Grund auf | Bedingungen lesen, nicht als „frei“ behandeln |

Aus früherer Recherche (in dieser Sitzung **nicht** erneut an der Quelle geprüft): `pavoque` (de) steht unter CC BY-NC-SA, und mehrere englische Stimmen (u. a. `ryan`, `hfc`, `l2arctic`) gelten als nicht-kommerziell. Wer eine Stimme außerhalb der Tabelle nutzt, liest zuerst deren `MODEL_CARD`.

Vorbereitet: [`voices/manifest.json`](../voices/manifest.json) und `scripts/fetch_voices.py` laden die drei empfohlenen Stimmen und zeigen die Lizenzzeilen der Modellkarte an. Modelle gehören **nicht** ins Repository (`voices/*.onnx` ist in `.gitignore`).

### Weitere Möglichkeiten (nicht eingebaut)

* **Kokoro** – [Apache-2.0-Gewichte](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/README.md?code=true), mehrere Sprachen; Trainingsdaten enthalten u. a. CC-BY-Sätze (SIWIS, Koniwa). Eine deutsche Variante gibt es als [Thorsten-Voice/Kokoro](https://huggingface.co/Thorsten-Voice/Kokoro) (Apache 2.0, Datensatz CC0), sie braucht aber deutsche Forks von `misaki`/`kokoro` und `espeak-ng`. Lässt sich über denselben HTTP-Vertrag anschließen (eigener kleiner Server, der `{"text","lang","voice"}` entgegennimmt).
* **Browser-nativ** (WASM/WebGPU) ohne Server wäre möglich, ist hier aber nicht enthalten: kein Zugriff auf Modelle zum Testen, und die Modelle sind mehrere zehn MB groß.

### Eigener Server in der Praxis

```bash
pip install piper-tts
python scripts/fetch_voices.py                       # lädt Stimmen nach voices/
python scripts/tts_server.py \
  --model de=voices/de_DE-thorsten-medium.onnx \
  --model en=voices/en_US-ljspeech-high.onnx
```

In Stagehand Studio: Kopfzeile **Stimmen** → `http://localhost:5002/tts` → „Verbindung testen“. Danach je Figur als Stimme **Eigener TTS-Server** wählen. Das Feld „Stimmenname“ wählt bei `tts_server.py` ein Modell nach Namen (`--model name=pfad`) oder – bei Zahlen – die Sprecher-Nr. eines Mehrsprecher-Modells.

Hinweise:

* Piper bringt einen eigenen HTTP-Server mit, der in der dokumentierten Variante rohen Text per POST oder `?text=` per GET annimmt und **keine CORS-Header** setzt ([Beschreibung](https://tderflinger.github.io/piper-docs/codereading/python_run/piper/http_server)); ein Browser-Tool kann ihn so nicht direkt aufrufen. Deshalb gibt es `scripts/tts_server.py`.
* Läuft das Tool über `https://` (z. B. GitHub Pages), erlaubt Chrome Aufrufe an `http://localhost`; Safari blockiert das als gemischten Inhalt. In dem Fall das Tool lokal öffnen oder den Server per HTTPS bereitstellen.
* Steht `{text}` in der URL (z. B. `http://localhost:5000/?text={text}`), fragt das Tool per GET ab; `{lang}` und `{voice}` werden ebenfalls ersetzt.

---

## English

Stagehand Studio supports three voice sources, selectable per figure, with the speech language (German or English) set per figure:

| Source | Quality | Effort | Notes |
|---|---|---|---|
| **Browser/OS voices** (Web Speech API) | device-dependent: Edge “Natural” voices and Apple “Premium/Siri” are good, default iOS voices are weak | none | only one voice at a time; Chrome “Google” voices are online and give no word boundaries |
| **Your own audio file** per line | anything – e.g. from a high-quality TTS service or recorded yourself | create and upload the file | the line text acts as transcript for bubble and lips; lip movement follows the text plan and rests during pauses in the file |
| **Your own TTS server** (e.g. Piper) | good to very good, offline, any voice | run it locally (`scripts/tts_server.py`) | the tool sends `POST {"text","lang","voice"}` and expects WAV/MP3 back; the duration is measured and the timeline adapts |

### What was not tested

The development sandbox had no access to huggingface.co. **No voice models were downloaded or listened to.** What is tested is the integration (server protocol, audio playback, lip timing, failure behaviour) using a test-tone server (`--engine tone`). The sound quality of the Piper voices and `scripts/fetch_voices.py` are untested – please try them locally.

### Licence status of the recommended Piper voices

Read from the model cards (`MODEL_CARD`) in [rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices). This is not legal advice – check the cards and dataset licences yourself before commercial use. See the table above for per-voice links: **`de_DE-thorsten-medium`** (CC0, fine-tuned from a CC0 base) and **`en_US-ljspeech-high`** (public domain, trained from scratch) are the clean picks; **`en_US-libritts-high`** is CC BY 4.0 (attribution required, many speakers). **`de_DE-thorsten-high`** is fine-tuned from the Lessac voice and **`en_US-lessac-*`** is under the Blizzard 2013 licence with its own terms – avoid for commercial use until checked.

From earlier research (not re-verified at the source in this session): `pavoque` (de) is CC BY-NC-SA and several English voices (e.g. `ryan`, `hfc`, `l2arctic`) are considered non-commercial. For any voice outside the table, read its `MODEL_CARD` first.

Prepared: [`voices/manifest.json`](../voices/manifest.json) and `scripts/fetch_voices.py` download the three recommended voices and print the licence lines of each model card. Models are **not** committed (`voices/*.onnx` is git-ignored).

### Other options (not included)

* **Kokoro** – [Apache-2.0 weights](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/README.md?code=true), multiple languages; its training data includes CC-BY sets (SIWIS, Koniwa). A German variant exists as [Thorsten-Voice/Kokoro](https://huggingface.co/Thorsten-Voice/Kokoro) (Apache 2.0, CC0 dataset) but needs German forks of `misaki`/`kokoro` plus `espeak-ng`. It can plug in through the same HTTP contract (a small server accepting `{"text","lang","voice"}`).
* **In-browser** (WASM/WebGPU) without a server would be possible but is not included: no model access here for testing, and the models are tens of MB each.

### Using your own server

```bash
pip install piper-tts
python scripts/fetch_voices.py
python scripts/tts_server.py \
  --model de=voices/de_DE-thorsten-medium.onnx \
  --model en=voices/en_US-ljspeech-high.onnx
```

In Stagehand Studio: top bar **Voices** → `http://localhost:5002/tts` → “Test connection”. Then choose **Own TTS server** as the voice per figure. With `tts_server.py` the “voice name” field selects a model by name (`--model name=path`) or, if numeric, the speaker number of a multi-speaker model.

Notes:

* Piper ships its own HTTP server which, in the documented version, takes raw text via POST or `?text=` via GET and sets **no CORS headers** ([description](https://tderflinger.github.io/piper-docs/codereading/python_run/piper/http_server)), so a browser tool cannot call it directly. That is why `scripts/tts_server.py` exists.
* If the tool is served over `https://` (e.g. GitHub Pages), Chrome allows calls to `http://localhost`; Safari blocks it as mixed content. In that case open the tool locally or serve the TTS server over HTTPS.
* If the URL contains `{text}` (e.g. `http://localhost:5000/?text={text}`) the tool uses GET; `{lang}` and `{voice}` are substituted as well.
