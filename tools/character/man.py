"""Generator for the protagonist ("男") — flat graphic-noir shapes, layered for rigging.
Every body part is its own <g id=...> so it can be animated (Remotion / AE / Rive)."""

INK = "#0E0E10"
SHADOW = "#2A2A2E"
DARK = "#45454B"
MID = "#77777D"
LIGHT = "#B4B2AC"     # coat (balmacaan, desaturated beige -> grey)
PAPER = "#E9E6DF"     # skin / shirt highlight
SKIN = "#CFCAC0"
SKIN_SH = "#8E8A83"
ACCENT = "#FF2E88"


def P(d, fill, extra="", rim=False):
    """rim=True: a grey copy nudged up 3px behind the shape = rim light on the top edge (hair vs dark backgrounds)."""
    back = f'<path d="{d}" fill="#5A5A60" transform="translate(0 -3.5)"/>' if rim else ""
    return f'{back}<path d="{d}" fill="{fill}" {extra}/>'


# ---------------------------------------------------------------- face parts
def eyes(cx, ey, sep, w, mode="blank"):
    """Heavy-lidded, slightly drooping 'bedroom' eyes. mode: blank | distant | glance | resolve"""
    out = []
    droop = 2.8
    lid = {"blank": 6.6, "distant": 4.4, "glance": 7.2, "resolve": 5.6}[mode]
    for side in (-1, 1):
        x = cx + side * sep
        xi, xo = x - side * w / 2, x + side * w / 2
        # white
        out.append(P(f"M{xi},{ey} Q{x},{ey-3} {xo},{ey+droop} Q{x},{ey+4.5} {xi},{ey} Z", PAPER))
        px = x + {"blank": side * -0.04 * w, "distant": -w * 0.22, "glance": w * 0.34, "resolve": 0}[mode]
        py = ey + {"blank": 1.4, "distant": -0.6, "glance": 1.6, "resolve": 1.0}[mode]
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{w*0.17:.1f}" fill="{INK}"/>')
        # heavy upper lid, its lower edge sits low over the pupil
        out.append(P(f"M{xi-side*1.5},{ey+0.3} Q{x},{ey-5.5} {xo+side*1.8},{ey+droop+0.6} "
                     f"L{xo+side*1.2},{ey+droop-1+lid*0.55} Q{x},{ey-3.2+lid} {xi-side*1},{ey-0.8+lid*0.55} Z", INK))
        # lid crease (heavy, sleepy)
        out.append(f'<path d="M{xi},{ey-6} Q{x},{ey-10} {xo+side*2},{ey-3+droop}" stroke="{SKIN_SH}" stroke-width="1.8" fill="none"/>')
        # puffy under-eye (tear trough) + bag
        out.append(f'<path d="M{xi+side*1},{ey+5} Q{x},{ey+8.5} {xo},{ey+droop+3.5}" stroke="{SKIN_SH}" stroke-width="1.6" fill="none"/>')
        out.append(f'<path d="M{xi+side*3},{ey+10} Q{x},{ey+13} {xo-side*2},{ey+droop+8}" stroke="{SKIN_SH}" stroke-width="1.2" fill="none" opacity=".7"/>')
    return "".join(out)


def brows(cx, by, sep, w, mode="blank"):
    out = []
    for side in (-1, 1):
        x = cx + side * sep
        inner = x - side * w / 2
        outer = x + side * w / 2
        tilt = {"blank": -1.0, "distant": -3.0, "glance": 1.0, "resolve": 5.0}[mode]
        lift = -4.0 if (mode in ("blank", "glance") and side == 1) else 0.0  # one brow cocked
        out.append(P(f"M{inner},{by+tilt+lift} Q{x},{by-3+lift} {outer},{by+1.5+lift} L{outer},{by+5+lift} Q{x},{by+0.5+lift} {inner},{by+tilt+4.5+lift} Z", INK))
    return "".join(out)


