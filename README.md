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
* **Figur antippen**: Jede Figur zeigt im Bearbeiten-Modus drei Symbole – 🎙 Einsprechen, 💬 Text/Stimme/Sprache, ⚙ Konfiguration (Zustand, Reaktion, Blickrichtung, Figurenstil …) als Popover (auf dem Handy als Bottom-Sheet). Schalter **✎ Bearbeiten | 👁 Vorschau** blendet alle Bearbeitungs-Symbole aus.
* **Größe, Duplizieren, Löschen**: Figuren und Objekte mit ＋/－ (oder Tasten +/−) oder Ziehpunkt (Seitenverhältnis bleibt, Text skaliert die Schrift mit); ⧉ dupliziert Figur/Objekt, **Szene duplizieren** kopiert alles (Objekte, Figuren, Texte in DE+EN, Ziele, Kamera). „Person löschen“ entfernt Figur samt Sprecherzeile und Text; neue Figuren bekommen sofort ihre Sprecher-Vorgaben.
* **Szenen direkt am Filmstreifen**: pro Szene Symbole ◂+ / +▸ (leere neutrale Szene davor/danach einfügen), ⧉ (Szene mit allem kopieren), 🗑 (löschen, mit Rückfrage wenn Inhalt vorhanden; die letzte Szene bleibt); „+“ am Ende hängt eine leere Szene an. Alles per Rückgängig umkehrbar.
* **Szenen einzeln oder als Auswahl abspielen/exportieren**: ▶ an jeder Szene spielt nur diese Szene; mit dem Häkchen oben links wählen Sie beliebige Szenen aus – „▶ Auswahl“ spielt nur diese (Pause/Weiter und Zeitleiste inklusive), und der Export hat den Umfang „Auswahl“ (Untertitel passend dazu).
* **✂ Leerraum entfernen**: Analyse je Szene (Länge, Sprechzeit, Leerlauf) und Vorschau der Zeitersparnis; kürzt lange Pausen zwischen Sprechern, Stille am Anfang/Ende und Szenen ohne Sprache. Posen, Gehwege, Kamera und Objekte wandern mit, überlappende Sprecher bleiben überlappend, alles per Strg+Z umkehrbar.
* **Beispielabläufe (Vorlagen, je 4 Szenen)**: „Software erklärt: Online-Werbung bestellen“ und „Tickets für eine Veranstaltung bestellen“ – mit Bildschirm-Mockups (neue Kategorie „Bildschirm“ in den Objekten), Beraterin und Kunde im Dialog, Mauszeiger und Klick-Markierungen, Texte in Deutsch und Englisch.
* **Mehrere Formate in einem Durchlauf**: Beim Export lässt sich zusätzlich zum Hauptformat (MP4/WebM) ein zweites Format oder nur der Ton (M4A/WebM) im selben Durchlauf speichern.
* **Automatische Übersetzung & weitere Sprachen**: 🌐 „Übersetzen“ je Sprechzeile übersetzt den Text (auch Diktat/Transkript einer Aufnahme) in alle Projektsprachen; mit „Automatisch übersetzen“ geschieht das nach jeder Änderung von selbst. Von Hand geschriebene Texte anderer Sprachen werden nie ohne Rückfrage überschrieben, eigene Korrekturen an einer Übersetzung bleiben geschützt (Chip 🌐 = maschinell übersetzt). „＋ Sprache“ fügt weitere Sprachen hinzu (Spanisch, Französisch, Italienisch, Portugiesisch, Niederländisch, Polnisch, Türkisch, Schwedisch, Dänisch, Tschechisch, Russisch, Ukrainisch, Arabisch, Hindi, Chinesisch, Japanisch, Koreanisch) – mit eigener Stimme/Aufnahme je Sprache, Lippenbewegung und SRT/VTT-Untertiteln. Engine unter „Stimmen“: Browser-Übersetzer (Chrome, lokal) → eigener LibreTranslate-Server → kostenloses MyMemory (Text geht an den Dienst, Tageskontingent begrenzt).
* **Projekt speichern/laden** (`.stagehand.json`, mit Aufnahmen, Bildern und Musik eingebettet), Autosave (ohne Medien) und **Rückgängig/Wiederholen** (Strg+Z / Strg+Umschalt+Z).
* **Export**: Dialog mit Format (**MP4 H.264**, WebM VP9/VP8, je nach Browser), Auflösung (480p – Full HD), Bildrate, **Qualität/Kompression** (mit Größenschätzung), Umfang (alles/Szene) und Ton; dazu **Untertitel SRT/VTT** in Deutsch und Englisch. Die Aufnahme läuft in Echtzeit über die Tab-Freigabe von Chrome/Edge (Bühne exakt zugeschnitten). Ton: eigener Mix (Musik, Audiodateien, Aufnahmen, TTS-Server) oder Tab-Audio (nötig für Browserstimmen). „Vollbild abspielen“ ist für die Bildschirmaufnahme am iPhone gedacht.
* **Wiedergabe-Steuerung**: Pause/Weiter, Klick ins Lineal = ab dort abspielen (Szene und Gesamtfilm), **⏱ Zeiten automatisch** (Sprecher nacheinander, Szenenlänge angepasst).
* **Kamera**: Zoom/Schwenk auf eine Figur oder zurück zum Gesamtbild als Clips in der Timeline (4 Zoomstufen).
* **Mehr Posen und Vorlagen**: Nicken, Schulterzucken; Vorlagen „Problem → Lösung → Aufruf“ und „In drei Schritten erklärt“ (Texte in DE+EN).
* **Stimmquellen**: Browser-/Systemstimmen, eigene **Audiodatei** pro Zeile oder ein **eigener TTS-Server** (z. B. Piper) → [docs/VOICES.md](docs/VOICES.md)
* **Hintergrundmusik**: vier Synth-Stile (WebAudio, kein Download) **oder eigene Dateien** (MP3, M4A, WAV, OGG, MP4 mit Tonspur) pro Szene – mit Lautstärke, Schleife und automatischer Absenkung beim Sprechen. Geladene Dateien gelten nur für die laufende Sitzung (sie werden nicht in der Seite gespeichert).
* **Bewegung**: sinusförmiger Gehzyklus mit Fußhub und Rumpf-Wippen, überlappende Kopfbewegung, weiche Posenübergänge (Winken → Ruhe gleitet statt zu springen), Atmen, Blinzeln, Blickwechsel, Gestik beim Sprechen.
* **Hintergründe** im Cartoon-Stil mit Konturen, Verläufen und sanfter Bewegung (Wolken, Fahnen, Uhrzeiger, Lampen, Pflanzen, Ballons); dazu acht einfarbige Hintergründe.
* **Handy-tauglich** (iPhone/Android): Touch-Bedienung, feste Bühne 960×540 skaliert.

