# Play vs. Apple — was übernommen wurde

Stand der Erhebung: 2026-08-05. Quellen sind die öffentlichen Listings:
Play `at.insglueck.timeinvoicer`, App Store `id6761268235` (beide dieselbe Bundle-ID).

## Ausgangslage

|                     | Google Play                        | App Store (vorher)              |
|---------------------|------------------------------------|---------------------------------|
| Name                | TimeInvoicer Praxissoftware (27)   | TimeInvoicer (12)               |
| Kurzbeschreibung    | 68 Zeichen, keyword-dicht          | Untertitel ungenutzt            |
| Beschreibung        | 3.585 Zeichen, 10 Feature-Blöcke   | 2.181 Zeichen, Umlaute als `ae`/`ue` |
| Screenshots         | 4 Phone mit Overlay + 2 Querformat | 10 iPhone + 10 iPad, ohne Overlay |
| Disclaimer          | vorhanden                          | **fehlte**                      |

Der Befund war also nicht einseitig: Play hatte die **besseren Texte und das
bessere Screenshot-Design**, Apple die **umfangreichere Screenshot-Abdeckung**
(10 statt 4 Screens, inkl. Kassenanträge, Zeitbestätigung, Mitschrift, iPad).

Deshalb wurde nicht das Play-Listing kopiert, sondern gezielt zusammengeführt:
Play-Texte und Play-Bildsprache auf Apples vollständigeren Screen-Satz.

## Texte

**Übernommen aus Play:**

- Name `TimeInvoicer Praxissoftware` — nutzt 27 statt 12 der 30 Zeichen und
  bringt „Praxissoftware" in den Suchindex.
- Der komplette Feature-Kanon, der bei Apple fehlte: ICD-10-Codeverzeichnis,
  Kassenantrag, Zeitbestätigungen, Sammelrechnungen, halbe Einheiten (0,5 / 1,5 / 2,5),
  EPC-QR-Code, ELDA-WAH-XML-Export, CSV-Steuerexport für BMD/RZL/DATEV,
  PDF-Honorarnote mit Logo und Signatur.
- Die Play-Abschnitte „Kalender statt doppelter Eingabe", „Mitschrift direkt zur
  Stunde", „Datenschutz und Kontrolle", „Typische Anwendungsfälle", „Geeignet für".

**Aus dem Apple-Text behalten:**

- Der wärmere Ton und die Abschnitte „Sammelrechnung in Sekunden",
  „Statistik und Überblick", „Gratis starten", „Made in Austria".
- Preisangabe (3 Klient:innen gratis, Pro ab 4,99 €/Monat) und die
  Rechtliches-Links inklusive Apple-Standard-EULA — die braucht das
  Apple-Listing, Play kennt sie nicht.

**Neu, weil beide Listings es nicht hatten:**

- Untertitel `Honorarnoten aus dem Kalender` (29/30). Der war leer; Apple
  indexiert ihn wie den Namen.
- Keywords (95/100). Play hat kein Keyword-Feld — abgeleitet aus dem Play-Text.
- Werbetext (164/170), ohne Review änderbar.

**Korrigiert:** Der bisherige Apple-Text schrieb Umlaute als `ae`/`oe`/`ue`
(„Geraet", „Betraege", „oesterreichische"). Die neue Fassung nutzt echte
Umlaute — App Store Connect ist UTF-8, die Umschreibung kostet nur Lesbarkeit
und Keyword-Treffer.

## Screenshots

Overlay-Design 1:1 aus Play übernommen (Farben und Maße siehe README).
Der App-Inhalt stammt aus den bestehenden **iOS**-Screenshots, nicht aus den
Android-Bildern — Begründung im README.

Kopfzeilen, die wörtlich aus Play stammen (in der Config als `"source": "play"`
markiert):

| Screen | Headline                 | Subline                             |
|--------|--------------------------|-------------------------------------|
| 02     | Aus Termin wird Rechnung | Für Praxen, Beratung und EPU        |
| 03     | PDF fertig senden        | Weniger Verwaltung nach dem Termin  |
| 04     | Kontakt & Leistung       | Alles Wichtige an einem Ort         |
| 06     | Schneller abrechnen      | Vorlagen, Codes und offene Beträge  |

Ebenfalls aus Play: die Bandüberschrift „Was TimeInvoicer anders macht", die
Tagline „Kein PC. Keine Cloud-Pflicht. Lokal auf deinem Gerät." und die
Benefit-Chips dieser vier Screens.

Für die sechs Screens ohne Play-Vorlage (01, 05, 07–10 iPhone; 04–06 iPad)
wurden Headline, Subline und Chips im selben Duktus ergänzt.

Die Chips von Screen 04 und 06 laufen auf zwei Zeilen um. Bei 06 ist das auch im
Play-Original so; bei 04 liegt es daran, dass Inter etwas breiter läuft als das
Roboto der Play-Grafiken. Chip-Padding und -Abstand sind dafür bereits von
26 u/18 u auf 21 u/15 u reduziert.

## Compliance-Befunde

Geprüft gegen den Skill `timeinvoicer-playstore-compliance` (Anlass: Rollback
durch Google Play am 23.04.2026 wegen inkohärenter Health-Deklaration).

**1 — Pflicht-Disclaimer fehlte bei Apple.** Der Skill verlangt ihn im ersten
Absatz der Store-Beschreibung. Im bisherigen Apple-Text stand er nirgends. Er
ist jetzt der erste Absatz von `description.txt`, im vorgegebenen Wortlaut.
Apple hat deswegen bisher nichts beanstandet — die Kohärenz-Logik, die bei Play
zum Rollback führte, greift hier aber genauso, sobald ICD-10 und
Therapie-Zielgruppe im Text stehen.

**2 — „Vorschläge" beim ICD-10-Katalog nicht übernommen.** Play formuliert
„ICD-10-F Katalog mit Suche, Favoriten und Vorschlaegen". Ein System, das
ICD-Codes *vorschlägt*, ist klinische Entscheidungsunterstützung — laut Skill
ein harter Trigger. Im Apple-Text steht deshalb „ICD-10-Codeverzeichnis mit
Suche und Favoriten" und an anderer Stelle „ICD-10-Abrechnungscodes zur
eigenständigen Auswahl".

**3 — Leistungserkennung mit Klarstellung.** Der bisherige Apple-Text bewarb
„KI-GESTUETZTE LEISTUNGSERKENNUNG". Die Wortwahl „Leistung wird automatisch
erkannt" ist laut Wörterbuch erlaubt (im Gegensatz zu „Diagnose wird erkannt").
Der Abschnitt ist erhalten, ergänzt um den Satz, dass keine Auswertung
medizinischer Inhalte stattfindet, sondern eine Zuordnung zu eigenen Tarifen.