def mouth(cx, my, w, mode="blank"):
    """Fuller lower lip, one corner up (a knowing half-smile), mole by the mouth."""
    up = {"blank": 4.5, "distant": 0.5, "glance": 7.0, "resolve": 5.5}[mode]
    out = []
    # lower lip volume
    out.append(P(f"M{cx-w*0.34},{my+2.5} Q{cx},{my+12} {cx+w*0.32},{my+1.5} Q{cx},{my+5} {cx-w*0.34},{my+2.5} Z", SKIN_SH, 'opacity=".95"'))
    # smile line on the raised side
    if up > 3:
        out.append(f'<path d="M{cx+w*0.62},{my-14} Q{cx+w*0.72},{my-4} {cx+w*0.58},{my+3}" stroke="{SKIN_SH}" stroke-width="1.8" fill="none"/>')
    if mode == "distant":
        out.append(f'<ellipse cx="{cx}" cy="{my+0.5}" rx="{w*0.16}" ry="1.6" fill="{INK}"/>')
    out.append(f'<path d="M{cx-w/2},{my+1} Q{cx-w*0.05},{my+2.2} {cx+w/2},{my-up}" stroke="{INK}" stroke-width="2.6" fill="none" stroke-linecap="round"/>')
    out.append(f'<circle id="mole" cx="{cx+w*0.66}" cy="{my+7}" r="3" fill="{INK}"/>')
    return "".join(out)


# ---------------------------------------------------------------- head (front)
def head_front(cx, top, H, W, jaw="long", mode="blank", light="right"):
    """cx: centre, top: crown y, H: head height (crown→chin), W: face width."""
    hw = W / 2
    chin = top + H
    brow_y = top + H * 0.43
    eye_y = top + H * 0.52
    mouth_y = top + H * 0.85
    hair_line = top + H * 0.22
    jaw_y = top + H * 0.70
    if jaw == "square":
        face = (f"M{cx-hw},{hair_line} L{cx-hw},{jaw_y} Q{cx-hw},{chin} {cx-hw*0.45},{chin} "
                f"L{cx+hw*0.45},{chin} Q{cx+hw},{chin} {cx+hw},{jaw_y} L{cx+hw},{hair_line} Z")
    elif jaw == "narrow":
        face = (f"M{cx-hw},{hair_line} C{cx-hw},{jaw_y} {cx-hw*0.55},{chin} {cx},{chin} "
                f"C{cx+hw*0.55},{chin} {cx+hw},{jaw_y} {cx+hw},{hair_line} Z")
    else:  # long
        face = (f"M{cx-hw},{hair_line} L{cx-hw*0.98},{jaw_y} C{cx-hw*0.9},{chin-H*0.05} {cx-hw*0.45},{chin} {cx},{chin} "
                f"C{cx+hw*0.45},{chin} {cx+hw*0.9},{chin-H*0.05} {cx+hw*0.98},{jaw_y} L{cx+hw},{hair_line} Z")
    s = []
    s.append(f'<g id="head">')
    # ears
    s.append(f'<g id="ears"><ellipse cx="{cx-hw-3}" cy="{eye_y+4}" rx="6" ry="{H*0.12:.1f}" fill="{SKIN_SH}"/>'
             f'<ellipse cx="{cx+hw+3}" cy="{eye_y+4}" rx="6" ry="{H*0.12:.1f}" fill="{SKIN}"/></g>')
    s.append(f'<g id="face">{P(face, SKIN)}')
    # stubble
    s.append(P(f"M{cx-hw*0.92},{jaw_y-4} C{cx-hw*0.8},{chin-2} {cx-hw*0.4},{chin+1} {cx},{chin+1} "
               f"C{cx+hw*0.4},{chin+1} {cx+hw*0.8},{chin-2} {cx+hw*0.92},{jaw_y-4} "
               f"C{cx+hw*0.6},{mouth_y+8} {cx-hw*0.6},{mouth_y+8} {cx-hw*0.92},{jaw_y-4} Z", MID, 'opacity="0.62"'))
    # noir side shadow (light from the side given)
    sgn = -1 if light == "right" else 1
    edge = cx + sgn * hw
    s.append(P(f"M{cx + sgn*hw*0.18},{hair_line} L{edge},{hair_line} L{edge},{jaw_y} "
               f"C{edge - sgn*hw*0.1},{chin-H*0.05} {cx+sgn*hw*0.45},{chin} {cx+sgn*hw*0.05},{chin} "
               f"C{cx+sgn*hw*0.25},{mouth_y} {cx+sgn*hw*0.05},{eye_y+H*0.12} {cx+sgn*hw*0.12},{eye_y} "
               f"C{cx+sgn*hw*0.2},{brow_y} {cx+sgn*hw*0.1},{hair_line+H*0.1} {cx + sgn*hw*0.18},{hair_line} Z",
               INK, 'id="face-shadow" opacity="0.72"'))
    s.append('</g>')
    # nose
    s.append(f'<g id="nose"><path d="M{cx+2},{eye_y+3} L{cx-3},{eye_y+H*0.2} L{cx+5},{eye_y+H*0.22}" '
             f'stroke="{INK}" stroke-width="2" fill="none" stroke-linejoin="round" stroke-linecap="round"/></g>')
    s.append(f'<g id="sheen"><ellipse cx="{cx+W*0.06}" cy="{eye_y+H*0.17}" rx="{W*0.025}" ry="{H*0.02}" fill="#F4F2EE" opacity=".8"/>'
             f'<ellipse cx="{cx+W*0.14}" cy="{brow_y-H*0.08}" rx="{W*0.07}" ry="{H*0.012}" fill="#F4F2EE" opacity=".45"/></g>')
    s.append(f'<g id="brows">{brows(cx, brow_y, W*0.22, W*0.26, mode)}</g>')
    s.append(f'<g id="eyes">{eyes(cx, eye_y, W*0.22, W*0.25, mode)}</g>')
    s.append(f'<g id="mouth">{mouth(cx, mouth_y, W*0.3, mode)}</g>')
    # scar above the character's LEFT brow (viewer right)
    s.append(f'<path id="scar" d="M{cx+W*0.26},{brow_y-9} L{cx+W*0.31},{brow_y-4}" stroke="{SKIN_SH}" stroke-width="2.2" stroke-linecap="round"/>')
    # hair: short, side part on viewer-left, grey temples
    s.append('<g id="hair">')
    s.append(P(f"M{cx-hw-3},{hair_line+H*0.12} C{cx-hw-6},{top+H*0.02} {cx-hw*0.2},{top-H*0.04} {cx+hw*0.15},{top} "
               f"C{cx+hw*0.85},{top+H*0.03} {cx+hw+5},{top+H*0.1} {cx+hw+2},{hair_line+H*0.12} "
               f"C{cx+hw*0.9},{hair_line} {cx+hw*0.5},{hair_line-H*0.05} {cx-hw*0.25},{hair_line-H*0.02} "
               f"C{cx-hw*0.6},{hair_line+H*0.01} {cx-hw*0.85},{hair_line+H*0.05} {cx-hw-3},{hair_line+H*0.12} Z", INK, rim=True))
    # loose strand falling over forehead (part breaking down)
    s.append(P(f"M{cx-hw*0.25},{hair_line-H*0.02} C{cx-hw*0.1},{hair_line+H*0.06} {cx-hw*0.05},{hair_line+H*0.1} {cx-hw*0.12},{hair_line+H*0.14} "
               f"C{cx},{hair_line+H*0.08} {cx+hw*0.05},{hair_line+H*0.02} {cx+hw*0.05},{hair_line-H*0.04} Z", INK))
    for side in (-1, 1):
        x = cx + side * (hw + 1)
        s.append(P(f"M{x},{hair_line+H*0.02} L{x - side*5},{hair_line+H*0.04} L{x - side*4},{eye_y-2} L{x+side*1},{eye_y-4} Z", MID))
    s.append('</g>')
    s.append('</g>')
    return "".join(s)


