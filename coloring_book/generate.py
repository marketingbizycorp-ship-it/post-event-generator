#!/usr/bin/env python3
"""K-Pop Demon Hunters — Children's Coloring Book generator.

Produces print-ready, black-line-art SVG coloring pages plus a single
combined HTML file you can open and print (or "Save as PDF").

The characters are ORIGINAL, theme-inspired chibi idols & friendly demons
(idol-singer-meets-monster-hunter). They are bold, simple outlines designed
for small hands and crayons: thick strokes, big shapes, no fills to color in.

Usage:
    python coloring_book/generate.py            # build everything
    python coloring_book/generate.py --list     # list the pages

Output:
    coloring_book/pages/*.svg       one file per page
    coloring_book/coloring-book.html  printable book (all pages)
"""

from __future__ import annotations

import argparse
import html
import math
import os

# Letter page at 100 DPI, portrait.
PAGE_W = 850
PAGE_H = 1100

# Bold, kid-friendly line weights.
LINE = 5          # standard outline
LINE_BOLD = 8     # heavy outline (borders, big shapes)
LINE_FINE = 3     # small details

HERE = os.path.dirname(os.path.abspath(__file__))
PAGES_DIR = os.path.join(HERE, "pages")


# --------------------------------------------------------------------------
# Low-level SVG primitives. Everything is fill:none so it stays colorable.
# --------------------------------------------------------------------------

def _stroke(w=LINE, fill="none"):
    return (f'fill="{fill}" stroke="black" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"')


