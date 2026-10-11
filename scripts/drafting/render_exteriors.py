"""Exterior renderings of the P68 in Blender: at port, at anchor, underway, and at anchor at dusk.

The vessel is built by bvessel.py from the repository's main dimensions; lines, rig
heights and sail plan are illustrative. Output: drawings/renders/exterior/.
Run: python3 scripts/drafting/render_exteriors.py [port|anchor|underway|dusk ...] [--fast]
"""
from __future__ import annotations

import math
import sys

from PIL import Image, ImageDraw, ImageFont

import bkit as K
import bvessel as V
import p68

OUT = p68.OUT / 'renders' / 'exterior'
FAST = '--fast' in sys.argv
W, H = (1280, 720) if FAST else (2560, 1440)
import os as _os

def _font(names):
    """First installed font from a list of paths (DejaVu on Linux, Arial on macOS)."""
    for n in names:
        if _os.path.exists(n):
            return n
    raise FileNotFoundError(f'no font found in {names}')


FONT = _font(['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf'])
FONT_B = _font(['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'])

SKY = 0.06  # physical sky with sun disc, scaled to a daylight exposure

CAPTION = 'Illustrative render from the concept model: hull lines, rig heights and sail plan are not set. Not for construction.'


def caption(path, title, sub):
    img = Image.open(path).convert('RGB')
    s = img.size[0] / 2560
    dr = ImageDraw.Draw(img, 'RGBA')
    dr.rectangle([0, img.size[1] - int(120 * s), img.size[0], img.size[1]], fill=(8, 18, 26, 150))
    dr.text((int(50 * s), img.size[1] - int(100 * s)), title, font=ImageFont.truetype(FONT_B, int(40 * s)), fill=(245, 242, 235))
    dr.text((int(50 * s), img.size[1] - int(48 * s)), f'{sub} · {CAPTION}', font=ImageFont.truetype(FONT, int(22 * s)), fill=(210, 215, 218))
    out = path.with_name(path.stem.lstrip('_') + '.jpg')
    img.save(out, quality=90, optimize=True, progressive=True)
    path.unlink()
    print(f'wrote {out.relative_to(p68.ROOT)}')


def at_port():
    K.reset(samples=32 if FAST else 128, width=W, height=H)
    K.sky(elevation_deg=11, rotation_deg=215, strength=SKY * 1.4)
    M = K.lib()
    V.build_vessel(M)
    V.vessel_parent()
    V.water(M, wave_scale=0.08, wind=3, chop=0.3, color='#123f52')
    K.collection('Harbour')
    # Stern-to Med mooring: quay along the transom.
    K.box('Quay', -60, -80, -3, -6, 90, 1.6, M['quay'], bevel=0.1)
    K.box('Quay edge', -6.3, -80, 1.3, -6, 90, 1.7, M['stone_top'])
    for y in (-14, -4, 6, 16):
        K.cylinder('Bollard', -7.2, y, 1.6, 0.25, 0.6, M['rubber'], 20)
    for y in (-2.4, 2.4):
        K.rod('Stern line', (0.0, y, 3.8), (-7.2, y * 1.6, 2.0), 0.04, M['rope'])
    # Passerelle from the swim platform to the quay.
    K.box('Passerelle', -6.2, -0.5, 1.75, -1.4, 0.5, 1.82, M['teak_plain'])
    for y in (-0.5, 0.5):
        K.rod('Passerelle rail', (-6.2, y, 2.7), (-1.4, y, 2.75), 0.02, M['chrome'])
    # Village rising behind the quay, to the stern.
    K.collection('Village')
    for i, (yy0, yy1) in enumerate(((-75, -20), (20, 80))):
        _houses(M, -55, -14, yy0, yy1, seed=i)
    V.island(M, -150, 10, 120, 170, 70, seed=9, z0=-1, village_at=(-90, 10, 30, 90))
    K.camera((96, -66, 9), (8, 6, 16), lens=30)
    tmp = OUT / '_port.png'
    K.render(tmp)
    caption(tmp, 'At port · stern-to on the quay', 'Golden hour, Cyclades')


def _houses(M, x0, x1, y0, y1, seed=0):
    import random
    rnd = random.Random(seed)
    y = y0
    while y < y1:
        d = rnd.uniform(5, 9)
        x = x1
        level = 0
        while x > x0:
            w = rnd.uniform(5, 8)
            zz = 1.6 + level * 2.4
            h = rnd.uniform(3.2, 6.5)
            K.box('House', x - w, y, zz - 4, x, y + d - 0.6, zz + h, M['white_render'], bevel=0.15)
            if rnd.random() < 0.7:
                K.box('Door', x + 0.01, y + d / 2 - 0.5, zz, x + 0.08, y + d / 2 + 0.5, zz + 2.1, M['blue_door'])
            if rnd.random() < 0.6:
                K.box('Window', x + 0.01, y + 0.8, zz + 2.4, x + 0.08, y + 1.7, zz + 3.3, M['blue_door'])
            x -= w + rnd.uniform(0, 2)
            level += 1
        y += d


