#!/usr/bin/env python3
"""Wochen-Snapshot fuer die TimeInvoicer-Marktpositionsanalyse.

Sammelt die Zahlen, die sich Woche fuer Woche vergleichen lassen muessen:

  1. Store-Kennzahlen  — Play Store und App Store (Downloads, Bewertungen, Version)
  2. Preis-Kohaerenz   — alle Preise auf timeinvoicer.at/.com/.ch plus App Store
  3. Kategorie-Sichtbarkeit — taucht "TimeInvoicer" in den Vergleichsartikeln
                              der Konkurrenz auf?
  4. Konkurrenz-Preise — Preisseiten der Wettbewerber

Schreibt data/snapshot-YYYY-MM-DD.json und gibt eine Kurzfassung auf stdout aus.
Ein Lauf ist rein lesend: keine Konten, keine Logins, nur oeffentliche Seiten.

Aufruf:
    python3 marktposition/snapshot.py
    python3 marktposition/snapshot.py --diff        # gegen letzten Snapshot
"""

from __future__ import annotations

import argparse
import datetime as dt
import html as html_mod
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
TIMEOUT = 45

PLAY_URL = "https://play.google.com/store/apps/details?id=at.insglueck.timeinvoicer&hl=de&gl=AT"
APPSTORE_URL = "https://apps.apple.com/at/app/timeinvoicer/id6761268235"

# Eigene Preisflaechen. Jede Zeile ist eine Kaufflaeche, die ein Interessent
# tatsaechlich zu sehen bekommt — Abweichungen zwischen ihnen sind der Befund.
OWN_PRICE_PAGES = {
    "at_preise": "https://timeinvoicer.at/preise.html",
    "at_start": "https://timeinvoicer.at/",
    "com_start": "https://timeinvoicer.com/",
    "ch_start": "https://timeinvoicer.ch/",
}

# Vergleichsartikel, die die Kategorie definieren. Wer hier fehlt, existiert
# fuer den suchenden Therapeuten nicht.
CATEGORY_ARTICLES = {
    "freudio_vergleich": "https://www.freudio.com/blog/praxissoftware-psychotherapie-oesterreich-die-10-anbieter-im-test-vergleich-2026",
    "theradocx_vergleich": "https://www.theradocx.at/blog/praxissoftware-psychotherapie-oesterreich-2026",
    "praxissoftware_psychotherapie_com": "https://praxissoftware-psychotherapie.com/",
}

COMPETITOR_PAGES = {
    "synaptos": "https://synaptos.at/preise/",
    "zeipsy": "https://zeipsy.com/",
    "appointmed": "https://www.appointmed.com/preise",
    "freudio": "https://www.freudio.com/preise",
    "theradocx": "https://www.theradocx.at/",
    "gethonorar": "https://gethonorar.app/pricing",
}

# Preise stehen auf den eigenen Seiten als "9,90 &euro;", auf fremden als "€"
# oder "EUR" — deshalb erst Entities aufloesen, dann matchen. Waehrungszeichen
# vor ODER nach der Zahl, weil beide Schreibweisen im Markt vorkommen.
PRICE_RE = re.compile(
    r"(?:(\d{1,4}(?:[.\s]\d{3})*(?:,\d{2})?)\s*(?:€|EUR|CHF)"
    r"|(?:€|EUR|CHF)\s*(\d{1,4}(?:[.\s]\d{3})*(?:,\d{2})?))"
)
DROP_RE = re.compile(r"<(script|style|noscript)[^>]*>.*?</\1>", re.S | re.I)


def fetch(url: str) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "de-AT,de;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        print(f"  ! {url} -> {exc}", file=sys.stderr)
        return None


def visible_text(html: str) -> str:
    """Nur Textknoten — Tags samt Attributen fliegen raus, damit CSS-Zahlen
    nicht als Preise durchgehen. Danach Entities aufloesen (&euro;, &auml;)."""
    html = DROP_RE.sub(" ", html)
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html_mod.unescape(text))


