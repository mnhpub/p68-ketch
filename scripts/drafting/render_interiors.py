"""Interior renderings in Blender: features, accommodation and controls.

Rooms come from the DXF sources (room polylines and wall lines); finishes and
furniture follow layout/finishes.json and bfurnish.py. Walls with nothing on the
other side are glazed on the upper levels and get portholes on Tween, so the sea and
sky read through them. The outdoor pilot house and the Lido use the exterior vessel
model. Output: drawings/renders/interior/.
Run: python3 scripts/drafting/render_interiors.py [shot ...] [--fast]
"""
from __future__ import annotations

import math
import sys

from PIL import Image, ImageDraw, ImageFont

import bfurnish
import bkit as K
import bvessel as V
import p68

OUT = p68.OUT / 'renders' / 'interior'
FAST = '--fast' in sys.argv
W, H = (1200, 675) if FAST else (2400, 1350)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONT_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
CEILING = 2.5
SKY = 0.06

# key: (deck index, room name, title, category, eye (fx, fy, z), target (fx, fy, z), lens)
# Eye and target are fractions of the room rectangle (0 = aft / starboard edge, 1 = forward / port edge).
SHOTS = {
    'salon': (3, 'Main salon / dining', 'Main salon and dining', 'Feature', (0.06, 0.12, 1.5), (0.75, 0.62, 1.1), 22),
    'owner-suite': (3, 'Owner suite', 'Owner suite', 'Accommodation', (0.12, 0.15, 1.55), (0.7, 0.75, 0.8), 20),
    'vip-cabin': (3, 'VIP accommodation', 'VIP cabin', 'Accommodation', (0.08, 0.2, 1.5), (0.85, 0.7, 0.8), 20),
    'guest-cabin': (4, 'Guest cabins', 'Guest cabin, Tween', 'Accommodation', (0.06, 0.18, 1.5), (0.45, 0.8, 0.7), 18),
    'accessible-cabin': (4, 'Accessible guest cabin', 'Accessible guest cabin, Tween', 'Accommodation', (0.95, 0.1, 1.45), (0.25, 0.7, 0.6), 18),
    'bridge-helm': (1, 'Command position', 'Bridge helm and command position', 'Controls', (0.03, 0.12, 1.75), (1.05, 0.62, 1.0), 15),
    'chart-library': (1, 'Chart library', 'Chart library, Bridge', 'Feature', (0.04, 0.2, 1.55), (0.9, 0.85, 1.0), 20),
    'main-lift-lobby': (3, 'Main lift lobby', 'Main lift lobby', 'Feature', (0.08, 0.5, 1.55), (1.3, 0.5, 1.2), 22),
    'observation-lounge': (2, 'Observation lounge', 'Observation lounge, Commander', 'Feature', (0.05, 0.15, 1.5), (0.95, 0.7, 1.0), 20),
    'galley': (3, 'Professional galley', 'Professional galley', 'Feature', (0.03, 0.5, 1.65), (0.95, 0.45, 0.9), 20),
    'technical-corridor': (5, 'Technical access corridor', 'Technical access corridor, Tank deck', 'Controls', (0.95, 0.5, 1.6), (0.0, 0.5, 1.0), 20),
}
VESSEL_SHOTS = {
    'pilot-house': ('Outdoor pilot house helm, roof +9.30 m', 'Controls'),
    'lido-pool': ('Aft Lido and pool, Commander +6.60 m', 'Feature'),
}