# ---------------------------------------------------------------- full body (front)
def body_front(cx, top, H, W, heads=7.5, shoulder=2.3, coat_len=0.63, jaw="long", mode="blank",
               slouch=6, coat_flare=1.08):
    """heads: total height in head-units; shoulder: shoulder width in face-widths."""
    total = H * heads
    ground = top + total
    neck_top = top + H * 0.95
    sh_y = top + H * 1.32
    sw = W * shoulder / 2
    hem_y = top + total * coat_len
    hip_w = sw * 0.86 * coat_flare
    s = []
    # legs
    leg_w = W * 0.36
    s.append('<g id="legs">')
    for side in (-1, 1):
        lx = cx + side * W * 0.24
        s.append(P(f"M{lx-leg_w/2},{hem_y-20} L{lx+leg_w/2},{hem_y-20} L{lx+leg_w/2-2},{ground-10} L{lx-leg_w/2+2},{ground-10} Z",
                   SHADOW if side < 0 else DARK))
        s.append(P(f"M{lx-leg_w/2-4},{ground-16} L{lx+leg_w/2+4},{ground-16} Q{lx+leg_w/2+side*14},{ground-6} {lx+leg_w/2+side*12},{ground} "
                   f"L{lx-leg_w/2-4},{ground} Z", INK))
    s.append('</g>')
    # coat body
    s.append('<g id="torso">')
    coat = (f"M{cx-W*0.32},{neck_top+H*0.18} L{cx-sw},{sh_y+8} C{cx-sw-4},{sh_y+H*1.6} {cx-hip_w-2},{hem_y-H*1.2} {cx-hip_w},{hem_y} "
            f"L{cx+hip_w},{hem_y} C{cx+hip_w+2},{hem_y-H*1.2} {cx+sw+4},{sh_y+H*1.6} {cx+sw},{sh_y+8} "
            f"L{cx+W*0.32},{neck_top+H*0.18} Z")
    s.append(P(coat, LIGHT))
    # coat shadow side (viewer left, light from right)
    s.append(P(f"M{cx-W*0.32},{neck_top+H*0.18} L{cx-sw},{sh_y+8} C{cx-sw-4},{sh_y+H*1.6} {cx-hip_w-2},{hem_y-H*1.2} {cx-hip_w},{hem_y} "
               f"L{cx-hip_w*0.45},{hem_y} C{cx-hip_w*0.5},{hem_y-H*1.5} {cx-sw*0.55},{sh_y+H*1.2} {cx-W*0.2},{neck_top+H*0.4} Z", MID))
    # opening: suit, shirt, loosened tie
    open_bottom = sh_y + H * 1.75
    s.append(P(f"M{cx-W*0.2},{neck_top+H*0.3} L{cx+W*0.2},{neck_top+H*0.3} L{cx+W*0.12},{open_bottom} L{cx-W*0.08},{open_bottom} Z", SHADOW))
    s.append(P(f"M{cx-W*0.15},{neck_top+H*0.26} L{cx+W*0.17},{neck_top+H*0.26} L{cx+W*0.03},{neck_top+H*1.05} Z", PAPER))
    # open collar: skin V and a hint of chest hair
    s.append(P(f"M{cx-W*0.08},{neck_top+H*0.27} L{cx+W*0.1},{neck_top+H*0.27} L{cx+W*0.01},{neck_top+H*0.7} Z", SKIN_SH))
    for i in range(5):
        hx = cx - W * 0.03 + (i % 3) * W * 0.03
        hy = neck_top + H * (0.4 + 0.05 * i)
        s.append(f'<path d="M{hx},{hy} q2,-3 4,0" stroke="{INK}" stroke-width="1.2" fill="none" opacity=".55"/>')
    s.append(P(f"M{cx-W*0.02},{neck_top+H*0.74} L{cx+W*0.09},{neck_top+H*0.74} L{cx+W*0.1},{neck_top+H*0.84} "
               f"L{cx+W*0.13},{open_bottom-H*0.25} L{cx+W*0.04},{open_bottom-H*0.1} L{cx-W*0.02},{open_bottom-H*0.28} L{cx+W*0.0},{neck_top+H*0.84} Z", INK, 'id="tie"'))
    # coat front edge overlap line + buttons (single, hidden placket)
    s.append(f'<path d="M{cx+W*0.12},{open_bottom} L{cx+W*0.06},{hem_y}" stroke="{MID}" stroke-width="2.4"/>')
    # pockets
    for side in (-1, 1):
        px = cx + side * hip_w * 0.55
        s.append(f'<path d="M{px - 14},{hem_y - H*1.3} L{px + 12},{hem_y - H*1.38}" stroke="{DARK}" stroke-width="2.4" stroke-linecap="round"/>')
    s.append('</g>')
    # arms (over the coat, sleeve seam drawn)
    s.append('<g id="arm-R">')  # character right = viewer left
    s.append(P(f"M{cx-sw+4},{sh_y+4} C{cx-sw-10},{sh_y+H*1.2} {cx-sw-12},{sh_y+H*2.2} {cx-sw-6},{sh_y+H*2.75} "
               f"L{cx-sw+18},{sh_y+H*2.75} C{cx-sw+18},{sh_y+H*2.0} {cx-sw+22},{sh_y+H*1.0} {cx-sw+30},{sh_y+12} Z", MID))
    s.append(f'<path d="M{cx-sw+30},{sh_y+12} C{cx-sw+22},{sh_y+H*1.0} {cx-sw+18},{sh_y+H*2.0} {cx-sw+18},{sh_y+H*2.75}" stroke="{DARK}" stroke-width="2.2" fill="none"/>')
    s.append(f'<ellipse id="hand-R" cx="{cx-sw+6}" cy="{sh_y+H*2.95}" rx="{W*0.14}" ry="{H*0.2}" fill="{SKIN_SH}"/>')
    s.append('</g>')
    s.append('<g id="arm-L">')
    s.append(P(f"M{cx+sw-4},{sh_y+4} C{cx+sw+10},{sh_y+H*1.2} {cx+sw+12},{sh_y+H*2.2} {cx+sw+6},{sh_y+H*2.75} "
               f"L{cx+sw-18},{sh_y+H*2.75} C{cx+sw-18},{sh_y+H*2.0} {cx+sw-22},{sh_y+H*1.0} {cx+sw-30},{sh_y+12} Z", LIGHT))
    s.append(f'<path d="M{cx+sw-30},{sh_y+12} C{cx+sw-22},{sh_y+H*1.0} {cx+sw-18},{sh_y+H*2.0} {cx+sw-18},{sh_y+H*2.75}" stroke="{MID}" stroke-width="2.2" fill="none"/>')
    s.append(f'<ellipse id="hand-L" cx="{cx+sw-6}" cy="{sh_y+H*2.95}" rx="{W*0.14}" ry="{H*0.2}" fill="{SKIN}"/>')
    s.append('</g>')
    # neck
    s.append(f'<g id="neck">{P(f"M{cx-W*0.17},{neck_top-6} L{cx+W*0.17},{neck_top-6} L{cx+W*0.18},{neck_top+H*0.32} L{cx-W*0.18},{neck_top+H*0.32} Z", SKIN_SH)}</g>')
    # turned-up collar (in front of neck)
    s.append('<g id="collar">')
    s.append(P(f"M{cx-W*0.18},{neck_top+H*0.02} L{cx-W*0.48},{neck_top+H*0.18} L{cx-W*0.38},{neck_top+H*0.62} L{cx-W*0.12},{neck_top+H*0.38} Z", MID))
    s.append(P(f"M{cx+W*0.18},{neck_top+H*0.02} L{cx+W*0.48},{neck_top+H*0.18} L{cx+W*0.38},{neck_top+H*0.62} L{cx+W*0.12},{neck_top+H*0.38} Z", LIGHT))
    s.append('</g>')
    # head, nudged forward/down by slouch
    s.append(f'<g transform="translate(0,{slouch})">{head_front(cx, top, H, W, jaw=jaw, mode=mode)}</g>')
    return "".join(s)