def at_anchor(dusk=False):
    K.reset(samples=32 if FAST else (192 if dusk else 128), width=W, height=H)
    if dusk:
        K.sky(elevation_deg=1.5, rotation_deg=265, strength=0.35, sun_disc=False)
        K.sun(elev=2, azim=265, energy=1.2, angle=2, color=(1.0, 0.6, 0.4))
    else:
        K.sky(elevation_deg=48, rotation_deg=150, strength=SKY)
    M = K.lib()
    V.build_vessel(M, night=dusk)
    V.vessel_parent(yaw_deg=-8)
    V.water(M, wave_scale=0.15, wind=4, chop=0.5, color='#0f5f7a' if not dusk else '#123447', shallow=None if dusk else '#15647a')
    K.collection('Bay')
    # Anchor chain from the bow into the water, tender at the swim platform.
    K.rod('Anchor chain', (66.8, -0.5, 4.4), (73, -1.2, -0.3), 0.06, M['steel'])
    V.build_tender(M, -6.5, 4.5, rot=math.radians(80))
    V.island(M, -230, 360, 260, 160, 80, seed=4, village_at=(-200, 300, 40, 60))
    V.island(M, -520, 120, 200, 150, 50, seed=7)
    V.island(M, 120, 560, 320, 170, 105, seed=11)
    if dusk:
        for x in range(10, 56, 6):
            K.point_light((x, 0, 5.0), 120, 0.3, (1.0, 0.75, 0.45))
            K.point_light((x, 0, 8.0), 90, 0.3, (1.0, 0.75, 0.45))
        K.point_light((14, 0, 6.2), 220, 0.6, (0.4, 0.8, 1.0))  # pool glow
    K.camera((128, -92, 7.5), (32, 0, 17), lens=38)
    tmp = OUT / ('_dusk.png' if dusk else '_anchor.png')
    K.render(tmp)
    if dusk:
        caption(tmp, 'At anchor · dusk', 'Interior and Lido lighting on')
    else:
        caption(tmp, 'At anchor in a Cycladic bay', 'Tender at the swim platform')


def underway():
    K.reset(samples=32 if FAST else 128, width=W, height=H)
    K.sky(elevation_deg=32, rotation_deg=135, strength=SKY)
    M = K.lib()
    V.build_vessel(M, sails=True, boom_angle=math.radians(14))
    V.vessel_parent(heel_deg=9, yaw_deg=0)
    V.water(M, wave_scale=1.2, wind=11, chop=1.1, color='#0d3f5e', foam=True, resolution=15)
    K.collection('Wake')
    foam = K.principled('Wake foam', (0.9, 0.93, 0.95), rough=0.6, alpha=1.0)
    import random
    rnd = random.Random(2)
    for i in range(70):
        x = rnd.uniform(-60, 2)
        spread = 2 + abs(x) * 0.25
        y = rnd.choice((-1, 1)) * rnd.uniform(0.5, spread)
        K.cbox('Wake', x, y, 0.25, rnd.uniform(1.5, 5), rnd.uniform(0.3, 1.2), 0.05, foam, rot=rnd.uniform(-0.3, 0.3), bevel=0.02)
    for i in range(20):
        x = rnd.uniform(40, 68)
        side = rnd.choice((-1, 1))
        y = side * (V.hb_render(x) + rnd.uniform(0.0, 1.0))
        K.cbox('Bow wave', x, y, 0.3, rnd.uniform(1.5, 3), rnd.uniform(0.3, 0.8), 0.06, foam, rot=side * 0.4, bevel=0.02)
    K.camera((112, -92, 10), (30, 0, 22), lens=30)
    tmp = OUT / '_underway.png'
    K.render(tmp)
    caption(tmp, 'Underway under sail', 'Close reach, about 7° heel')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    want = [a for a in sys.argv[1:] if not a.startswith('--')] or ['port', 'anchor', 'underway', 'dusk']
    for w in want:
        {'port': at_port, 'anchor': at_anchor, 'underway': underway, 'dusk': lambda: at_anchor(dusk=True)}[w]()


if __name__ == '__main__':
    main()