def caption(path, title, category):
    img = Image.open(path).convert('RGB')
    s = img.size[0] / 2400
    dr = ImageDraw.Draw(img, 'RGBA')
    dr.rectangle([0, img.size[1] - int(108 * s), img.size[0], img.size[1]], fill=(8, 18, 26, 160))
    dr.text((int(46 * s), img.size[1] - int(92 * s)), f'{category.upper()} · {title}', font=ImageFont.truetype(FONT_B, int(34 * s)), fill=(245, 242, 235))
    dr.text((int(46 * s), img.size[1] - int(44 * s)),
            'Finish-out concept render from the DXF layout · proposed finishes, indicative furniture · not a coordinated interior design',
            font=ImageFont.truetype(FONT, int(20 * s)), fill=(210, 215, 218))
    out = path.with_name(path.stem.lstrip('_') + '.jpg')
    img.save(out, quality=90, optimize=True, progressive=True)
    path.unlink()
    print(f'wrote {out.relative_to(p68.ROOT)}')


def inside(cd, x, y):
    return any(r.x0 - 1e-3 <= x <= r.x1 + 1e-3 and r.y0 - 1e-3 <= y <= r.y1 + 1e-3 for r in cd.rooms)


def exterior_wall(cd, seg):
    """True when one side of the wall line is outside every room."""
    (x0, y0), (x1, y1) = seg
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    if abs(x1 - x0) < 1e-6:
        a, b = (mx - 0.2, my), (mx + 0.2, my)
    else:
        a, b = (mx, my - 0.2), (mx, my + 0.2)
    return inside(cd, *a) != inside(cd, *b)