**4 — „Befunde" vermieden.** Der zehnte Screenshot heißt in der Quelldatei
`10-befunde.png`. Das Wörterbuch führt „Befund erstellen" → „Dokument erstellen",
prominente Befund-Features gelten als Grauzone. Overlay-Headline ist deshalb
„Dokumente & Vorlagen". In der Beschreibung kommt „Befund" nicht vor.

**5 — Drei Play-Bilder sind selbst compliance-kritisch (offener Punkt, betrifft
Play).** Beim Sichten des Play-Materials sind drei Bilder aufgefallen, die die
Screenshot-Checkliste des Skills verletzen. Keines davon wurde nach Apple
übernommen — **im Play-Listing stehen sie aber weiterhin**, und das sind genau
die Signale, die im April zum Rollback beigetragen haben:

| Bild | Größe | Problem |
|------|-------|---------|
| Querformat 1 | 1672 × 941 | Rechnungsvorschau mit klinischem Fließtext: *„… ist bei mir in psychotherapeutischer **Behandlung** und zeigt folgende **Symptomatik**: Rezidivierende depressive Stoerung, gegenwaertig remittiert (ICD10: F33.4)"* |
| Querformat 2 | 1024 × 500 | **„Befund"** als prominentes Feature-Label in der Funktionsliste; im Telefon-Mockup „ICD-10 Diagnose hinzufügen" |
| Phone 4 | 1080 × 1920 | „ICD-10 Diagnose" und „ICD-10 Diagnose hinzufügen" im App-UI |

Die Checkliste sagt dazu wörtlich: *„OCR-Check: Sind 'Diagnose', 'Symptom',
'Krankheit', 'erkrankt', 'wieder gesund', 'Behandlung' prominent zu sehen? →
Bild austauschen."* und *„Steht 'ICD-10 Diagnose' im Bild? → zu 'ICD-10
Abrechnungscode' ändern."*

Das erste Bild ist der kritischste Fall: Es zeigt eine ausformulierte Diagnose
samt ICD-Code als Beispielinhalt. Empfehlung, nach Dringlichkeit:

1. Querformat 1 sofort aus dem Play-Listing entfernen oder durch eine
   Rechnungsvorschau ohne klinischen Text ersetzen.
2. In-App-Label „ICD-10 Diagnose" → „ICD-10 Abrechnungscode" ändern, danach
   Querformat 2 und Phone 4 neu aufnehmen.
3. „Befund" in der Feature-Liste durch „Dokument" ersetzen.

Nebenbefund: Beide Querformat-Bilder zeigen echte Kontaktdaten
(Briefkopf mit Adresse und Telefonnummer, eine Mobilnummer im Terminblatt, ein
Kalendername `Klienten_Nextcloud_2025_09-21`). Für die Neuaufnahme wären
durchgängige Musterdaten sauberer.

## Nicht übernommen

- **Feature Graphic** (1024 × 500) — reines Play-Format, App Store kennt es nicht.
- **App-Vorschauvideos** — in keinem der beiden Listings vorhanden.
- **Weitere Sprachen.** Das Apple-Listing hat aktuell nur eine Lokalisierung
  (Deutsch, wird in allen Storefronts ausgeliefert), obwohl die App laut
  Store-Metadaten EN, FR, IT und ES mitbringt. Eine englische Lokalisierung wäre
  der nächste sinnvolle Schritt; die Disclaimer-Bausteine für EN, FR und IT
  stehen im Compliance-Skill bereit. Bewusst nicht mitgeliefert, weil eine
  ungeprüfte Übersetzung bei einem compliance-sensiblen Listing mehr Risiko als
  Nutzen bringt.
