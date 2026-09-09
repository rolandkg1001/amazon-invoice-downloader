# Marktposition TimeInvoicer — wöchentlicher Lauf

Jede Woche ein Bericht, der sich mit dem der Vorwoche vergleichen lässt. Der Wert liegt nicht im
einzelnen Bericht, sondern in der Reihe: Preisbewegungen der Konkurrenz, neue Anbieter, Store-Zahlen
und die Frage, ob TimeInvoicer endlich in den Vergleichsartikeln auftaucht.

## Ablauf

```bash
python3 marktposition/snapshot.py --diff
```

Das schreibt `data/snapshot-YYYY-MM-DD.json`, gibt eine Kurzfassung aus und listet jede Abweichung
zum letzten Snapshot. Danach wird der Bericht `MARKTPOSITION_YYYY-MM-DD.md` daraus geschrieben.

Ein Lauf ist rein lesend — nur öffentliche Seiten, keine Logins, keine Konten.

## Was der Snapshot automatisch erhebt

| Block | Inhalt | Warum |
|---|---|---|
| `play_store` | Downloads, Bewertungen, Stand, Titel | einzige öffentliche Wachstumszahl |
| `app_store` | Version, Bewertungen, IAP-Preise | Preis, wie ihn der Käufer sieht |
| `own_price_surfaces` | alle Preise auf .at / .com / .ch | Preis-Kohärenz über alle Kaufflächen |
| `category_visibility` | steht „TimeInvoicer" in den Vergleichsartikeln? | die Kernfrage der Marktposition |
| `competitors` | Preisseiten von 6 Wettbewerbern | Preisbewegungen im Feld |

Die Preisliste speichert jeweils **Betrag plus Textumgebung** (`"99 EUR — Gründerpreis: 99 € im 1.
Jahr"`). Ohne Kontext ist ein Betrag nicht auswertbar und der Wochenvergleich rauscht.

## Was Handarbeit bleibt

Diese Quellen sind nicht öffentlich und müssen pro Lauf ergänzt werden — ohne sie ist der Bericht
unvollständig, aber nicht falsch:

- **Google Ads** — Kosten, Klicks, Conversions nach Conversion-Aktion.
  Seit 28.08.2026 liegt Basic Access für die Ads API vor (15.000 Operations/Tag). Sobald
  Developer-Token, OAuth-Client und Refresh-Token verfügbar sind, gehört dieser Block in
  `snapshot.py`.
- **Play Console** — Geräteimpressionen, Akquisitionen, Store-Conversion-Rate, aktive Geräte.
- **App Store Connect** — Impressionen, Downloads, Abo-Status.
- **GA4** — Sitzungen und Ereignisse auf .at / .com / .ch.

Die zuletzt bekannten Werte dieser vier Quellen stehen im jeweils letzten Bericht und in
`clientmanager/marketing/google-ads/timeinvoicer-daily-audit-*.md`.

## Aufbau eines Berichts

1. **Gesamturteil** — ein Absatz, der die Position benennt, nicht die Aktivität
2. **Kategorie-Sichtbarkeit** — wer definiert die Kategorie, kommt TimeInvoicer darin vor
3. **Wettbewerbsfeld** — Tabelle mit Preis/Plattform, neue Anbieter markiert
4. **Preis-Positionierung** — eigene Preise gegen das Feld, plus Kohärenz über alle Kaufflächen
5. **Store-Realität** — Downloads, Bewertungen, Conversion
6. **Entscheidungen** — höchstens fünf, jede umsetzbar
7. **Beobachtungsliste** — was nächste Woche zu prüfen ist

## Regeln

- Zahlen, die nicht aus einer geprüften Quelle stammen, werden als Schätzung gekennzeichnet.
- Ein Bericht behauptet nie einen Live-Store-Stand, der nicht in diesem Lauf abgerufen wurde.
- Die Entscheidungsliste wird nicht länger als fünf Punkte. Was nicht in fünf passt, ist keine
  Entscheidung, sondern eine Sammlung.

## Artifact

Der Bericht wird zusätzlich als Artifact veröffentlicht — eine stabile URL, die jede Woche
überschrieben wird, damit sich Lesezeichen und geteilte Links nicht ändern:

**https://claude.ai/code/artifact/edba7218-504e-4a68-87eb-9fcf01aac858**

`report.html` ist die zuletzt veröffentlichte Fassung und dient dem nächsten Lauf als Vorlage:
Inhalte ersetzen, Struktur und Gestaltung behalten, dann mit `url:` auf dieselbe Adresse
republishen. Ohne `url:` entsteht ein zweites Artifact statt einer neuen Version.