def build_interior(deck: p68.Deck, M):
    K.collection(deck.name)
    cd = K.read_deck(deck)
    z = cd.z
    K.build_floors(cd, z)
    portholes = deck.name in ('Tween', 'Tank / Technical')
    wall_m = M['wall']
    panel = M['walnut']
    t = 0.12
    for i, seg in enumerate(cd.walls):
        (x0, y0), (x1, y1) = seg
        vertical = abs(x1 - x0) < 1e-6
        lo = (x0 - t / 2, min(y0, y1) - t / 2) if vertical else (min(x0, x1) - t / 2, y0 - t / 2)
        hi = (x0 + t / 2, max(y0, y1) + t / 2) if vertical else (max(x0, x1) + t / 2, y0 + t / 2)
        if exterior_wall(cd, seg) and deck.name != 'Tank / Technical':
            if portholes:
                K.box(f'W{i}', *lo, z, *hi, z + CEILING, wall_m)
                n = int((max(abs(x1 - x0), abs(y1 - y0))) / 1.6)
                day = K.principled('Porthole daylight', (0.8, 0.9, 1.0), rough=0.1, emission=(0.75, 0.88, 1.0), estrength=2.0)
                for k in range(n):
                    f = (k + 0.5) / n
                    px, py = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
                    if vertical:
                        K.box(f'PortRing{i}{k}', px - t / 2 - 0.015, py - 0.3, z + 1.05, px + t / 2 + 0.015, py + 0.3, z + 1.65, M['brass'])
                        K.box(f'PortG{i}{k}', px - t / 2 - 0.02, py - 0.24, z + 1.11, px + t / 2 + 0.02, py + 0.24, z + 1.59, day)
                    else:
                        K.box(f'PortRing{i}{k}', px - 0.3, py - t / 2 - 0.015, z + 1.05, px + 0.3, py + t / 2 + 0.015, z + 1.65, M['brass'])
                        K.box(f'PortG{i}{k}', px - 0.24, py - t / 2 - 0.02, z + 1.11, px + 0.24, py + t / 2 + 0.02, z + 1.59, day)
            else:
                K.box(f'Wsill{i}', *lo, z, *hi, z + 0.7, panel)
                K.box(f'Wglass{i}', *lo, z + 0.7, *hi, z + 2.25, M['glass'])
                K.box(f'Whead{i}', *lo, z + 2.25, *hi, z + CEILING, wall_m)
                # Mullions every 2 m.
                L = max(abs(x1 - x0), abs(y1 - y0))
                for k in range(1, int(L / 2.0) + 1):
                    f = k * 2.0 / L
                    if f >= 1:
                        break
                    px, py = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
                    K.box(f'Mull{i}{k}', px - 0.04, py - 0.04, z + 0.7, px + 0.04, py + 0.04, z + 2.25, M['brass'])
        else:
            K.box(f'W{i}', *lo, z, *hi, z + CEILING, wall_m)
            K.box(f'Wainscot{i}', lo[0] - 0.012, lo[1] - 0.012, z, hi[0] + 0.012, hi[1] + 0.012, z + 1.0, panel)
            K.box(f'Rail{i}', lo[0] - 0.02, lo[1] - 0.02, z + 1.0, hi[0] + 0.02, hi[1] + 0.02, z + 1.03, M['brass'])
    # Indicative cabin partitions, with an ensuite door gap at the passage end.
    for i, ((x0, y0), (x1, y1)) in enumerate(cd.partitions or []):
        K.box(f'Prtn{i}', x0 - 0.05, min(y0, y1), z, x0 + 0.05, max(y0, y1), z + CEILING, wall_m)
        K.box(f'PrtnPanel{i}', x0 - 0.062, min(y0, y1), z, x0 + 0.062, max(y0, y1), z + 1.0, panel)
    # Ceilings with a light cove and downlights.
    for r in cd.rooms:
        K.box(f'Ceil {r.name}', r.x0, r.y0, z + CEILING, r.x1, r.y1, z + CEILING + 0.06, M['wall'])
        cove = K.principled('Cove light', (1, 0.9, 0.75), emission=(1, 0.86, 0.66), estrength=6.0)
        if r.w > 2 and r.d > 1.6:
            K.box(f'Cove {r.name}', r.x0 + 0.35, r.y0 + 0.35, z + CEILING - 0.01, r.x1 - 0.35, r.y0 + 0.4, z + CEILING, cove)
            K.box(f'Cove2 {r.name}', r.x0 + 0.35, r.y1 - 0.4, z + CEILING - 0.01, r.x1 - 0.35, r.y1 - 0.35, z + CEILING, cove)
        nx, ny = max(1, int(r.w / 2.2)), max(1, int(r.d / 2.2))
        for i in range(nx):
            for j in range(ny):
                lx = r.x0 + (i + 0.5) * r.w / nx
                ly = r.y0 + (j + 0.5) * r.d / ny
                K.cylinder('Downlight', lx, ly, z + CEILING - 0.01, 0.06, 0.01, K.principled('Downlight', (1, 1, 1), emission=(1, 0.88, 0.7), estrength=40))
        K.area_light((r.cx, r.cy, z + CEILING - 0.05), min(r.w, 4.0), 60 * min(r.w * r.d, 40) / 10, size_y=min(r.d, 3.0), color=(1.0, 0.86, 0.68))
    for r in cd.rooms:
        bfurnish.furnish(r, z, M)
    # Masts pass through as carbon columns.
    for mx in p68.MASTS.values():
        if any(r.x0 <= mx <= r.x1 and r.y0 <= 0 <= r.y1 for r in cd.rooms) and deck.name != 'Tank / Technical':
            K.cylinder('Mast', mx, 0, z, 0.4, CEILING, M['carbon'], 32)
    # Floor slab and ceiling slab beyond the rooms, so the windows read against the deck structure.
    K.extrude_polygon('Slab', cd.outline, z - 0.3, z - 0.01, M['super'])
    return cd