def circle(cx, cy, r, w=LINE, fill="none"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" {_stroke(w, fill)}/>'


def ellipse(cx, cy, rx, ry, w=LINE, fill="none"):
    return f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" {_stroke(w, fill)}/>'


def line(x1, y1, x2, y2, w=LINE):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" {_stroke(w)}/>'


def path(d, w=LINE, fill="none"):
    return f'<path d="{d}" {_stroke(w, fill)}/>'


def rrect(x, y, w_, h_, r, sw=LINE, fill="none"):
    return (f'<rect x="{x}" y="{y}" width="{w_}" height="{h_}" rx="{r}" '
            f'ry="{r}" {_stroke(sw, fill)}/>')


def poly(points, w=LINE, fill="none", closed=True):
    tag = "polygon" if closed else "polyline"
    pts = " ".join(f"{x},{y}" for x, y in points)
    return f'<{tag} points="{pts}" {_stroke(w, fill)}/>'


def dot(cx, cy, r):
    """A solid black dot — used sparingly for pupils so faces look alive."""
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="black"/>'


def star(cx, cy, r, w=LINE, points=5, inner_ratio=0.45, rot=-math.pi / 2):
    pts = []
    for i in range(points * 2):
        rad = r if i % 2 == 0 else r * inner_ratio
        a = rot + i * math.pi / points
        pts.append((round(cx + rad * math.cos(a), 1),
                    round(cy + rad * math.sin(a), 1)))
    return poly(pts, w=w)


def heart(cx, cy, s, w=LINE):
    d = (f"M {cx} {cy + s*0.9} "
         f"C {cx - s*1.3} {cy - s*0.2}, {cx - s*0.55} {cy - s*1.0}, {cx} {cy - s*0.25} "
         f"C {cx + s*0.55} {cy - s*1.0}, {cx + s*1.3} {cy - s*0.2}, {cx} {cy + s*0.9} Z")
    return path(d, w=w)


def music_note(cx, cy, s, w=LINE):
    return (ellipse(cx, cy, s * 0.55, s * 0.42, w) +
            line(cx + s * 0.5, cy, cx + s * 0.5, cy - s * 1.8, w) +
            path(f"M {cx + s*0.5} {cy - s*1.8} q {s*0.9} {s*0.2} {s*0.5} {s*0.9}", w))


# --------------------------------------------------------------------------
# Face & body building blocks (cute "chibi" style).
# --------------------------------------------------------------------------

def chibi_eyes(cx, cy, spread, size, happy=False):
    """Big sparkly eyes. Outlined ovals + a black pupil + a sparkle gap."""
    out = []
    for sx in (-spread, spread):
        ex = cx + sx
        if happy:
            # closed "^_^" happy eyes
            out.append(path(f"M {ex - size} {cy + size*0.3} "
                            f"Q {ex} {cy - size*0.7} {ex + size} {cy + size*0.3}", LINE))
        else:
            out.append(ellipse(ex, cy, size * 0.8, size, LINE))
            out.append(dot(ex + size * 0.12, cy + size * 0.15, size * 0.42))
            out.append(circle(ex - size * 0.18, cy - size * 0.22, size * 0.16, LINE_FINE,
                              fill="white"))
    return "".join(out)


def smile(cx, cy, wdt, open_mouth=False):
    if open_mouth:
        return path(f"M {cx - wdt} {cy} Q {cx} {cy + wdt*1.3} {cx + wdt} {cy} "
                    f"Q {cx} {cy + wdt*0.5} {cx - wdt} {cy} Z", LINE)
    return path(f"M {cx - wdt} {cy} Q {cx} {cy + wdt} {cx + wdt} {cy}", LINE)


def blush(cx, cy, spread, r):
    return (circle(cx - spread, cy, r, LINE_FINE) +
            circle(cx + spread, cy, r, LINE_FINE))


# --------------------------------------------------------------------------
# Hair styles. Each takes the head center & radius.
# --------------------------------------------------------------------------

def hair_long(cx, cy, r):
    """Long flowing idol hair with a center part and side bangs."""
    d = (f"M {cx - r} {cy} "
         f"C {cx - r*1.15} {cy - r*1.25}, {cx + r*1.15} {cy - r*1.25}, {cx + r} {cy} "
         f"M {cx - r*0.95} {cy - r*0.2} "
         f"C {cx - r*1.35} {cy + r*1.7}, {cx - r*0.9} {cy + r*2.1}, {cx - r*0.55} {cy + r*1.9} "
         f"M {cx + r*0.95} {cy - r*0.2} "
         f"C {cx + r*1.35} {cy + r*1.7}, {cx + r*0.9} {cy + r*2.1}, {cx + r*0.55} {cy + r*1.9} "
         f"M {cx} {cy - r*1.18} L {cx} {cy - r*0.55} "
         f"M {cx} {cy - r*0.95} Q {cx - r*0.6} {cy - r*0.5} {cx - r*0.75} {cy + r*0.1} "
         f"M {cx} {cy - r*0.95} Q {cx + r*0.6} {cy - r*0.5} {cx + r*0.75} {cy + r*0.1}")
    return path(d, LINE)


def hair_bun(cx, cy, r):
    """Top bun with bangs — a sporty idol look."""
    return (circle(cx, cy - r * 1.35, r * 0.42, LINE) +
            path(f"M {cx - r} {cy - r*0.1} "
                 f"C {cx - r*1.1} {cy - r*1.1}, {cx + r*1.1} {cy - r*1.1}, {cx + r} {cy - r*0.1}", LINE) +
            path(f"M {cx - r*0.8} {cy - r*0.45} q {r*0.4} {r*0.45} {r*0.8} 0 "
                 f"q {r*0.4} {-r*0.45} {r*0.8} 0", LINE_FINE))


def hair_short(cx, cy, r):
    """Short spiky idol-boy hair."""
    pts_d = (f"M {cx - r} {cy + r*0.1} "
             f"L {cx - r*0.9} {cy - r*0.7} L {cx - r*0.55} {cy - r*0.3} "
             f"L {cx - r*0.3} {cy - r*1.05} L {cx} {cy - r*0.5} "
             f"L {cx + r*0.3} {cy - r*1.05} L {cx + r*0.55} {cy - r*0.3} "
             f"L {cx + r*0.9} {cy - r*0.7} L {cx + r} {cy + r*0.1}")
    return path(pts_d, LINE)


# --------------------------------------------------------------------------
# Accessories.
# --------------------------------------------------------------------------

def microphone(x, y, scale=1.0):
    """Hand-held idol microphone, ball pointing up-ish."""
    s = scale
    out = [circle(x, y, 26 * s, LINE)]
    # grille lines
    out.append(path(f"M {x-18*s} {y-12*s} A {26*s} {26*s} 0 0 0 {x-18*s} {y+12*s}", LINE_FINE))
    out.append(path(f"M {x} {y-26*s} L {x} {y+26*s}", LINE_FINE))
    out.append(line(x, y + 26 * s, x, y + 80 * s, LINE_BOLD))
    out.append(rrect(x - 9 * s, y + 78 * s, 18 * s, 22 * s, 6 * s, LINE))
    return "".join(out)


def light_stick(x, y, scale=1.0):
    """K-pop light stick — a glowing heart on a handle."""
    s = scale
    return (heart(x, y - 40 * s, 26 * s, LINE) +
            line(x, y - 5 * s, x, y + 70 * s, LINE_BOLD) +
            rrect(x - 11 * s, y + 66 * s, 22 * s, 26 * s, 7 * s, LINE) +
            # little sparkles around the heart
            star(x - 50 * s, y - 55 * s, 10 * s, LINE_FINE) +
            star(x + 50 * s, y - 45 * s, 8 * s, LINE_FINE))


def hunter_sword(x, y, length=190, scale=1.0):
    """A glowing 'talisman' sword the hunters use against demons."""
    s = scale
    tip_y = y - length * s
    out = [
        # blade
        poly([(x, tip_y), (x - 14 * s, y - 24 * s), (x + 14 * s, y - 24 * s)], LINE),
        line(x, tip_y + 14 * s, x, y - 30 * s, LINE_FINE),  # fuller
        # guard
        rrect(x - 38 * s, y - 24 * s, 76 * s, 16 * s, 6 * s, LINE),
        # grip
        rrect(x - 11 * s, y - 8 * s, 22 * s, 70 * s, 7 * s, LINE),
        line(x - 11 * s, y + 8 * s, x + 11 * s, y + 8 * s, LINE_FINE),
        line(x - 11 * s, y + 24 * s, x + 11 * s, y + 24 * s, LINE_FINE),
        # pommel
        circle(x, y + 70 * s, 13 * s, LINE),
        # power sparkles along blade
        star(x - 34 * s, tip_y + 60 * s, 9 * s, LINE_FINE),
        star(x + 30 * s, tip_y + 110 * s, 7 * s, LINE_FINE),
    ]
    return "".join(out)


def headphones(cx, cy, r):
    return (path(f"M {cx - r} {cy - r*0.2} "
                 f"A {r*1.05} {r*1.05} 0 0 1 {cx + r} {cy - r*0.2}", LINE_BOLD) +
            rrect(cx - r - 14, cy - r * 0.25, 26, 50, 10, LINE) +
            rrect(cx + r - 12, cy - r * 0.25, 26, 50, 10, LINE))


def demon_horns(cx, cy, r):
    """Little curved horns for the friendly demon characters."""
    return (path(f"M {cx - r*0.55} {cy - r*0.78} "
                 f"q {-r*0.35} {-r*0.55} {r*0.05} {-r*0.9}", LINE) +
            path(f"M {cx + r*0.55} {cy - r*0.78} "
                 f"q {r*0.35} {-r*0.55} {-r*0.05} {-r*0.9}", LINE))


# --------------------------------------------------------------------------
# Full characters. Each returns an SVG group string.
# --------------------------------------------------------------------------

def idol_girl_singing(cx, top):
    """Idol girl mid-song with a microphone and a little hunter sword sheathed."""
    r = 92                      # head radius
    hcy = top + r + 18          # head center y
    body_top = hcy + r
    out = []

    # body / stage dress
    out.append(path(f"M {cx - 58} {body_top + 8} "
                    f"L {cx - 46} {body_top + 250} "
                    f"L {cx + 46} {body_top + 250} "
                    f"L {cx + 58} {body_top + 8} Z", LINE_BOLD))
    # skirt frill
    out.append(path(f"M {cx - 46} {body_top + 250} q 18 30 36 0 q 18 30 36 0 "
                    f"q 18 30 36 0 q 18 30 36 0", LINE))
    # belt + star buckle
    out.append(line(cx - 53, body_top + 96, cx + 53, body_top + 96, LINE))
    out.append(star(cx, body_top + 96, 16, LINE_FINE))
    # arm up holding mic
    out.append(path(f"M {cx + 50} {body_top + 30} Q {cx + 120} {body_top - 10} "
                    f"{cx + 138} {body_top - 70}", LINE_BOLD))
    out.append(microphone(cx + 150, body_top - 92, 1.0))
    # other arm out
    out.append(path(f"M {cx - 50} {body_top + 30} Q {cx - 110} {body_top + 70} "
                    f"{cx - 120} {body_top + 130}", LINE_BOLD))
    # legs / boots
    out.append(line(cx - 22, body_top + 250, cx - 22, body_top + 330, LINE_BOLD))
    out.append(line(cx + 22, body_top + 250, cx + 22, body_top + 330, LINE_BOLD))
    out.append(rrect(cx - 40, body_top + 326, 38, 30, 10, LINE))
    out.append(rrect(cx + 4, body_top + 326, 38, 30, 10, LINE))

    # head
    out.append(circle(cx, hcy, r, LINE_BOLD))
    out.append(chibi_eyes(cx, hcy + 8, 36, 26))
    out.append(smile(cx, hcy + 52, 26, open_mouth=True))
    out.append(blush(cx, hcy + 40, 60, 13))
    out.append(hair_long(cx, hcy, r))
    # star hair clip
    out.append(star(cx - r * 0.7, hcy - r * 0.6, 14, LINE_FINE))
    return _group(out)


def idol_boy_dancing(cx, top):
    """Idol boy with light stick and headphones, mid pose."""
    r = 90
    hcy = top + r + 18
    body_top = hcy + r
    out = []

    # jacket body
    out.append(rrect(cx - 60, body_top, 120, 200, 26, LINE_BOLD))
    out.append(line(cx, body_top + 6, cx, body_top + 190, LINE))   # zipper
    out.append(line(cx - 60, body_top + 70, cx - 30, body_top + 90, LINE))  # lapel
    out.append(line(cx + 60, body_top + 70, cx + 30, body_top + 90, LINE))
    # collar
    out.append(path(f"M {cx - 36} {body_top + 2} L {cx} {body_top + 34} "
                    f"L {cx + 36} {body_top + 2}", LINE))
    # arm up with light stick
    out.append(path(f"M {cx + 58} {body_top + 24} Q {cx + 128} {body_top - 6} "
                    f"{cx + 140} {body_top - 64}", LINE_BOLD))
    out.append(light_stick(cx + 150, body_top - 84, 0.95))
    # arm pointing
    out.append(path(f"M {cx - 58} {body_top + 24} Q {cx - 124} {body_top + 50} "
                    f"{cx - 150} {body_top + 18}", LINE_BOLD))
    # legs
    out.append(line(cx - 26, body_top + 198, cx - 40, body_top + 300, LINE_BOLD))
    out.append(line(cx + 26, body_top + 198, cx + 46, body_top + 296, LINE_BOLD))
    out.append(rrect(cx - 62, body_top + 296, 40, 28, 10, LINE))
    out.append(rrect(cx + 26, body_top + 292, 40, 28, 10, LINE))

    # head
    out.append(circle(cx, hcy, r, LINE_BOLD))
    out.append(chibi_eyes(cx, hcy + 6, 34, 24))
    out.append(smile(cx, hcy + 48, 22))
    out.append(hair_short(cx, hcy, r))
    out.append(headphones(cx, hcy, r))
    return _group(out)


def friendly_demon(cx, top):
    """A small, cute hunter-buddy demon — round, fluffy, with horns & a tail."""
    r = 100
    hcy = top + r + 20
    body_top = hcy + r * 0.6
    out = []

    # round fluffy body
    out.append(ellipse(cx, body_top + 120, 120, 130, LINE_BOLD))
    # tummy
    out.append(ellipse(cx, body_top + 140, 70, 80, LINE_FINE))
    # arms
    out.append(path(f"M {cx - 110} {body_top + 110} q -40 20 -30 70", LINE_BOLD))
    out.append(path(f"M {cx + 110} {body_top + 110} q 40 20 30 70", LINE_BOLD))
    out.append(circle(cx - 138, body_top + 188, 22, LINE))
    out.append(circle(cx + 138, body_top + 188, 22, LINE))
    # feet
    out.append(ellipse(cx - 50, body_top + 240, 38, 26, LINE))
    out.append(ellipse(cx + 50, body_top + 240, 38, 26, LINE))
    # spaded tail
    out.append(path(f"M {cx + 118} {body_top + 200} q 60 30 70 -30", LINE_BOLD))
    out.append(poly([(cx + 188, body_top + 170), (cx + 168, body_top + 150),
                     (cx + 208, body_top + 150)], LINE))

    # head (overlaps body — big cute face)
    out.append(circle(cx, hcy, r, LINE_BOLD))
    out.append(demon_horns(cx, hcy, r))
    # bat-ish ears
    out.append(path(f"M {cx - r*0.92} {hcy - r*0.25} q -55 -10 -70 40 q 45 6 70 -22", LINE))
    out.append(path(f"M {cx + r*0.92} {hcy - r*0.25} q 55 -10 70 40 q -45 6 -70 -22", LINE))
    out.append(chibi_eyes(cx, hcy + 6, 40, 30))
    out.append(smile(cx, hcy + 56, 30, open_mouth=True))
    # little fangs
    out.append(poly([(cx - 18, hcy + 56), (cx - 10, hcy + 74), (cx - 2, hcy + 56)], LINE_FINE))
    out.append(poly([(cx + 18, hcy + 56), (cx + 10, hcy + 74), (cx + 2, hcy + 56)], LINE_FINE))
    out.append(blush(cx, hcy + 44, 66, 14))
    return _group(out)


# --------------------------------------------------------------------------
# Page assembly.
# --------------------------------------------------------------------------

def _group(parts):
    return "<g>" + "".join(parts) + "</g>"


def _bubble_title(text):
    """Big outlined 'bubble' title centered near the top — colorable letters."""
    safe = html.escape(text.upper())
    return (f'<text x="{PAGE_W/2}" y="120" text-anchor="middle" '
            f'font-family="Arial Black, Arial, sans-serif" font-size="62" '
            f'font-weight="900" fill="white" stroke="black" stroke-width="3" '
            f'paint-order="stroke" letter-spacing="2">{safe}</text>')


def _footer(text):
    safe = html.escape(text)
    return (f'<text x="{PAGE_W/2}" y="{PAGE_H-34}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="20" fill="black" '
            f'opacity="0.65">{safe}</text>')


def _border():
    """Decorative star-and-music-note border so each page feels like a book."""
    m = 28
    out = [rrect(m, m, PAGE_W - 2 * m, PAGE_H - 2 * m, 26, LINE)]
    out.append(rrect(m + 12, m + 12, PAGE_W - 2 * (m + 12), PAGE_H - 2 * (m + 12),
                     20, LINE_FINE))
    # corner stars
    for x, y in [(m + 38, m + 38), (PAGE_W - m - 38, m + 38),
                 (m + 38, PAGE_H - m - 38), (PAGE_W - m - 38, PAGE_H - m - 38)]:
        out.append(star(x, y, 22, LINE_FINE))
    return "".join(out)


def page(title, body_svg, footer="K-Pop Demon Hunters Coloring Book",
         border=True, decorate=True):
    extras = []
    if decorate:
        extras.append(star(120, 190, 24, LINE_FINE))
        extras.append(music_note(PAGE_W - 130, 200, 24, LINE_FINE))
        extras.append(heart(150, PAGE_H - 150, 22, LINE_FINE))
        extras.append(star(PAGE_W - 140, PAGE_H - 150, 26, LINE_FINE))
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PAGE_W} {PAGE_H}" '
        f'width="{PAGE_W}" height="{PAGE_H}">',
        f'<rect width="{PAGE_W}" height="{PAGE_H}" fill="white"/>',
        _border() if border else "",
        _bubble_title(title) if title else "",
        "".join(extras),
        body_svg,
        _footer(footer),
        "</svg>",
    ]
    return "\n".join(p for p in svg if p)


