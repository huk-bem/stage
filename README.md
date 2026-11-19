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
* **Sprechblasen-Gestaltung (pro Figur)**: Button „Blase gestalten …“ je Sprecher → 11 Vorlagen (Klassisch, Comic-Sprechblase, Gedanke, Schrei, Flüstern, Erzähler, Notizzettel, Untertitel, Skizze, Retro-Terminal, Pop), Form (Rechteck, Kapsel, Oval, Wolke, Zacken, Erzählerkasten, Zettel, Balken, wackelig), Zeiger, Schrift (7 Gerätschriften), Größe, Fett/Kursiv, Text-/Füll-/Randfarbe, Randstärke, gestrichelt, Einblend-Effekt (Pop, Gummi, Ruf-Wackeln, Fallen, Hochgleiten, Aufklappen, sofort), „Wort springt beim Sprechen“, Textanzeige (Wort hervorheben / Mitschreiben / sofort), Sprechername, „Form folgt Reaktion“, Live-Vorschau, „Auf alle Figuren übertragen“. Schriften kommen vom Gerät (keine Downloads).
* **Frauenfiguren überarbeitet**: Haar fällt als zwei Strähnen mit freiem Hals (kein „Bart“ mehr), Ohren bei langem Haar verdeckt, sonst klein und tiefer, runde Koteletten statt spitzer Haarenden, schmalere Schultern und Taille.
* **Figurenstil**: je Figur Standard, Kontur, Cartoon (Kontur + größerer Kopf) oder Chibi (Riesenkopf).
* **Deutsch und Englisch**: Oberfläche per **DE | EN**-Schalter; die **Sprache jeder Figur** (Sprechtext, Stimmenauswahl, Mundformen) ist unabhängig wählbar – auch gemischte Dialoge.
* **Ziele für Gehen & Zeigen**: Ein Pose-Clip „Gehen“ bekommt über „👣 Ziel“ einen Zielpunkt, ein Clip „Zeigen“ über „👉 Ziel“ einen Punkt oder ein Objekt auf der Bühne (Tippen/Klicken; Esc bricht ab). Die Ziele erscheinen als verschiebbare Pins mit Weg-Linie; die Figur läuft wirklich dorthin (dreht sich ins Profil) bzw. streckt den Arm exakt in Richtung des Ziels.
* **Erzähler (Off-Sprecher)**: eigene Sprecherspur ohne Figur (＋ Erzähler) mit eigener Stimme, Timeline-Zeile und Untertitel-Balken unten; Ton und Blase einzeln schaltbar (nur Blase, nur Ton oder beides).
* **Texte, Stimmen und Aufnahmen je Sprache**: jede Sprechzeile (und der Erzähler) merkt sich Text, Stimme und Aufnahme getrennt für **Deutsch und Englisch**. Chips „DE ✓ 🎵 / EN ⚠“ zeigen, was vorhanden bzw. noch nicht übersetzt ist; „Alle Sprecher auf Deutsch/English“ schaltet das ganze Projekt um.
* **Aufnehmen & Transkribieren**: „🎙 Aufnehmen“ nimmt die Stimme im Browser auf (je Sprache getrennt); wenn der Browser Spracherkennung kann, entsteht dabei ein **Transkript**, das als Sprechtext/Blase übernommen und bearbeitet werden kann. „📝 Diktieren“ trägt nur den Text ein. Aufnahmen der **iOS-Sprachmemos** (oder anderer Rekorder) lassen sich als Audiodatei je Zeile und Sprache laden; den Text dazu tippst oder diktierst du als Transkript.
* **Eigenes Hintergrundbild**: Foto/Grafik hochladen (JPG, PNG, HEIC …; wird auf ≤1920 px verkleinert), Modus „füllen“ oder „einpassen“, Abdunkeln und Weichzeichnen.
* **Stimmquellen**: Browser-/Systemstimmen, eigene **Audiodatei** pro Zeile oder ein **eigener TTS-Server** (z. B. Piper) → [docs/VOICES.md](docs/VOICES.md)
* **Hintergrundmusik**: vier Synth-Stile (WebAudio, kein Download) **oder eigene Dateien** (MP3, M4A, WAV, OGG, MP4 mit Tonspur) pro Szene – mit Lautstärke, Schleife und automatischer Absenkung beim Sprechen. Geladene Dateien gelten nur für die laufende Sitzung (sie werden nicht in der Seite gespeichert).
* **Bewegung**: sinusförmiger Gehzyklus mit Fußhub und Rumpf-Wippen, überlappende Kopfbewegung, weiche Posenübergänge (Winken → Ruhe gleitet statt zu springen), Atmen, Blinzeln, Blickwechsel, Gestik beim Sprechen.
* **Hintergründe** im Cartoon-Stil mit Konturen, Verläufen und sanfter Bewegung (Wolken, Fahnen, Uhrzeiger, Lampen, Pflanzen, Ballons); dazu acht einfarbige Hintergründe.
* **Handy-tauglich** (iPhone/Android): Touch-Bedienung, feste Bühne 960×540 skaliert.

## Hinweise zu den Stimmen

Ohne Einrichtung nutzt das Tool die Stimmen des Browsers/Betriebssystems – die Qualität hängt vom Gerät ab (Edge „Natural“, Apple „Premium“ sind gut). Bessere Stimmen: eigene Audiodatei oder lokaler TTS-Server. **Es sind keine Stimmmodelle im Repository**; welche frei nutzbar sind, steht mit Quellen in [docs/VOICES.md](docs/VOICES.md).