def prices_in(html: str, limit: int = 40) -> list[str]:
    """Preisangaben mit dem Text, in dem sie stehen.

    Der Kontext ist der eigentliche Wert: '9,90 EUR' allein sagt nichts,
    '9,90 EUR — Praxis Plus im 1. Jahr' laesst sich woechentlich vergleichen
    und trennt eigene Preise von Preisen in Vergleichstabellen.
    """
    text = visible_text(html)
    found: list[str] = []
    seen: set[str] = set()
    for m in PRICE_RE.finditer(text):
        value = (m.group(1) or m.group(2) or "").replace(" ", "").replace(".", "")
        if not value:
            continue
        context = text[max(0, m.start() - 45): m.end() + 25].strip()
        token = f"{value} EUR — {context}"
        key = f"{value}|{context}"
        if key in seen:
            continue
        seen.add(key)
        found.append(token)
        if len(found) >= limit:
            break
    return found


def play_metrics() -> dict:
    html = fetch(PLAY_URL)
    if not html:
        return {"error": "unreachable"}
    text = visible_text(html)
    out: dict = {"url": PLAY_URL}

    m = re.search(r"([\d.,]+\s*(?:Tsd\.|Mio\.)?\+?)\s*Downloads", text)
    out["downloads"] = m.group(1).strip() if m else None

    m = re.search(r'<div class="ClM7O">([^<]{1,20})</div>', html)
    if m and not out.get("downloads"):
        out["downloads"] = m.group(1).strip()

    m = re.search(r"Aktualisiert am\s*([\d.]{8,10})", text)
    out["last_update"] = m.group(1) if m else None

    m = re.search(r"([\d,]+)\s*<[^>]*>\s*(?:Sterne|star)", html)
    out["rating"] = m.group(1) if m else None

    m = re.search(r"([\d.]+)\s*Rezensionen", text)
    out["reviews"] = m.group(1) if m else "0"

    m = re.search(r'itemprop="name"[^>]*>([^<]+)<', html)
    out["title"] = m.group(1).strip() if m else None
    return out


def appstore_metrics() -> dict:
    html = fetch(APPSTORE_URL)
    if not html:
        return {"error": "unreachable"}
    text = visible_text(html)
    out: dict = {"url": APPSTORE_URL}

    m = re.search(r"Version\s*([\d.]+)", text)
    out["version"] = m.group(1) if m else None

    m = re.search(r"([\d,]+)\s*von\s*5", text)
    out["rating"] = m.group(1) if m else None

    m = re.search(r"([\d.,]+)\s*(?:Bewertungen|Ratings)", text)
    out["reviews"] = m.group(1) if m else "0"

    out["iap_prices"] = prices_in(html, limit=20)
    return out


def price_values(entries: list[str] | None) -> list[str]:
    """Nur die Betraege aus den 'Betrag — Kontext'-Eintraegen, sortiert."""
    if not entries:
        return []
    return sorted({e.split(" EUR — ", 1)[0] for e in entries})


def own_prices() -> dict:
    out = {}
    for name, url in OWN_PRICE_PAGES.items():
        html = fetch(url)
        out[name] = {"url": url, "prices": prices_in(html) if html else None}
    return out


def category_visibility() -> dict:
    out = {}
    for name, url in CATEGORY_ARTICLES.items():
        html = fetch(url)
        if html is None:
            out[name] = {"url": url, "listed": None}
            continue
        text = visible_text(html).lower()
        out[name] = {
            "url": url,
            "listed": "timeinvoicer" in text,
            "providers_hint": sorted(
                {
                    kw
                    for kw in (
                        "synaptos", "appointmed", "zeipsy", "treatsoft", "freudio",
                        "theradocx", "therapsy", "psido", "latido", "onono",
                        "via healthtech", "playnvoice", "gethonorar", "timeinvoicer",
                    )
                    if kw in text
                }
            ),
        }
    return out


def competitor_prices() -> dict:
    out = {}
    for name, url in COMPETITOR_PAGES.items():
        html = fetch(url)
        out[name] = {"url": url, "prices": prices_in(html, limit=25) if html else None}
    return out