# --------------------------------------------------------------------------
# Individual pages.
# --------------------------------------------------------------------------

def page_cover():
    out = []
    # crossed sword + microphone emblem
    cx, cy = PAGE_W / 2, 470
    out.append(f'<g transform="rotate(-22 {cx} {cy})">{hunter_sword(cx-70, cy+150, 230)}</g>')
    out.append(f'<g transform="rotate(22 {cx} {cy})">{microphone(cx+70, cy-40, 2.2)}</g>')
    # big banner star behind
    out.append(star(cx, cy - 20, 230, LINE, inner_ratio=0.5))
    out.append(star(cx, cy - 20, 230, LINE, inner_ratio=0.5))
    # floating notes & hearts
    for x, y, s in [(170, 360, 28), (690, 380, 24), (210, 720, 22), (660, 720, 26)]:
        out.append(music_note(x, y, s, LINE))
    out.append(heart(PAGE_W / 2, 800, 40, LINE))
    # subtitle plate
    out.append(rrect(PAGE_W/2 - 250, 850, 500, 110, 26, LINE))
    out.append(f'<text x="{PAGE_W/2}" y="905" text-anchor="middle" '
               f'font-family="Arial Black, Arial, sans-serif" font-size="34" '
               f'font-weight="900" fill="white" stroke="black" stroke-width="2" '
               f'paint-order="stroke">A COLORING BOOK</text>')
    out.append(f'<text x="{PAGE_W/2}" y="945" text-anchor="middle" '
               f'font-family="Arial, sans-serif" font-size="22" fill="black">'
               f'This book belongs to: _______________</text>')
    return page("K-Pop Demon Hunters", "".join(out),
                footer="Color me in!  •  Ages 4+", decorate=False)


