# Stagehand Studio

**DE** · [English below](#english)

Browser-Editor für **Erklärvideos mit comichaften Figuren**: Figuren sprechen, gehen, zeigen und reagieren – mit Szenen, Timeline, Sprechblasen, Hintergrundmusik und Lippen-Synchronisation. Eine einzige HTML-Datei, kein Build, keine Abhängigkeiten.

```
index.html   die komplette App (HTML + CSS + JS)
```

Direkt öffnen (Doppelklick auf `index.html`) oder per GitHub Pages veröffentlichen (Settings → Pages → Branch `main`, Ordner `/ (root)`).

## Funktionen

* **20 Figuren** in je 4 Ansichten (Front, ¾, Seite, Rücken), einheitlich animierbar: Stehen, Gehen, Zeigen, Winken, Erklären, Jubeln; Reaktionen (Freude, Ärger, Verwunderung, Neuigkeiten, Zuhören).
* **Szenen & Übergänge**: Branchen-Szenen, einfache Hintergründe, Objekte und Text auf der Bühne, Überblenden/Schieben/Wischblende/Zoom.
* **Timeline pro Szene**: Sprache, Pose-Clips, Reaktion, Objekte, Hintergrund und Musik als verschiebbare Balken; Gesamtfilm-Leiste über alle Szenen.
* **Sprachausgabe & Lippen-Sync**: je Figur Stimme, Tempo, Tonhöhe, „Ton“ und „Sprechblase“ einzeln schaltbar; Mundformen aus dem Text (11 Visemen), nachgeführt an die Wortgrenzen der Stimme und kalibriert pro Stimme. Immer nur eine Stimme gleichzeitig, Zeilen laufen nacheinander.
* **Deutsch und Englisch**: Oberfläche per **DE | EN**-Schalter; die **Sprache jeder Figur** (Sprechtext, Stimmenauswahl, Mundformen) ist unabhängig wählbar – auch gemischte Dialoge.
* **Stimmquellen**: Browser-/Systemstimmen, eigene **Audiodatei** pro Zeile oder ein **eigener TTS-Server** (z. B. Piper) → [docs/VOICES.md](docs/VOICES.md)
* **Hintergrundmusik**: vier Synth-Stile (WebAudio, kein Download) **oder eigene Dateien** (MP3, M4A, WAV, OGG, MP4 mit Tonspur) pro Szene – mit Lautstärke, Schleife und automatischer Absenkung beim Sprechen. Geladene Dateien gelten nur für die laufende Sitzung (sie werden nicht in der Seite gespeichert).
* **Bewegung**: sinusförmiger Gehzyklus mit Fußhub und Rumpf-Wippen, überlappende Kopfbewegung, weiche Posenübergänge (Winken → Ruhe gleitet statt zu springen), Atmen, Blinzeln, Blickwechsel, Gestik beim Sprechen.
* **Hintergründe** im Cartoon-Stil mit Konturen, Verläufen und sanfter Bewegung (Wolken, Fahnen, Uhrzeiger, Lampen, Pflanzen, Ballons); dazu acht einfarbige Hintergründe.
* **Handy-tauglich** (iPhone/Android): Touch-Bedienung, feste Bühne 960×540 skaliert.

## Hinweise zu den Stimmen

Ohne Einrichtung nutzt das Tool die Stimmen des Browsers/Betriebssystems – die Qualität hängt vom Gerät ab (Edge „Natural“, Apple „Premium“ sind gut). Bessere Stimmen: eigene Audiodatei oder lokaler TTS-Server. **Es sind keine Stimmmodelle im Repository**; welche frei nutzbar sind, steht mit Quellen in [docs/VOICES.md](docs/VOICES.md).

## Tests

Browser-Tests mit Playwright (Rig, Bearbeiten, Wiedergabe, Lippen-Sync, Handy, Robustheit, Deutsch/Englisch, Audio-Quellen):

```bash
pip install -r tests/requirements.txt && python -m playwright install chromium
tests/run_all.sh          # optional: CHROME_PATH=/pfad/zu/chrome
```

## Stand / Grenzen

* MP4-Export und Embed-Code sind Platzhalter (der Export soll später serverseitig rendern).
* Es gibt noch kein Speichern/Laden von Projekten; Audiodateien pro Zeile gelten nur für die laufende Sitzung.
* Sprachausgabe der Browser kann nicht mehrere Stimmen parallel – Überschneidungen werden nacheinander gesprochen.
* Lizenz des Codes: noch nicht festgelegt (ohne Lizenzdatei gelten die gesetzlichen Standardrechte).

---

## English

Browser editor for **explainer videos with cartoon-style characters**: figures speak, walk, point and react – with scenes, timeline, speech bubbles, background music and lip sync. One single HTML file, no build step, no dependencies.

```
index.html   the whole app (HTML + CSS + JS)
```

Open it directly (double-click `index.html`) or publish via GitHub Pages (Settings → Pages → branch `main`, folder `/ (root)`).

## Features

* **20 characters** in 4 views each (front, ¾, side, back), animated consistently: standing, walking, pointing, waving, explaining, cheering; reactions (joy, anger, surprise, news, listening).
* **Scenes & transitions**: industry scenes, plain backgrounds, objects and text on the stage, fade/slide/wipe/zoom.
* **Per-scene timeline**: speech, pose clips, reaction, objects, background and music as draggable bars; an overall film strip across all scenes.
* **Speech & lip sync**: per figure voice, speed, pitch, and separate “sound” and “speech bubble” switches; mouth shapes derived from the text (11 visemes), re-anchored to the voice’s word boundaries and calibrated per voice. Only one voice at a time; lines are spoken one after another.
* **German and English**: UI via the **DE | EN** switch; the **language of each figure** (spoken text, voice choice, mouth shapes) is set independently – mixed-language dialogues work.
* **Voice sources**: browser/OS voices, your own **audio file** per line, or **your own TTS server** (e.g. Piper) → [docs/VOICES.md](docs/VOICES.md)
* **Background music**: four synth styles (WebAudio, no download) **or your own files** (MP3, M4A, WAV, OGG, MP4 with an audio track) per scene – with volume, loop and automatic ducking while someone speaks. Loaded files only live for the current session (they are not stored in the page).
* **Motion**: sine-based walk cycle with foot lift and torso bob, overlapping head movement, smooth pose transitions (wave → rest glides instead of snapping), breathing, blinking, glances, gestures while speaking.
* **Backgrounds** in cartoon style with outlines, gradients and gentle motion (clouds, bunting, clock hands, lamps, plants, balloons); plus eight plain backgrounds.
* **Mobile-friendly** (iPhone/Android): touch controls, fixed 960×540 stage scaled to fit.

## About the voices

Out of the box the tool uses your browser/OS voices – quality depends on the device (Edge “Natural”, Apple “Premium” are good). For better voices use your own audio file or a local TTS server. **No voice models are included in the repository**; which ones are free to use, with sources, is in [docs/VOICES.md](docs/VOICES.md).

## Tests

Playwright browser tests (rig, editing, playback, lip sync, mobile, robustness, German/English, audio sources):

```bash
pip install -r tests/requirements.txt && python -m playwright install chromium
tests/run_all.sh          # optional: CHROME_PATH=/path/to/chrome
```

## Status / limits

* MP4 export and embed code are placeholders (export is meant to render server-side later).
* No saving/loading of projects yet; per-line audio files only live for the current session.
* Browser speech synthesis cannot speak several voices in parallel – overlapping lines are spoken one after another.
* Code licence: not decided yet (without a licence file the default legal rights apply).
