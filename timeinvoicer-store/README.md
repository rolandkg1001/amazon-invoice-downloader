# TimeInvoicer — Play-Listing nach App Store Connect übertragen

Upload-fertiges Paket für **App Store Connect**, Inhalte übernommen aus dem
Google-Play-Listing von `at.insglueck.timeinvoicer`.

> **Hinweis zum Ablageort:** Diese Dateien gehören inhaltlich zur TimeInvoicer-App,
> liegen aber in diesem Repo, weil die Aufgabe auf diesen Branch geroutet wurde.
> Beim Übernehmen am besten nach `fastlane/` im TimeInvoicer-Repo verschieben —
> der Ordner `metadata/` folgt bereits dem fastlane-`deliver`-Schema.

## Was drin ist

```
metadata/de-DE/     Texte für App Store Connect (fastlane-deliver-Layout)
screenshots/        30 fertige Screenshots (iPhone 6.9" + 6.5", iPad 13")
assets/screens/     freigestellte iOS-App-Screens (Quellmaterial)
tools/              Generator + Overlay-Konfiguration + Inter-Fonts
```

## Warum die Screenshots so gebaut sind

Die Play-Screenshots sehen besser aus, weil sie ein **Overlay-System** haben,
das dem Apple-Listing fehlt: Verlaufsband oben mit fetter Headline und goldener
Subline, unten ein dunkles Band mit Benefit-Chips und Tagline. Der App-Inhalt
füllt dabei die volle Breite, statt als kleines Gerät-Mockup in viel leerem
Hintergrund zu schweben.

**Die Android-Bilder wurden nicht einfach hochskaliert.** Das wäre ein
Rejection-Risiko (Guideline 2.3.3: Screenshots müssen die App auf dem jeweiligen
Gerät zeigen — Material-Design-UI und Android-Statusbar im iOS-Listing fallen auf).
Stattdessen:

1. Aus den **bestehenden Apple-Screenshots** wurde der iOS-App-Screen
   freigestellt (`assets/screens/`, exakter Bildausschnitt des Geräte-Mockups).
2. Darüber liegt das **Play-Overlay**, pixelvermessen aus dem Play-Listing
   übernommen — Farben, Bandhöhen, Schriftgrade und Chip-Geometrie stehen in
   `tools/screenshots.config.json` unter `design`.

Ergebnis: echte iOS-Oberfläche mit iOS-Statusbar und Dynamic Island, in der
Play-Bildsprache.

Übernommene Farben (gemessen an `play_03.png` @ 1080×1920):

| Element        | Wert                          |
|----------------|-------------------------------|
| Kopfband       | Verlauf `#004E44` → `#007667` |
| Headline       | `#FFFFFF`, 66 u, Weight 800   |
| Subline        | `#FFCC50`, 34 u               |
| Fußband        | `#003A34`, Höhe 300 u         |
| Chips          | Weiß auf `#003A34`, 57 u hoch |

`u` = Play-Unit: Das Design ist auf 1080 px Breite vermessen, alle Maße skalieren
mit `Zielbreite / 1080 × scale`.

## Screenshots neu bauen

```bash
python3 tools/build_screenshots.py                  # alle 3 Zielgrößen
python3 tools/build_screenshots.py --target ipad-13
python3 tools/build_screenshots.py --only 01,03     # einzelne Screens
```

Voraussetzung: Python 3 mit **Pillow** und ein Chromium. Das Skript findet
Chromium selbst; gerendert wird bevorzugt mit `headless_shell`, weil
`chrome --headless` den Layout-Viewport rund 87 px niedriger anlegt als
`--window-size` verlangt und dadurch das Fußband abschneidet.

Texte, Chips und Bildausschnitt ändert man in `tools/screenshots.config.json` —
kein Code-Eingriff nötig. `focus` steuert pro Screen den Bildausschnitt
(`top` / `center` / `bottom`).

## Hochladen

**Texte** — App Store Connect → App → *Deutsch (Österreich)*:

| Feld                       | Datei                  | Länge   |
|----------------------------|------------------------|---------|
| Name                       | `name.txt`             | 27/30   |
| Untertitel                 | `subtitle.txt`         | 29/30   |
| Werbetext                  | `promotional_text.txt` | 164/170 |
| Beschreibung               | `description.txt`      | 3877/4000 |
| Keywords                   | `keywords.txt`         | 95/100  |
| Neue Funktionen            | `release_notes.txt`    | unverändert übernommen |

`release_notes.txt` enthält den **aktuell live stehenden** Text von Version 1.0.1
unverändert — damit ein `fastlane deliver` ihn nicht überschreibt. Bei einem
neuen Build hier den neuen Text eintragen.

**Screenshots** — pro Gerätegröße den passenden Ordner hochladen. Reihenfolge
ergibt sich aus dem Dateinamen (`01-…` bis `10-…`):

- `screenshots/iphone-6.9/` → iPhone 6,9" (1290 × 2796)
- `screenshots/iphone-6.5/` → iPhone 6,5" (1284 × 2778)
- `screenshots/ipad-13/` → iPad 13" (2064 × 2752)

Alle Bilder sind PNG ohne Alphakanal — App Store Connect lehnt Screenshots mit
Transparenz ab.

Mit fastlane:

```bash
fastlane deliver --skip_binary_upload --skip_app_version_update \
  --metadata_path metadata --screenshots_path screenshots
```

## Compliance

Alles gegen den Skill `timeinvoicer-playstore-compliance` geprüft. Details in
[PLAY-VS-APPLE.md](PLAY-VS-APPLE.md) unter „Compliance-Befunde". Kurzfassung:

- Der **Pflicht-Disclaimer fehlte im bisherigen Apple-Text** komplett. Er steht
  jetzt als erster Absatz in `description.txt`.
- „ICD-10-F Katalog … mit Vorschlägen" aus dem Play-Text wurde zu
  „ICD-10-Codeverzeichnis mit Suche und Favoriten" — ein vorschlagendes System
  wäre klinische Entscheidungsunterstützung.
- Screenshot 10 heißt im Overlay „Dokumente & Vorlagen" statt „Befunde".

⚠️ **Offener Punkt im Play-Listing, unabhängig von diesem Paket:** Drei
Play-Bilder verletzen die Screenshot-Checkliste des Skills — eines zeigt eine
ausformulierte Diagnose samt ICD-Code („Symptomatik: Rezidivierende depressive
Stoerung … ICD10: F33.4"), zwei zeigen „Befund" bzw. „ICD-10 Diagnose" als
Label. Nach Apple wurde keines davon übernommen, im Play-Listing stehen sie
weiter. Das ist dieselbe Signal-Inkohärenz, die im April 2026 zum Rollback
geführt hat.