def build() -> dict:
    print("Play Store ...")
    play = play_metrics()
    print("App Store ...")
    appstore = appstore_metrics()
    print("Eigene Preisflaechen ...")
    own = own_prices()
    print("Kategorie-Sichtbarkeit ...")
    visibility = category_visibility()
    print("Konkurrenz-Preise ...")
    competitors = competitor_prices()

    return {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "week": dt.date.today().isocalendar()[:2],
        "play_store": play,
        "app_store": appstore,
        "own_price_surfaces": own,
        "category_visibility": visibility,
        "competitors": competitors,
    }


def latest_snapshot(before: pathlib.Path | None = None) -> pathlib.Path | None:
    files = sorted(DATA.glob("snapshot-*.json"))
    if before is not None:
        files = [f for f in files if f != before]
    return files[-1] if files else None


def summarise(snap: dict) -> None:
    play = snap["play_store"]
    app = snap["app_store"]
    print("\n--- Kurzfassung ---")
    print(f"Play:  {play.get('downloads')} Downloads · {play.get('reviews')} Rezensionen · Stand {play.get('last_update')}")
    print(f"iOS:   v{app.get('version')} · {app.get('reviews')} Bewertungen")

    surfaces = {n: price_values(v["prices"]) for n, v in snap["own_price_surfaces"].items()}
    surfaces["app_store"] = price_values(app.get("iap_prices"))
    surfaces = {n: p for n, p in surfaces.items() if p}
    if len({tuple(v) for v in surfaces.values()}) > 1:
        print("Preise: ABWEICHUNG zwischen den Kaufflaechen:")
        for n, p in surfaces.items():
            print(f"        {n:12s} {', '.join(p)}")
    else:
        print("Preise: alle Kaufflaechen identisch")

    listed = {n: v["listed"] for n, v in snap["category_visibility"].items()}
    missing = [n for n, ok in listed.items() if ok is False]
    print(f"Sichtbarkeit: gelistet in {sum(1 for v in listed.values() if v)}/{len(listed)} Vergleichsartikeln")
    if missing:
        print(f"        fehlt in: {', '.join(missing)}")


def diff(old: dict, new: dict) -> None:
    print("\n--- Veraenderung zur Vorwoche ---")
    for path in (("play_store", "downloads"), ("play_store", "reviews"),
                 ("play_store", "last_update"), ("app_store", "version"),
                 ("app_store", "reviews")):
        a, b = old, new
        for key in path:
            a = (a or {}).get(key) if isinstance(a, dict) else None
            b = (b or {}).get(key) if isinstance(b, dict) else None
        if a != b:
            print(f"  {'.'.join(path)}: {a} -> {b}")

    for name in new.get("category_visibility", {}):
        was = old.get("category_visibility", {}).get(name, {}).get("listed")
        now = new["category_visibility"][name]["listed"]
        if was != now:
            print(f"  sichtbarkeit.{name}: {was} -> {now}")

    for name in new.get("own_price_surfaces", {}):
        was = old.get("own_price_surfaces", {}).get(name, {}).get("prices")
        now = new["own_price_surfaces"][name]["prices"]
        if was != now:
            print(f"  preise.{name}: {was} -> {now}")

    for name in new.get("competitors", {}):
        was = old.get("competitors", {}).get(name, {}).get("prices")
        now = new["competitors"][name]["prices"]
        if was != now:
            print(f"  konkurrenz.{name}: {was} -> {now}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--diff", action="store_true", help="gegen den letzten Snapshot vergleichen")
    args = parser.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    previous = latest_snapshot()

    snap = build()
    target = DATA / f"snapshot-{dt.date.today().isoformat()}.json"
    target.write_text(json.dumps(snap, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\ngeschrieben: {target.relative_to(HERE.parent)}")

    summarise(snap)
    if args.diff and previous and previous != target:
        diff(json.loads(previous.read_text(encoding="utf-8")), snap)
    elif args.diff:
        print("\n(kein Vorgaenger-Snapshot fuer einen Vergleich)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