# ---------------------------------------------------------------- side view (profile, facing right)
def body_side(cx, top, H, W, heads=7.5, coat_len=0.63, slouch=26):
    total = H * heads
    ground = top + total
    hem_y = top + total * coat_len
    sh_y = top + H * 1.32
    d = W * 0.82  # body depth
    s = []
    # legs
    s.append('<g id="legs">')
    s.append(P(f"M{cx-d*0.25},{hem_y-20} L{cx+d*0.15},{hem_y-20} L{cx+d*0.12},{ground-10} L{cx-d*0.22},{ground-10} Z", SHADOW))
    s.append(P(f"M{cx-d*0.26},{ground-12} L{cx+d*0.35},{ground-12} Q{cx+d*0.5},{ground} {cx+d*0.3},{ground} L{cx-d*0.26},{ground} Z", INK))
    s.append('</g>')
    # coat: back curve (slouch) and front
    s.append('<g id="torso">')
    s.append(P(f"M{cx-d*0.35},{top+H*1.15} C{cx-d*0.75},{sh_y+H*0.3} {cx-d*0.7},{sh_y+H*2.2} {cx-d*0.62},{hem_y} "
               f"L{cx+d*0.55},{hem_y} C{cx+d*0.6},{sh_y+H*2.2} {cx+d*0.55},{sh_y+H*0.5} {cx+d*0.25},{top+H*1.15} Z", LIGHT))
    s.append(P(f"M{cx-d*0.35},{top+H*1.15} C{cx-d*0.75},{sh_y+H*0.3} {cx-d*0.7},{sh_y+H*2.2} {cx-d*0.62},{hem_y} "
               f"L{cx-d*0.3},{hem_y} C{cx-d*0.35},{sh_y+H*2.2} {cx-d*0.4},{sh_y+H*0.6} {cx-d*0.1},{top+H*1.2} Z", MID))
    # collar up, behind the neck
    s.append(P(f"M{cx-d*0.38},{top+H*1.2} L{cx-d*0.45},{top+H*0.82} L{cx-d*0.05},{top+H*0.98} L{cx+d*0.05},{top+H*1.3} Z", MID, 'id="collar"'))
    s.append('</g>')
    # arm hanging, slightly forward
    s.append('<g id="arm-L">')
    s.append(P(f"M{cx-d*0.15},{sh_y} C{cx-d*0.05},{sh_y+H*1.2} {cx+d*0.05},{sh_y+H*2.2} {cx+d*0.12},{sh_y+H*2.75} "
               f"L{cx+d*0.38},{sh_y+H*2.7} C{cx+d*0.3},{sh_y+H*2.0} {cx+d*0.25},{sh_y+H*1.0} {cx+d*0.2},{sh_y+6} Z", "#A3A19B"))
    s.append(f'<ellipse id="hand-L" cx="{cx+d*0.27}" cy="{sh_y+H*2.95}" rx="{W*0.11}" ry="{H*0.2}" fill="{SKIN}"/>')
    s.append('</g>')
    # head in profile, pushed forward by slouch
    hx = cx + slouch * 0.7
    ht = top + slouch * 0.4
    chin = ht + H
    s.append(f'<g id="head">')
    s.append(P(f"M{hx-W*0.18},{ht+H*0.95} L{hx+W*0.12},{ht+H*0.95} L{hx+W*0.05},{ht+H*1.25} L{hx-W*0.25},{ht+H*1.25} Z", SKIN_SH, 'id="neck"'))
    face = (f"M{hx-W*0.38},{ht+H*0.25} C{hx-W*0.45},{ht+H*0.7} {hx-W*0.25},{ht+H*0.95} {hx+W*0.05},{chin} "
            f"L{hx+W*0.28},{chin-H*0.02} C{hx+W*0.33},{chin-H*0.08} {hx+W*0.3},{ht+H*0.86} {hx+W*0.33},{ht+H*0.83} "
            f"L{hx+W*0.36},{ht+H*0.74} L{hx+W*0.34},{ht+H*0.7} L{hx+W*0.48},{ht+H*0.66} L{hx+W*0.36},{ht+H*0.5} "
            f"L{hx+W*0.38},{ht+H*0.42} C{hx+W*0.38},{ht+H*0.3} {hx+W*0.3},{ht+H*0.22} {hx+W*0.2},{ht+H*0.2} Z")
    s.append(P(face, SKIN))
    s.append(P(f"M{hx-W*0.3},{ht+H*0.72} C{hx-W*0.18},{ht+H*0.95} {hx},{chin} {hx+W*0.28},{chin-H*0.02} "
               f"C{hx+W*0.3},{ht+H*0.86} {hx+W*0.1},{ht+H*0.86} {hx-W*0.3},{ht+H*0.72} Z", MID, 'opacity="0.45"'))
    # ear
    s.append(f'<ellipse cx="{hx-W*0.1}" cy="{ht+H*0.56}" rx="7" ry="{H*0.12:.1f}" fill="{SKIN_SH}"/>')
    # eye (side)
    ey = ht + H * 0.52
    s.append(P(f"M{hx+W*0.22},{ey} L{hx+W*0.32},{ey-1} L{hx+W*0.31},{ey+2} Z", INK))
    s.append(P(f"M{hx+W*0.18},{ey-3} L{hx+W*0.34},{ey-4} L{hx+W*0.34},{ey-1} L{hx+W*0.19},{ey} Z", INK))
    s.append(P(f"M{hx+W*0.17},{ht+H*0.43} L{hx+W*0.37},{ht+H*0.41} L{hx+W*0.37},{ht+H*0.44} L{hx+W*0.18},{ht+H*0.46} Z", INK))
    s.append(f'<path d="M{hx+W*0.26},{ht+H*0.85} L{hx+W*0.33},{ht+H*0.85}" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>')
    # hair
    s.append(P(f"M{hx-W*0.42},{ht+H*0.55} C{hx-W*0.5},{ht+H*0.1} {hx-W*0.1},{ht-H*0.05} {hx+W*0.2},{ht+H*0.02} "
               f"C{hx+W*0.38},{ht+H*0.06} {hx+W*0.42},{ht+H*0.16} {hx+W*0.36},{ht+H*0.24} "
               f"C{hx+W*0.2},{ht+H*0.2} {hx},{ht+H*0.22} {hx-W*0.15},{ht+H*0.3} "
               f"C{hx-W*0.2},{ht+H*0.4} {hx-W*0.25},{ht+H*0.5} {hx-W*0.3},{ht+H*0.6} Z", INK, rim=True))
    s.append(P(f"M{hx-W*0.17},{ht+H*0.3} L{hx-W*0.25},{ht+H*0.42} L{hx-W*0.2},{ht+H*0.5} L{hx-W*0.12},{ht+H*0.36} Z", MID))
    s.append('</g>')
    return "".join(s)