def page_idol_girl():
    return page("Star Singer", idol_girl_singing(PAGE_W / 2 - 10, 200))


def page_idol_boy():
    return page("Dance Idol", idol_boy_dancing(PAGE_W / 2, 200))


def page_demon_buddy():
    return page("Demon Buddy", friendly_demon(PAGE_W / 2, 220))


def page_duo_stage():
    """Two idols on a stage with spotlights — a fuller scene."""
    out = []
    # stage floor
    out.append(line(70, 930, PAGE_W - 70, 930, LINE_BOLD))
    out.append(path(f"M 70 930 L 150 1000 M {PAGE_W-70} 930 L {PAGE_W-150} 1000", LINE))
    out.append(line(150, 1000, PAGE_W - 150, 1000, LINE))
    # spotlights
    for sx in (190, PAGE_W - 190):
        out.append(poly([(sx, 200), (sx - 70, 360), (sx + 70, 360)], LINE, closed=False))
        out.append(line(sx - 70, 360, sx + 70, 360, LINE_FINE))
    # two smaller characters
    out.append(f'<g transform="translate(-150 350) scale(0.62)">'
               f'{idol_girl_singing(PAGE_W/2, 60)}</g>')
    out.append(f'<g transform="translate(150 350) scale(0.62)">'
               f'{idol_boy_dancing(PAGE_W/2, 60)}</g>')
    # floating notes
    out.append(music_note(PAGE_W/2 - 30, 300, 30, LINE))
    out.append(music_note(PAGE_W/2 + 60, 360, 22, LINE))
    return page("Showtime!", "".join(out))


