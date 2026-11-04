"""Regenerate every character SVG in assets/character/ from man.py.

    python tools/character/build.py

Adopted design: A (7.5 heads). B and C are kept only as the rejected candidates.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from man import body_back, body_front, body_side, head_front, svg, woman_legs  # noqa: E402

ROOT = HERE.parent.parent / "assets" / "character"

A = dict(H=124, W=86, heads=7.5, shoulder=2.3, jaw="long", coat_len=0.63, coat_flare=1.08)
B = dict(H=150, W=118, heads=6.0, shoulder=2.9, jaw="square", coat_len=0.58, coat_flare=1.1)
C = dict(H=96, W=64, heads=9.4, shoulder=2.2, jaw="narrow", coat_len=0.82, coat_flare=1.25)


def front(p, mode="blank"):
    return body_front(200, 40, p["H"], p["W"], heads=p["heads"], shoulder=p["shoulder"],
                      coat_len=p["coat_len"], jaw=p["jaw"], mode=mode, coat_flare=p["coat_flare"])


def main():
    out = {
        "candidates/A.svg": svg(400, 1000, front(A)),
        "candidates/B.svg": svg(400, 1000, front(B)),
        "candidates/C.svg": svg(400, 1000, front(C)),
        "man/front.svg": svg(400, 1000, front(A)),
        "man/side.svg": svg(400, 1000, body_side(190, 40, A["H"], A["W"], heads=A["heads"], coat_len=A["coat_len"])),
        "man/back.svg": svg(400, 1000, body_back(200, 40, A["H"], A["W"], heads=A["heads"], shoulder=A["shoulder"],
                                                  coat_len=A["coat_len"], coat_flare=A["coat_flare"])),
        "woman_pass.svg": svg(600, 460, woman_legs(300, 380, 1.25)),
    }
    for mode in ("blank", "distant", "glance", "resolve"):
        out[f"man/face_{mode}.svg"] = svg(300, 320, head_front(150, 50, 240, 165, jaw="long", mode=mode))
    for rel, text in out.items():
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print("wrote", path.relative_to(ROOT.parent.parent))


if __name__ == "__main__":
    main()
