"""Finish-out renderings of each deck, built in Blender from the DXF sources.

For each level:
  finish-plan-NN-<deck>.jpg   top-down orthographic render, walls cut at 1.1 m, proposed
                              floor finishes and indicative furniture, labelled, with a
                              finish legend
  cutaway-NN-<deck>.jpg       perspective cutaway from the aft starboard quarter

Output: drawings/renders/finish/ (copied to public/renders/finish/ by npm run build:renders).
Run: python3 scripts/drafting/render_finish.py [deck-index ...] [--fast]
"""
from __future__ import annotations

import math
import sys

from PIL import Image, ImageDraw, ImageFont

import bfurnish
import bkit as K
import p68

OUT = p68.OUT / 'renders' / 'finish'
FAST = '--fast' in sys.argv
import os as _os

def _font(names):
    """First installed font from a list of paths (DejaVu on Linux, Arial on macOS)."""
    for n in names:
        if _os.path.exists(n):
            return n
    raise FileNotFoundError(f'no font found in {names}')


FONT = _font(['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/System/Library/Fonts/Supplemental/Arial.ttf'])
FONT_B = _font(['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'])

PLAN_W, PLAN_SPAN = 4000, 71.0  # pixels, metres across the plan render
PLAN_H = 860
PLAN_CX, PLAN_CY = 34.0, 0.0


def deck_shell(cd: K.CadDeck, M, z, rim=0.35, depth=0.25):
    """Unassigned deck surface and the hull edge around the level."""
    deck_mat = K.principled('Deck surface', K.srgb('#e7e3da'), rough=0.85)
    K.extrude_polygon('Deck', cd.outline, z - 0.25, z - 0.005, deck_mat)
    # Hull rim: outline offset outward, as a thin wall.
    pts = cd.outline
    for i in range(len(pts)):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1e-6:
            continue
        nx, ny = (y1 - y0) / L, -(x1 - x0) / L  # outward for a counter-clockwise outline
        q = [(x0, y0), (x1, y1), (x1 + nx * 0.18, y1 + ny * 0.18), (x0 + nx * 0.18, y0 + ny * 0.18)]
        K.extrude_polygon(f'Rim{i}', q, z - depth, z + rim, M['hull'])


def build_level(deck: p68.Deck, wall_h: float, cap: bool, depth: float = 0.25):
    K.collection(deck.name)
    M = K.lib()
    cd = K.read_deck(deck)
    z = cd.z
    deck_shell(cd, M, z, depth=depth)
    K.build_floors(cd, z)
    K.build_walls(cd, z, wall_h, M['wall'], cap=M['wall_cap'] if cap else None)
    # Indicative cabin partitions from the DXF, thinner than the walls.
    for i, ((x0, y0), (x1, y1)) in enumerate(cd.partitions or []):
        K.box(f'Prtn{i}', x0 - 0.04, min(y0, y1), z, x0 + 0.04, max(y0, y1), z + wall_h, M['wall'])
        if cap:
            K.box(f'PrtnCap{i}', x0 - 0.04, min(y0, y1), z + wall_h, x0 + 0.04, max(y0, y1), z + wall_h + 0.01, M['wall_cap'])
    for r in cd.rooms:
        bfurnish.furnish(r, z, M)
    # Masts through the level, approximate.
    x0 = min(r.x0 for r in cd.rooms)
    x1 = max(r.x1 for r in cd.rooms)
    for mx in p68.MASTS.values():
        if x0 <= mx <= x1 and deck.name != 'Tank / Technical':
            K.cylinder('Mast', mx, 0, z, 0.4, wall_h + 0.6, M['carbon'])
    return cd