def page_props():
    """Magic hunter gear to color: sword, light stick, talisman, headphones."""
    out = []
    out.append(f'<g transform="translate(190 80)">{hunter_sword(0, 380, 300, 1.2)}</g>')
    out.append(f'<g transform="translate(470 120)">{light_stick(0, 320, 1.6)}</g>')
    # talisman (paper charm with a star)
    tx, ty = 230, 760
    out.append(rrect(tx - 70, ty - 110, 140, 220, 14, LINE_BOLD))
    out.append(rrect(tx - 50, ty - 88, 100, 176, 10, LINE_FINE))
    out.append(star(tx, ty - 30, 40, LINE))
    out.append(line(tx, ty + 30, tx, ty + 86, LINE_FINE))
    out.append(line(tx - 30, ty + 50, tx + 30, ty + 50, LINE_FINE))
    # headphones
    out.append(f'<g transform="translate(600 760)">{headphones(0, 0, 90)}{circle(0,0,90,LINE)}</g>')
    # labels
    for x, y, t in [(190, 470, "SWORD"), (470, 480, "LIGHT STICK"),
                    (230, 900, "TALISMAN"), (600, 880, "HEADPHONES")]:
        out.append(f'<text x="{x}" y="{y}" text-anchor="middle" '
                   f'font-family="Arial, sans-serif" font-size="22" '
                   f'fill="black" opacity="0.6">{t}</text>')
    return page("Hunter Gear", "".join(out))


