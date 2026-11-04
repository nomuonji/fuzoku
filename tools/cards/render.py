"""Render the punchline card and subtitle samples to assets/cards/ (needs Playwright + Noto Serif CJK JP).

    python tools/cards/render.py [episode_number]
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE.parent.parent / "assets" / "cards"


def main(ep="001"):
    jobs = [
        ("card.html", {"__MODE__": "", "__TOP__": "560", "#001": f"#{ep}"}, "ochi_card_1080x1920.png", False),
        ("card.html", {"__MODE__": "transparent", "__TOP__": "560", "#001": f"#{ep}"}, "ochi_overlay_transparent.png", True),
        ("subtitle.html", {"__MODE__": "guide"}, "subtitle_safearea_guide.png", False),
        ("subtitle.html", {"__MODE__": "noguide"}, "subtitle_style_sample.png", False),
    ]
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for src, rep, out, transparent in jobs:
            html = (HERE / src).read_text(encoding="utf-8")
            for k, v in rep.items():
                html = html.replace(k, v)
            tmp = HERE / f"_{out}.html"
            tmp.write_text(html, encoding="utf-8")
            page = browser.new_page(viewport={"width": 1080, "height": 1920})
            page.goto(tmp.as_uri())
            page.wait_for_timeout(400)
            page.screenshot(path=str(OUT / out), omit_background=transparent)
            tmp.unlink()
            print("wrote", OUT / out)
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "001")
