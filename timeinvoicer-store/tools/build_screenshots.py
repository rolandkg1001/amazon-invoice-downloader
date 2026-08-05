#!/usr/bin/env python3
"""Rendert App-Store-Screenshots im Google-Play-Overlay-Stil.

Quelle der App-Inhalte sind die freigestellten iOS-Screens unter assets/screens
(echte iOS-UI, kein Android-Material — siehe README).  Darüber legt das Skript
das Overlay aus dem Play-Listing: Verlaufsband oben mit Headline und goldener
Subline, unten ein dunkles Band mit Benefit-Chips und Tagline.

Gerendert wird über Headless-Chromium, damit Typografie und Pill-Radien exakt
den CSS-Werten folgen.  Alle Maße sind in "Play-Units" (u) angegeben: das
Play-Design ist auf 1080 px Breite vermessen, u = Zielbreite / 1080 * scale.

    python3 tools/build_screenshots.py                 # alles bauen
    python3 tools/build_screenshots.py --target ipad-13
    python3 tools/build_screenshots.py --only 01,03
"""

from __future__ import annotations

import argparse
import base64
import json
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = Path(__file__).resolve().parent / "screenshots.config.json"
FONTS = Path(__file__).resolve().parent / "fonts"
SCREENS = ROOT / "assets" / "screens"
OUT = ROOT / "screenshots"

# headless_shell zuerst: `chrome --headless` legt den Layout-Viewport rund 87 px
# niedriger an als --window-size verlangt, wodurch das untere Band abgeschnitten
# wird.  headless_shell hält die Fenstergröße exakt ein.
CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
    "/opt/pw-browsers/chromium_headless_shell/chrome-linux/headless_shell",
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium/chrome-linux/chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/google-chrome",
]


def find_chrome() -> str:
    for c in CHROME_CANDIDATES:
        if Path(c).exists():
            return c
    for name in ("headless_shell", "chromium", "chromium-browser", "google-chrome", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    sys.exit("Kein Chromium gefunden — bitte CHROME_CANDIDATES in diesem Skript ergänzen.")


def data_uri(path: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def font_face_css() -> str:
    faces = []
    for weight in (400, 600, 700, 800):
        ttf = FONTS / f"Inter-{weight}.ttf"
        if not ttf.exists():
            continue
        faces.append(
            "@font-face{font-family:'InterLocal';font-style:normal;"
            f"font-weight:{weight};src:url({data_uri(ttf, 'font/ttf')}) format('truetype');}}"
        )
    return "\n".join(faces)


def build_html(screen: dict, target: dict, common: dict, design: dict, fonts_css: str) -> str:
    """Baut die Seite für genau einen Screenshot.

    Das Layout ist ein Flex-Column über die volle Zielhöhe:
    Kopfband (feste Höhe) — App-Fläche (flex:1, Bild als object-fit:cover) —
    Fußband (feste Höhe, Tagline unten verankert).
    """
    w, h = target["width"], target["height"]
    u = w / 1080.0 * target.get("scale", 1.0)

    def px(v: float) -> str:
        return f"{v * u:.2f}px"

    img = data_uri(SCREENS / screen["file"], "image/png")
    focus = {"top": "center top", "center": "center center", "bottom": "center bottom"}[
        screen.get("focus", "top")
    ]
    chips = "".join(f"<span class=chip>{escape(c)}</span>" for c in screen["chips"])

    return f"""<!doctype html><html lang=de><head><meta charset=utf-8><style>
{fonts_css}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}px;height:{h}px;overflow:hidden}}
body{{font-family:'InterLocal','Inter',system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;display:flex;flex-direction:column;
  background:{design['bandColor']}}}

.head{{height:{px(360)};flex:0 0 auto;padding:{px(50)} {px(56)} 0 {px(56)};
  background:linear-gradient(180deg,{design['headerGradientTop']} 0%,{design['headerGradientBottom']} 100%)}}
.headline{{font-size:{px(66)};font-weight:800;line-height:1.05;
  letter-spacing:{px(-0.8)};color:{design['headlineColor']}}}
.subline{{font-size:{px(34)};font-weight:500;line-height:1.22;
  margin-top:{px(16)};color:{design['sublineColor']}}}

.shot{{flex:1 1 auto;min-height:0;position:relative;overflow:hidden}}
.shot img{{width:100%;height:100%;object-fit:cover;object-position:{focus};display:block}}

.band{{height:{px(300)};flex:0 0 auto;background:{design['bandColor']};
  padding:{px(30)} {px(56)} {px(21)} {px(56)};
  display:flex;flex-direction:column}}
.band h2{{font-size:{px(34)};font-weight:700;line-height:1.15;
  color:#fff;letter-spacing:{px(-0.2)}}}
.chips{{display:flex;flex-wrap:wrap;gap:{px(15)};margin-top:{px(24)}}}
.chip{{display:inline-flex;align-items:center;height:{px(57)};
  padding:0 {px(21)};border-radius:{px(28.5)};
  background:{design['chipBg']};color:{design['chipFg']};
  font-size:{px(30)};font-weight:700;line-height:1;white-space:nowrap}}
.foot{{margin-top:auto;font-size:{px(26)};font-weight:400;
  color:{design['footerColor']};line-height:1.2}}
</style></head><body>
<div class=head>
  <div class=headline>{escape(screen['headline'])}</div>
  <div class=subline>{escape(screen['subline'])}</div>
</div>
<div class=shot><img src="{img}" alt=""></div>
<div class=band>
  <h2>{escape(common['bandHeading'])}</h2>
  <div class=chips>{chips}</div>
  <div class=foot>{escape(common['footer'])}</div>
</div>
</body></html>"""


def render(chrome: str, html: str, out_png: Path, w: int, h: int) -> None:
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / "page.html"
        page.write_text(html, encoding="utf-8")
        cmd = [chrome]
        if Path(chrome).name != "headless_shell":
            cmd.append("--headless")
        cmd += [
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--default-background-color=00000000",
            f"--window-size={w},{h}",
            f"--screenshot={out_png}",
            f"--user-data-dir={td}/profile",
            page.as_uri(),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if not out_png.exists():
            sys.exit(f"Render fehlgeschlagen für {out_png.name}:\n{res.stderr[-2000:]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", help="nur dieses Ziel bauen, z.B. iphone-6.9")
    ap.add_argument("--only", help="nur diese Screen-Nummern, z.B. 01,03")
    args = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    chrome = find_chrome()
    fonts_css = font_face_css()
    if not fonts_css:
        sys.exit(f"Keine Inter-TTFs in {FONTS} gefunden.")
    wanted = set(args.only.split(",")) if args.only else None

    total = 0
    for target in cfg["targets"]:
        if args.target and target["name"] != args.target:
            continue
        out_dir = OUT / target["name"]
        out_dir.mkdir(parents=True, exist_ok=True)
        for idx, screen in enumerate(cfg["screens"][target["device"]], start=1):
            num = f"{idx:02d}"
            if wanted and num not in wanted:
                continue
            slug = screen["file"].split("_", 1)[1].removesuffix(".png")
            out_png = out_dir / f"{slug}.png"
            html = build_html(screen, target, cfg["common"], cfg["design"], fonts_css)
            render(chrome, html, out_png, target["width"], target["height"])
            print(f"  {target['name']}/{out_png.name}")
            total += 1
    print(f"\n{total} Screenshots in {OUT} erzeugt.")


if __name__ == "__main__":
    main()