## Hinweise zu den Stimmen

Ohne Einrichtung nutzt das Tool die Stimmen des Browsers/Betriebssystems – die Qualität hängt vom Gerät ab (Edge „Natural“, Apple „Premium“ sind gut). Bessere Stimmen: eigene Audiodatei oder lokaler TTS-Server. **Es sind keine Stimmmodelle im Repository**; welche frei nutzbar sind, steht mit Quellen in [docs/VOICES.md](docs/VOICES.md).

## Tests

Browser-Tests mit Playwright (Rig, Bearbeiten, Wiedergabe, Lippen-Sync, Handy, Robustheit, Deutsch/Englisch, Audio-Quellen, Ziele, Aufnahme/Erzähler, Projekt, Overlay, Export, Wiedergabe/Kamera):

```bash
pip install -r tests/requirements.txt && python -m playwright install chromium
tests/run_all.sh          # optional: CHROME_PATH=/pfad/zu/chrome
```

## Stand / Grenzen

* Embed-Code ist ein Platzhalter. Der Videoexport nimmt in Echtzeit auf (Chrome/Edge am Computer); auf iPhone/iPad-Safari gibt es keine Seitenaufnahme – dort „Vollbild abspielen“ + iOS-Bildschirmaufnahme. Browserstimmen kommen nur über Tab-Audio ins Video (im Freigabe-Fenster „Tab-Audio teilen“).
* Projekte lassen sich als Datei speichern; Autosave im Browser enthält keine Aufnahmen/Musik. Große Projekte mit vielen Aufnahmen werden entsprechend groß.
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
* **Tap a figure**: in edit mode every figure shows three icons – 🎙 record, 💬 text/voice/language, ⚙ configuration (state, reaction, facing, figure style …) as a popover (bottom sheet on phones). The **✎ Edit | 👁 Preview** switch hides all editing overlays.
* **Resize, duplicate, delete**: figures and objects with ＋/－ (or the +/− keys) or the drag handle (aspect ratio kept, text scales its font); ⧉ duplicates a figure/object, **duplicate scene** copies everything (objects, figures, texts in DE+EN, targets, camera). “Delete person” removes the figure with its speaker row and text; new figures immediately get their speaker settings.
* **Scene icons on the film strip**: per scene ◂+ / +▸ (insert an empty neutral scene before/after), ⧉ (copy the scene with everything), 🗑 (delete, with confirmation if it has content; the last scene stays); “+” at the end appends an empty scene. All undoable.
* **Play/export scenes individually or as a selection**: ▶ on each scene plays only that scene; the checkbox at the top left selects any scenes – “▶ Selection” plays just those (pause/resume and timeline included), and the export has the scope “Selection” (subtitles match).
* **✂ Remove dead air**: analysis per scene (length, speech time, idle) and a preview of the time saved; shortens long pauses between speakers, silence at the start/end and scenes without speech. Poses, walks, camera and objects move along, overlapping speakers stay overlapping, everything is undoable with Ctrl+Z.
* **Example flows (templates, 4 scenes each)**: “Software explained: ordering online ads” and “Ordering tickets for an event” – with screen mockups (new object category “Screen”), advisor and customer in dialogue, mouse pointer and click markers, texts in German and English.
* **Several formats in one run**: besides the main format (MP4/WebM) the export can also save a second format or just the audio (M4A/WebM) in the same run.
* **Automatic translation & more languages**: 🌐 “Translate” per speaker line translates the text (also the dictated transcript of a recording) into all project languages; “Auto-translate” does it by itself after every change. Texts you wrote by hand in other languages are never overwritten without asking, and your own corrections to a translation stay protected (chip 🌐 = machine-translated). “＋ Language” adds more languages (Spanish, French, Italian, Portuguese, Dutch, Polish, Turkish, Swedish, Danish, Czech, Russian, Ukrainian, Arabic, Hindi, Chinese, Japanese, Korean) – each with its own voice/recording, lip movement and SRT/VTT subtitles. Engine under “Voices”: browser translator (Chrome, on-device) → your own LibreTranslate server → free MyMemory (text is sent to that service, limited daily quota).
* **Save/load project** (`.stagehand.json`, recordings, images and music embedded), autosave (without media) and **undo/redo** (Ctrl+Z / Ctrl+Shift+Z).
* **Export**: dialog with format (**MP4 H.264**, WebM VP9/VP8, depending on the browser), resolution (480p – Full HD), frame rate, **quality/compression** (with size estimate), scope (all/scene) and sound; plus **SRT/VTT subtitles** in German and English. Recording runs in real time via Chrome/Edge tab sharing (stage cropped exactly). Sound: own mix (music, audio files, recordings, TTS server) or tab audio (needed for browser voices). “Play fullscreen” is meant for the iPhone’s screen recording.
* **Playback control**: pause/resume, click the ruler = play from there (scene and whole film), **⏱ auto timing** (speakers one after another, scene length adjusted).
* **Camera**: zoom/pan to a figure or back to the wide shot as timeline clips (4 zoom levels).
* **More poses and templates**: nodding, shrugging; templates “Problem → solution → call to action” and “Explained in three steps” (texts in DE+EN).
* **Voice sources**: browser/OS voices, your own **audio file** per line, or **your own TTS server** (e.g. Piper) → [docs/VOICES.md](docs/VOICES.md)
* **Background music**: four synth styles (WebAudio, no download) **or your own files** (MP3, M4A, WAV, OGG, MP4 with an audio track) per scene – with volume, loop and automatic ducking while someone speaks. Loaded files only live for the current session (they are not stored in the page).
* **Motion**: sine-based walk cycle with foot lift and torso bob, overlapping head movement, smooth pose transitions (wave → rest glides instead of snapping), breathing, blinking, glances, gestures while speaking.
* **Backgrounds** in cartoon style with outlines, gradients and gentle motion (clouds, bunting, clock hands, lamps, plants, balloons); plus eight plain backgrounds.
* **Mobile-friendly** (iPhone/Android): touch controls, fixed 960×540 stage scaled to fit.