def room_shot(key):
    idx, room_name, title, category, eye, tgt, lens = SHOTS[key]
    deck = next(d for d in p68.decks() if d.index == idx)
    K.reset(samples=48 if FAST else 160, width=W, height=H)
    K.bpy.context.scene.cycles.max_bounces = 10
    K.sky(elevation_deg=35, rotation_deg=140, strength=SKY)
    M = K.lib()
    cd = build_interior(deck, M)
    V.water(M, wave_scale=0.2, wind=4, chop=0.5, color='#0f5f7a', shallow='#1d8aa0', resolution=10)
    r = next(r for r in cd.rooms if r.name == room_name)
    if r.furniture == 'cabins':
        # Frame one indicative cabin, not the whole block.
        import dataclasses
        n = max(1, round(r.w / 4.5))
        r = dataclasses.replace(r, x1=r.x0 + r.w / n)
    ex = r.x0 + eye[0] * r.w
    ey = r.y0 + eye[1] * r.d
    tx = r.x0 + tgt[0] * r.w
    ty = r.y0 + tgt[1] * r.d
    K.camera((ex, ey, cd.z + eye[2]), (tx, ty, cd.z + tgt[2]), lens=lens)
    if key == 'accessible-cabin':
        # Grab rails and a roll-in shower suggestion in the ensuite.
        K.rod('Grab rail', (r.x0 + 0.3, r.y0 + 0.12, cd.z + 0.85), (r.x0 + 1.4, r.y0 + 0.12, cd.z + 0.85), 0.02, M['chrome'])
    tmp = OUT / f'_{key}.png'
    K.render(tmp)
    caption(tmp, title, category)


def pilot_house():
    K.reset(samples=48 if FAST else 160, width=W, height=H)
    K.sky(elevation_deg=24, rotation_deg=120, strength=SKY)
    M = K.lib()
    V.build_vessel(M)
    V.water(M, wave_scale=0.5, wind=7, chop=0.8, color='#0d4a66')
    # Helm screens and an emergency stop on the outdoor console, hooded for sun.
    for i, y in enumerate((-0.9, -0.3, 0.3, 0.9)):
        scr = K.cbox(f'Helm screen{i}', 10.25, y, 10.3, 0.04, 0.52, 0.36, M['screen' if i % 2 == 0 else 'screen_warm'])
        scr.rotation_euler = (0, math.radians(-20), 0)
    K.cbox('Screen hood', 10.35, 0, 10.72, 0.35, 2.3, 0.04, M['carbon'])
    K.cylinder('E-stop', 10.0, 1.25, 10.3, 0.06, 0.06, M['red'])
    K.cbox('Throttles', 9.85, 0, 10.3, 0.25, 0.4, 0.12, M['chrome'])
    K.camera((7.4, -1.2, 11.0), (14.0, 0.4, 10.6), lens=24)
    tmp = OUT / '_pilot-house.png'
    K.render(tmp)
    caption(tmp, *VESSEL_SHOTS['pilot-house'])


def lido_pool():
    K.reset(samples=48 if FAST else 160, width=W, height=H)
    K.sky(elevation_deg=20, rotation_deg=290, strength=SKY * 1.2)
    M = K.lib()
    V.build_vessel(M)
    V.water(M, wave_scale=0.2, wind=4, chop=0.5, color='#0f5f7a', shallow='#1d8aa0')
    for i, y in enumerate((-2.9, -1.7, 1.7, 2.9)):
        bfurnish.lounger(f'Lido lounger{i}', 9.0, y, 6.62, M)
    bfurnish.table('Lido table', 18.6, 0, 6.62, 2.4, 1.0, 0.74, M, top='teak_plain', legs='chrome')
    for k in range(3):
        bfurnish.chair(f'Lido c{k}a', 17.8 + k * 0.8, -0.8, 6.62, 0.0, M, 'ivory')
        bfurnish.chair(f'Lido c{k}b', 17.8 + k * 0.8, 0.8, 6.62, math.pi, M, 'ivory')
    K.camera((7.2, -3.3, 8.3), (19.0, 0.8, 7.2), lens=22)
    tmp = OUT / '_lido-pool.png'
    K.render(tmp)
    caption(tmp, *VESSEL_SHOTS['lido-pool'])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    want = [a for a in sys.argv[1:] if not a.startswith('--')] or [*SHOTS, *VESSEL_SHOTS]
    for key in want:
        if key == 'pilot-house':
            pilot_house()
        elif key == 'lido-pool':
            lido_pool()
        else:
            room_shot(key)


if __name__ == '__main__':
    main()