def overlay_plan(path, deck: p68.Deck, cd: K.CadDeck):
    img = Image.open(path).convert('RGB')
    W, H = img.size
    head = 150
    rows = (len({r.finish for r in cd.rooms}) + 3) // 4
    foot = 120 + rows * 80 + 70
    sheet = Image.new('RGB', (W, H + head + foot), (250, 249, 246))
    sheet.paste(img, (0, head))
    dr = ImageDraw.Draw(sheet)
    f_title = ImageFont.truetype(FONT_B, 54)
    f_sub = ImageFont.truetype(FONT, 28)
    f_lab = ImageFont.truetype(FONT_B, 22)
    f_small = ImageFont.truetype(FONT, 19)
    dr.text((60, 30), f'P68 KETCH · FINISH-OUT PLAN · {deck.name.upper()}  {deck.meta["elevation"]}', font=f_title, fill=(16, 32, 39))
    dr.text((60, 98), 'Proposed floor finishes and indicative furniture · rendered in Blender from the DXF source · walls cut at 1.10 m · concept only, not specified',
            font=f_sub, fill=(84, 110, 122))
    ppm = W / PLAN_SPAN

    def px(x, y):
        return (x - PLAN_CX) * ppm + W / 2, head + H / 2 - (y - PLAN_CY) * ppm

    for r in cd.rooms:
        if r.furniture == 'lift':
            continue
        label = r.name.upper() if len(r.name) < 26 else r.name[:24].upper() + '…'
        x, y = px(r.cx, r.cy)
        tw = dr.textlength(label, font=f_lab)
        if tw > r.w * ppm - 10 and r.d * ppm > 220:
            continue
        bx = [x - tw / 2 - 10, y - 16, x + tw / 2 + 10, y + 16]
        dr.rounded_rectangle(bx, 6, fill=(255, 255, 255), outline=(16, 32, 39), width=2)
        dr.text((x, y), label, font=f_lab, fill=(16, 32, 39), anchor='mm')
    # Finish legend.
    used = []
    for r in cd.rooms:
        if r.finish not in used:
            used.append(r.finish)
    ly = head + H + 40
    dr.text((60, ly), 'FINISH LEGEND (PROPOSED)', font=f_lab, fill=(16, 32, 39))
    import textures
    for i, fin in enumerate(used):
        col, row = i % 4, i // 4
        x0, y0 = 60 + col * 980, ly + 45 + row * 80
        sw = textures.to_image(textures.material(fin, 1.2, 0.6, 110)).resize((120, 60))
        sheet.paste(sw, (x0, y0))
        dr.rectangle([x0, y0, x0 + 120, y0 + 60], outline=(16, 32, 39), width=2)
        dr.text((x0 + 140, y0 + 30), p68.FINISHES['finishes'][fin]['label'], font=f_small, fill=(16, 32, 39), anchor='lm')
    dr.line([(60, H + head + foot - 62), (W - 60, H + head + foot - 62)], fill=(176, 190, 197), width=2)
    dr.text((W - 60, H + head + foot - 30), 'PROVISIONAL · NOT FOR CONSTRUCTION · Source: drawings/cad/' + f'P68-ENG-{deck.index:02d}-{p68.slug(deck.name)}.dxf',
            font=f_small, fill=(142, 59, 106), anchor='rs')
    dr.text((60, head + H - 24), 'STERN · AP', font=f_lab, fill=(16, 32, 39), anchor='ls')
    dr.text((W - 60, head + H - 24), 'BOW · FP  →', font=f_lab, fill=(16, 32, 39), anchor='rs')
    out = OUT / f'finish-plan-{deck.file_stem}.jpg'
    sheet.save(out, quality=88, optimize=True, progressive=True)
    path.unlink()
    print(f'wrote {out.relative_to(p68.ROOT)}')


def render_plan(deck: p68.Deck):
    K.reset(samples=24 if FAST else 64, width=PLAN_W // (2 if FAST else 1), height=PLAN_H // (2 if FAST else 1))
    K.flat_world((1.0, 1.0, 1.0), 0.75)
    K.sun(elev=58, azim=150, energy=2.6, angle=3)
    cd = build_level(deck, wall_h=1.1, cap=True)
    K.camera((PLAN_CX, PLAN_CY, cd.z + 40), (PLAN_CX, PLAN_CY, cd.z), ortho_scale=PLAN_SPAN)
    tmp = OUT / f'_plan-{deck.file_stem}.png'
    K.render(tmp)
    overlay_plan(tmp, deck, cd)


def render_cutaway(deck: p68.Deck):
    K.reset(samples=24 if FAST else 96, width=1200 if FAST else 2400, height=675 if FAST else 1350)
    K.sky(elevation_deg=40, rotation_deg=200, strength=0.06, sun_disc=True)
    cd = build_level(deck, wall_h=1.2, cap=True, depth=1.6)
    # Studio floor below the level, mid grey so the model reads against it.
    K.plane('Studio', -300, -300, 360, 300, cd.z - 1.65, K.principled('Studio floor', K.srgb('#9aa6ac'), rough=0.9))
    # Same viewing direction for every level, scaled to the extent of its rooms.
    x0 = min(r.x0 for r in cd.rooms) - 1.5
    x1 = max(r.x1 for r in cd.rooms) + 1.5
    k = (x1 - x0) / 52.0
    mid = (x0 + x1) / 2
    K.camera((mid - 42.5 * k, 0.5 - 33.5 * k, cd.z + 36 * k), (mid, 0.5, cd.z - 3 * k), lens=33)
    K.bpy.context.scene.view_settings.look = 'AgX - High Contrast'
    tmp = OUT / f'_cut-{deck.file_stem}.png'
    K.render(tmp)
    img = Image.open(tmp).convert('RGB')
    dr = ImageDraw.Draw(img)
    s = img.size[0] / 2400
    dr.text((int(40 * s), int(36 * s)), f'{deck.name.upper()} · {deck.meta["elevation"]}', font=ImageFont.truetype(FONT_B, int(46 * s)), fill=(16, 32, 39))
    dr.text((int(40 * s), int(96 * s)), 'Finish-out cutaway · proposed finishes, indicative furniture · concept only', font=ImageFont.truetype(FONT, int(26 * s)), fill=(60, 75, 85))
    out = OUT / f'cutaway-{deck.file_stem}.jpg'
    img.save(out, quality=88, optimize=True, progressive=True)
    tmp.unlink()
    print(f'wrote {out.relative_to(p68.ROOT)}')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wanted = {int(a) for a in sys.argv[1:] if a.isdigit()}
    which = [a for a in sys.argv[1:] if a in ('plan', 'cutaway')] or ['plan', 'cutaway']
    for deck in p68.decks():
        if wanted and deck.index not in wanted:
            continue
        if 'plan' in which:
            render_plan(deck)
        if 'cutaway' in which:
            render_cutaway(deck)


if __name__ == '__main__':
    main()