def page_pattern():
    """A simple repeating stars-hearts-notes pattern for the youngest colorers."""
    out = []
    cols, rows = 4, 5
    x0, y0 = 175, 230
    dx = (PAGE_W - 2 * x0) / (cols - 1)
    dy = (PAGE_H - y0 - 150 - 60) / (rows - 1)
    shapes = [
        lambda x, y: star(x, y, 52, LINE),
        lambda x, y: heart(x, y, 48, LINE),
        lambda x, y: music_note(x - 10, y - 10, 44, LINE),
    ]
    i = 0
    for ry in range(rows):
        for cxn in range(cols):
            x = x0 + cxn * dx
            y = y0 + ry * dy
            out.append(shapes[i % len(shapes)](x, y))
            i += 1
        i += 1  # shift the pattern each row
    return page("Pattern Power", "".join(out),
                footer="Color the stars, hearts & notes!")


def page_design_your_idol():
    """Blank-ish idol body so kids design their own demon-hunter outfit & face."""
    cx = PAGE_W / 2
    r = 96
    hcy = 270
    body_top = hcy + r
    out = []
    # plain head, blank face (just a guideline) for them to draw
    out.append(circle(cx, hcy, r, LINE_BOLD))
    out.append(line(cx - 60, hcy + 6, cx - 20, hcy + 6, LINE_FINE))   # eye lines
    out.append(line(cx + 20, hcy + 6, cx + 60, hcy + 6, LINE_FINE))
    out.append(path(f"M {cx-26} {hcy+50} Q {cx} {hcy+66} {cx+26} {hcy+50}", LINE_FINE))
    # simple t-pose body to dress up
    out.append(rrect(cx - 64, body_top, 128, 210, 24, LINE_BOLD))
    out.append(path(f"M {cx-64} {body_top+20} L {cx-150} {body_top+60}", LINE_BOLD))
    out.append(path(f"M {cx+64} {body_top+20} L {cx+150} {body_top+60}", LINE_BOLD))
    out.append(circle(cx - 160, body_top + 70, 20, LINE))
    out.append(circle(cx + 160, body_top + 70, 20, LINE))
    out.append(line(cx - 30, body_top + 210, cx - 30, body_top + 320, LINE_BOLD))
    out.append(line(cx + 30, body_top + 210, cx + 30, body_top + 320, LINE_BOLD))
    out.append(rrect(cx - 50, body_top + 318, 42, 30, 10, LINE))
    out.append(rrect(cx + 8, body_top + 318, 42, 30, 10, LINE))
    # prompt
    out.append(f'<text x="{cx}" y="{PAGE_H-90}" text-anchor="middle" '
               f'font-family="Arial, sans-serif" font-size="24" fill="black">'
               f'Draw a face, hair &amp; a cool outfit — then color it!</text>')
    return page("Design Your Idol", "".join(out))