# ---------------------------------------------------------------- back view
def body_back(cx, top, H, W, heads=7.5, shoulder=2.3, coat_len=0.63, coat_flare=1.08):
    total = H * heads
    ground = top + total
    hem_y = top + total * coat_len
    sh_y = top + H * 1.32
    sw = W * shoulder / 2
    hip_w = sw * 0.86 * coat_flare
    s = []
    s.append('<g id="legs">')
    for side in (-1, 1):
        lx = cx + side * W * 0.24
        s.append(P(f"M{lx-W*0.18},{hem_y-20} L{lx+W*0.18},{hem_y-20} L{lx+W*0.16},{ground-10} L{lx-W*0.16},{ground-10} Z", SHADOW))
        s.append(P(f"M{lx-W*0.19},{ground-12} L{lx+W*0.19},{ground-12} L{lx+W*0.19},{ground} L{lx-W*0.19},{ground} Z", INK))
    s.append('</g>')
    for side, col in ((-1, MID), (1, LIGHT)):
        s.append(P(f"M{cx+side*(sw-4)},{sh_y+4} C{cx+side*(sw+10)},{sh_y+H*1.2} {cx+side*(sw+12)},{sh_y+H*2.2} {cx+side*(sw+6)},{sh_y+H*2.75} "
                   f"L{cx+side*(sw-18)},{sh_y+H*2.75} L{cx+side*(sw-30)},{sh_y+12} Z", col))
    s.append(P(f"M{cx-W*0.34},{top+H*1.05} L{cx-sw},{sh_y+8} C{cx-sw-4},{sh_y+H*1.6} {cx-hip_w-2},{hem_y-H*1.2} {cx-hip_w},{hem_y} "
               f"L{cx+hip_w},{hem_y} C{cx+hip_w+2},{hem_y-H*1.2} {cx+sw+4},{sh_y+H*1.6} {cx+sw},{sh_y+8} L{cx+W*0.34},{top+H*1.05} Z", LIGHT, 'id="torso"'))
    s.append(P(f"M{cx-W*0.34},{top+H*1.05} L{cx-sw},{sh_y+8} C{cx-sw-4},{sh_y+H*1.6} {cx-hip_w-2},{hem_y-H*1.2} {cx-hip_w},{hem_y} "
               f"L{cx-hip_w*0.4},{hem_y} C{cx-hip_w*0.5},{hem_y-H*1.6} {cx-sw*0.5},{sh_y+H*1.0} {cx-W*0.1},{top+H*1.2} Z", MID))
    # back vent
    s.append(f'<path d="M{cx},{hem_y-H*1.1} L{cx},{hem_y}" stroke="{MID}" stroke-width="2.4"/>')
    # collar standing up, from behind it hides the neck
    s.append(P(f"M{cx-W*0.42},{top+H*1.12} L{cx-W*0.38},{top+H*0.8} L{cx+W*0.38},{top+H*0.8} L{cx+W*0.42},{top+H*1.12} Z", MID, 'id="collar"'))
    # back of head
    hw = W / 2
    s.append(f'<g id="head"><ellipse cx="{cx-hw-3}" cy="{top+H*0.56}" rx="6" ry="{H*0.12:.1f}" fill="{SKIN_SH}"/>'
             f'<ellipse cx="{cx+hw+3}" cy="{top+H*0.56}" rx="6" ry="{H*0.12:.1f}" fill="{SKIN_SH}"/>')
    s.append(P(f"M{cx-hw-2},{top+H*0.35} C{cx-hw-5},{top} {cx+hw+5},{top} {cx+hw+2},{top+H*0.35} "
               f"L{cx+hw*0.85},{top+H*0.82} C{cx+hw*0.4},{top+H*0.9} {cx-hw*0.4},{top+H*0.9} {cx-hw*0.85},{top+H*0.82} Z", INK, rim=True))
    for side in (-1, 1):
        s.append(P(f"M{cx+side*(hw+1)},{top+H*0.35} L{cx+side*(hw-6)},{top+H*0.4} L{cx+side*(hw*0.86)},{top+H*0.78} L{cx+side*(hw-1)},{top+H*0.72} Z", MID))
    s.append('</g>')
    return "".join(s)