## Tests

Browser-Tests mit Playwright (Rig, Bearbeiten, Wiedergabe, Lippen-Sync, Handy, Robustheit, Deutsch/Englisch, Audio-Quellen, Ziele, Aufnahme/Erzähler):

```bash
pip install -r tests/requirements.txt && python -m playwright install chromium
tests/run_all.sh          # optional: CHROME_PATH=/pfad/zu/chrome
```

## Stand / Grenzen

* MP4-Export und Embed-Code sind Platzhalter (der Export soll später serverseitig rendern).
* Es gibt noch kein Speichern/Laden von Projekten (auch Aufnahmen und Hintergrundbilder gelten nur für die laufende Sitzung); Audiodateien pro Zeile gelten nur für die laufende Sitzung.
* Transkription: Der Browser kann hochgeladene Dateien nicht in Text umwandeln, nur live beim Aufnehmen/Diktieren (je nach Browser; iOS-Safari nimmt und erkennt nicht immer gleichzeitig) – sonst Text tippen.
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
* **Speech-bubble styling (per figure)**: “Style bubble …” button per speaker → 11 presets (classic, comic speech, thought, shout, whisper, narrator, sticky note, subtitle, sketch, retro terminal, pop), shapes (box, pill, oval, cloud, burst, caption, note, bar, wobbly), pointer, font (7 device fonts), size, bold/italic, text/fill/border colours, border width, dashed, entrance effect (pop, jelly, shout shake, drop, slide, flip, instant), “word bounces while spoken”, text reveal (highlight word / type along / all at once), speaker name, “shape follows reaction”, live preview, “apply to all figures”. Fonts come from the device (no downloads).
* **Women’s figures revised**: hair falls as two locks with a free neck (no more “beard” look), ears hidden under long hair and otherwise small and lower, rounded sideburns instead of pointed hair ends, narrower shoulders and a waist.
* **Figure style**: per figure standard, outlined, cartoon (outline + bigger head) or chibi (huge head).
* **German and English**: UI via the **DE | EN** switch; the **language of each figure** (spoken text, voice choice, mouth shapes) is set independently – mixed-language dialogues work.
* **Targets for walking & pointing**: a “walk” pose clip gets a destination via “👣 Target”, a “point” clip gets a spot or an object on the stage via “👉 Target” (tap/click; Esc cancels). Targets show as draggable pins with a path line; the figure really walks there (turning to profile) and the arm points exactly at the target.
* **Narrator (voice-over)**: its own speaker track without a figure (＋ Narrator) with its own voice, timeline row and a subtitle bar at the bottom; sound and bubble are separately switchable (bubble only, sound only or both).
* **Texts, voices and recordings per language**: every speech line (and the narrator) keeps text, voice and recording separately for **German and English**. Chips “DE ✓ 🎵 / EN ⚠” show what exists or is not yet translated; “Set all speakers to German/English” switches the whole project.
* **Recording & transcribing**: “🎙 Record” records the voice in the browser (separately per language); if the browser supports speech recognition a **transcript** is created that can be taken over as speech text/bubble and edited. “📝 Dictate” only enters the text. Recordings from the **iOS Voice Memos** app (or any recorder) can be loaded as an audio file per line and language; type or dictate the matching text as the transcript.
* **Own background image**: upload a photo/graphic (JPG, PNG, HEIC …; downscaled to ≤1920 px), mode “fill” or “fit”, darken and blur.
* **Voice sources**: browser/OS voices, your own **audio file** per line, or **your own TTS server** (e.g. Piper) → [docs/VOICES.md](docs/VOICES.md)
* **Background music**: four synth styles (WebAudio, no download) **or your own files** (MP3, M4A, WAV, OGG, MP4 with an audio track) per scene – with volume, loop and automatic ducking while someone speaks. Loaded files only live for the current session (they are not stored in the page).
* **Motion**: sine-based walk cycle with foot lift and torso bob, overlapping head movement, smooth pose transitions (wave → rest glides instead of snapping), breathing, blinking, glances, gestures while speaking.
* **Backgrounds** in cartoon style with outlines, gradients and gentle motion (clouds, bunting, clock hands, lamps, plants, balloons); plus eight plain backgrounds.
* **Mobile-friendly** (iPhone/Android): touch controls, fixed 960×540 stage scaled to fit.

## About the voices

Out of the box the tool uses your browser/OS voices – quality depends on the device (Edge “Natural”, Apple “Premium” are good). For better voices use your own audio file or a local TTS server. **No voice models are included in the repository**; which ones are free to use, with sources, is in [docs/VOICES.md](docs/VOICES.md).

## Tests

Playwright browser tests (rig, editing, playback, lip sync, mobile, robustness, German/English, audio sources, targets, recording/narrator):

```bash
pip install -r tests/requirements.txt && python -m playwright install chromium
tests/run_all.sh          # optional: CHROME_PATH=/path/to/chrome
```

## Status / limits

* MP4 export and embed code are placeholders (export is meant to render server-side later).
* No saving/loading of projects yet (recordings and background images only live for the current session); per-line audio files only live for the current session.
* Transcription: the browser cannot turn uploaded files into text, only live while recording/dictating (depends on the browser; iOS Safari does not always record and recognise at once) – otherwise type the text.
* Browser speech synthesis cannot speak several voices in parallel – overlapping lines are spoken one after another.
* Code licence: not decided yet (without a licence file the default legal rights apply).