# --------------------------------------------------------------------------
# Build.
# --------------------------------------------------------------------------

PAGES = [
    ("00-cover", "Cover", page_cover),
    ("01-star-singer", "Star Singer", page_idol_girl),
    ("02-dance-idol", "Dance Idol", page_idol_boy),
    ("03-demon-buddy", "Demon Buddy", page_demon_buddy),
    ("04-showtime", "Showtime!", page_duo_stage),
    ("05-hunter-gear", "Hunter Gear", page_props),
    ("06-pattern-power", "Pattern Power", page_pattern),
    ("07-design-your-idol", "Design Your Idol", page_design_your_idol),
]


def build():
    os.makedirs(PAGES_DIR, exist_ok=True)
    rendered = []
    for slug, title, fn in PAGES:
        svg = fn()
        out_path = os.path.join(PAGES_DIR, f"{slug}.svg")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg)
        rendered.append((slug, title, svg))
        print(f"  wrote pages/{slug}.svg")

    # Combined printable HTML book.
    book_path = os.path.join(HERE, "coloring-book.html")
    pages_html = "\n".join(
        f'<section class="page" aria-label="{html.escape(t)}">{svg}</section>'
        for _, t, svg in rendered
    )
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>K-Pop Demon Hunters — Coloring Book</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ margin: 0; background: #f3f3f7; font-family: Arial, sans-serif; }}
  .hint {{ max-width: 820px; margin: 24px auto; padding: 0 16px; color: #333; }}
  .hint h1 {{ margin: 0 0 6px; }}
  .page {{
    display: block; width: 850px; max-width: 96vw; margin: 24px auto;
    background: white; box-shadow: 0 2px 14px rgba(0,0,0,.18); border-radius: 8px;
    overflow: hidden;
  }}
  .page svg {{ display: block; width: 100%; height: auto; }}
  @media print {{
    body {{ background: white; }}
    .hint {{ display: none; }}
    .page {{ box-shadow: none; border-radius: 0; margin: 0; width: 100%;
             page-break-after: always; break-after: page; }}
    @page {{ size: letter; margin: 0; }}
  }}
</style>
</head>
<body>
  <div class="hint">
    <h1>K-Pop Demon Hunters — Coloring Book</h1>
    <p>{len(rendered)} printable pages of original, kid-friendly line art.
       Press <strong>Ctrl/Cmd&nbsp;+&nbsp;P</strong> and choose
       <em>Save as PDF</em> (or print) — pages are sized for US&nbsp;Letter.
       Each <code>.svg</code> in <code>pages/</code> also prints on its own.</p>
  </div>
  {pages_html}
</body>
</html>"""
    with open(book_path, "w", encoding="utf-8") as f:
        f.write(doc)
    print(f"  wrote coloring-book.html ({len(rendered)} pages)")

    # Landing gallery (the localhost home page).
    cards = []
    for slug, t, svg in rendered:
        cards.append(f"""
      <a class="card" href="pages/{slug}.svg" target="_blank" rel="noopener">
        <div class="thumb">{svg}</div>
        <div class="cap">{html.escape(t)}</div>
      </a>""")
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>K-Pop Demon Hunters — Coloring Book</title>
<style>
  body {{ margin:0; font-family:Arial, sans-serif; color:#1b1b29;
          background:#f4f4fb; }}
  header {{ text-align:center; padding:34px 16px 10px; }}
  header h1 {{ margin:0; font-size:34px; letter-spacing:1px; }}
  header p {{ margin:8px 0 0; color:#555; }}
  .bar {{ text-align:center; margin:18px 0 8px; }}
  .bar a {{ display:inline-block; background:#1b1b29; color:#fff;
            text-decoration:none; padding:12px 22px; border-radius:999px;
            font-weight:bold; }}
  .grid {{ display:grid; gap:20px; padding:24px;
           grid-template-columns:repeat(auto-fill, minmax(220px, 1fr));
           max-width:1100px; margin:0 auto; }}
  .card {{ background:#fff; border-radius:14px; overflow:hidden;
           box-shadow:0 2px 10px rgba(0,0,0,.12); text-decoration:none;
           color:inherit; transition:transform .12s, box-shadow .12s; }}
  .card:hover {{ transform:translateY(-3px);
                 box-shadow:0 8px 20px rgba(0,0,0,.18); }}
  .thumb {{ aspect-ratio:850/1100; background:#fff; border-bottom:1px solid #eee; }}
  .thumb svg {{ display:block; width:100%; height:100%; }}
  .cap {{ padding:12px 14px; font-weight:bold; text-align:center; }}
  footer {{ text-align:center; color:#888; padding:10px 16px 34px; font-size:14px; }}
</style>
</head>
<body>
  <header>
    <h1>🎤 K-Pop Demon Hunters 🗡️</h1>
    <p>Children's coloring book — {len(rendered)} printable pages. Tap a page to open it.</p>
  </header>
  <div class="bar">
    <a href="coloring-book.html">📖 Open the full printable book (Save as PDF)</a>
  </div>
  <div class="grid">{''.join(cards)}
  </div>
  <footer>Original, kid-friendly line art • print on US Letter</footer>
</body>
</html>"""
    index_path = os.path.join(HERE, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"  wrote index.html (gallery)")
    return book_path


def main():
    ap = argparse.ArgumentParser(description="Build the coloring book.")
    ap.add_argument("--list", action="store_true", help="list pages and exit")
    args = ap.parse_args()
    if args.list:
        for slug, title, _ in PAGES:
            print(f"{slug:24} {title}")
        return
    print("Building K-Pop Demon Hunters coloring book...")
    build()
    print("Done. Open coloring_book/coloring-book.html and print to PDF.")


if __name__ == "__main__":
    main()