# ---------------------------------------------------------------- the passing woman: motif only (no face)
def woman_legs(x, ground, scale=1.0, top=0):
    """Long dark coat (from frame top) + calves/pumps, mid-stride, walking left->right. No face, no body above the coat."""
    k = scale
    hem = ground - 120 * k
    s = ['<g id="woman-pass">']
    # back leg (behind coat)
    s.append(P(f"M{x-24*k},{hem-10*k} L{x-6*k},{hem-10*k} L{x-50*k},{ground-40*k} L{x-62*k},{ground-44*k} Z", "#3A3A40"))
    s.append(P(f"M{x-66*k},{ground-48*k} L{x-50*k},{ground-40*k} L{x-34*k},{ground-6*k} L{x-60*k},{ground-2*k} L{x-74*k},{ground-22*k} Z", INK))
    s.append(f'<rect x="{x-78*k}" y="{ground-30*k}" width="{4*k}" height="{28*k}" fill="{INK}" transform="rotate(-20 {x-76*k} {ground-16*k})"/>')
    # front leg
    s.append(P(f"M{x+6*k},{hem-10*k} L{x+26*k},{hem-10*k} L{x+38*k},{ground-34*k} L{x+26*k},{ground-34*k} Z", "#55555C"))
    s.append(P(f"M{x+22*k},{ground-38*k} L{x+40*k},{ground-38*k} C{x+60*k},{ground-24*k} {x+76*k},{ground-8*k} {x+78*k},{ground} "
               f"L{x+28*k},{ground} L{x+24*k},{ground-16*k} Z", INK))
    s.append(f'<path d="M{x+42*k},{ground-28*k} Q{x+60*k},{ground-16*k} {x+70*k},{ground-6*k}" stroke="#9A9AA2" stroke-width="{2.4*k}" fill="none" stroke-linecap="round"/>')
    s.append(f'<rect x="{x+22*k}" y="{ground-22*k}" width="{5*k}" height="{22*k}" fill="{INK}"/>')
    # long coat, from top of frame, hem swinging back with the stride
    s.append(P(f"M{x-40*k},{top} L{x+50*k},{top} C{x+56*k},{hem-120*k} {x+58*k},{hem-40*k} {x+52*k},{hem} "
               f"C{x+10*k},{hem+12*k} {x-60*k},{hem+16*k} {x-120*k},{hem+2*k} "
               f"C{x-90*k},{hem-50*k} {x-60*k},{hem-140*k} {x-40*k},{top} Z", SHADOW))
    # fold lines
    s.append(f'<path d="M{x-10*k},{top+40*k} C{x-20*k},{hem-90*k} {x-50*k},{hem-30*k} {x-70*k},{hem+8*k}" stroke="{INK}" stroke-width="{3*k}" fill="none" opacity="0.6"/>')
    s.append(f'<path d="M{x+30*k},{top+60*k} C{x+30*k},{hem-90*k} {x+20*k},{hem-30*k} {x+10*k},{hem+10*k}" stroke="{INK}" stroke-width="{3*k}" fill="none" opacity="0.5"/>')
    # reflection on wet pavement
    s.append(P(f"M{x+28*k},{ground+4*k} L{x+78*k},{ground+4*k} L{x+66*k},{ground+40*k} L{x+30*k},{ground+44*k} Z", INK, 'opacity="0.25"'))
    s.append(f'<line x1="{x-200*k}" y1="{ground}" x2="{x+200*k}" y2="{ground}" stroke="#3A3A40" stroke-width="2"/>')
    s.append('</g>')
    return "".join(s)


def svg(w, h, inner, bg=None):
    b = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'{b}{inner}</svg>')