## About the voices

Out of the box the tool uses your browser/OS voices – quality depends on the device (Edge “Natural”, Apple “Premium” are good). For better voices use your own audio file or a local TTS server. **No voice models are included in the repository**; which ones are free to use, with sources, is in [docs/VOICES.md](docs/VOICES.md).

## Tests

Playwright browser tests (rig, editing, playback, lip sync, mobile, robustness, German/English, audio sources, targets, recording/narrator, project, overlay, export, playback/camera):

```bash
pip install -r tests/requirements.txt && python -m playwright install chromium
tests/run_all.sh          # optional: CHROME_PATH=/path/to/chrome
```

## Status / limits

* Embed code is a placeholder. Video export records in real time (Chrome/Edge on a computer); iPhone/iPad Safari cannot record the page – use “Play fullscreen” + iOS screen recording there. Browser voices only reach the video via tab audio (tick “Share tab audio” in the share window).
* Projects can be saved as a file; the browser autosave contains no recordings/music. Large projects with many recordings get large.
* Transcription: the browser cannot turn uploaded files into text, only live while recording/dictating (depends on the browser; iOS Safari does not always record and recognise at once) – otherwise type the text.
* Browser speech synthesis cannot speak several voices in parallel – overlapping lines are spoken one after another.
* Code licence: not decided yet (without a licence file the default legal rights apply).
