"""Indicative furniture and fit-out for the finish-out renders.

Each function furnishes one room, read from the DXF (furniture key in the P68 XDATA),
on the floor at height z. Pieces are placed by rule from the room rectangle; they are a
concept fit-out for mood and planning, not a coordinated interior design.
"""
from __future__ import annotations

import math
import random

import bkit as K
from bkit import box, cbox, cylinder


def sofa(name, cx, cy, z, length, depth, rot, M, fabric='ivory', cushions='navy'):
    """Sofa centred at (cx, cy); back on the -Y side before rotation."""
    parts = [
        cbox(f'{name} base', 0, 0, 0.0, length, depth, 0.42, M[fabric], bevel=0.04),
        cbox(f'{name} back', 0, -depth / 2 + 0.11, 0.42, length, 0.22, 0.38, M[fabric], bevel=0.06),
        cbox(f'{name} armL', -length / 2 + 0.1, 0, 0.42, 0.2, depth, 0.2, M[fabric], bevel=0.05),
        cbox(f'{name} armR', length / 2 - 0.1, 0, 0.42, 0.2, depth, 0.2, M[fabric], bevel=0.05),
    ]
    n = max(2, int(length / 0.9))
    for i in range(n):
        x = -length / 2 + 0.45 + i * (length - 0.9) / max(1, n - 1)
        parts.append(cbox(f'{name} cushion{i}', x, -depth / 2 + 0.3, 0.45, 0.45, 0.14, 0.42, M[cushions], bevel=0.06))
    _group(parts, cx, cy, z, rot)


def armchair(name, cx, cy, z, rot, M, fabric='ivory'):
    parts = [
        cbox(f'{name} seat', 0, 0, 0, 0.85, 0.85, 0.42, M[fabric], bevel=0.05),
        cbox(f'{name} back', 0, -0.33, 0.42, 0.85, 0.18, 0.36, M[fabric], bevel=0.06),
    ]
    _group(parts, cx, cy, z, rot)


def _group(parts, cx, cy, z, rot):
    c, s = math.cos(rot), math.sin(rot)
    for p in parts:
        x, y, zz = p.location
        p.location = (cx + x * c - y * s, cy + x * s + y * c, z + zz)
        p.rotation_euler[2] = p.rotation_euler[2] + rot


def table(name, cx, cy, z, w, d, h, M, top='walnut', rot=0.0, legs='brass'):
    cbox(f'{name} top', cx, cy, z + h - 0.04, w, d, 0.04, M[top], rot=rot, bevel=0.01)
    if w > 1.2:
        cbox(f'{name} pedestal', cx, cy, z, min(w * 0.5, 1.2), 0.18, h - 0.04, M[legs], rot=rot, bevel=0.01)
    else:
        cylinder(f'{name} stem', cx, cy, z, 0.05, h - 0.04, M[legs])


def chair(name, cx, cy, z, rot, M, fabric='cognac'):
    parts = [
        cbox(f'{name} seat', 0, 0, 0.42, 0.48, 0.48, 0.07, M[fabric], bevel=0.02),
        cbox(f'{name} back', 0, -0.22, 0.49, 0.46, 0.05, 0.42, M[fabric], bevel=0.02),
        cbox(f'{name} legs', 0, 0, 0.0, 0.4, 0.4, 0.42, M['walnut'], bevel=0.01),
    ]
    _group(parts, cx, cy, z, rot)


def bed(name, cx, cy, z, w, l, rot, M):
    """Bed with the headboard on the -Y side before rotation; w across, l along."""
    parts = [
        cbox(f'{name} plinth', 0, 0, 0, w + 0.1, l, 0.32, M['walnut'], bevel=0.02),
        cbox(f'{name} mattress', 0, 0.02, 0.32, w, l - 0.05, 0.24, M['linen'], bevel=0.06),
        cbox(f'{name} throw', 0, l / 2 - 0.45, 0.555, w + 0.04, 0.7, 0.03, M['throw'], bevel=0.015),
        cbox(f'{name} head', 0, -l / 2 - 0.06, 0, w + 0.5, 0.12, 1.15, M['ivory'], bevel=0.04),
        cbox(f'{name} pillowL', -w / 4, -l / 2 + 0.3, 0.56, w / 2 - 0.12, 0.38, 0.16, M['linen'], bevel=0.07),
        cbox(f'{name} pillowR', w / 4, -l / 2 + 0.3, 0.56, w / 2 - 0.12, 0.38, 0.16, M['linen'], bevel=0.07),
        cbox(f'{name} cushion', 0, -l / 2 + 0.55, 0.56, w * 0.45, 0.16, 0.26, M['navy'], bevel=0.06),
        cbox(f'{name} nsL', -w / 2 - 0.45, -l / 2 + 0.25, 0, 0.5, 0.42, 0.5, M['walnut'], bevel=0.01),
        cbox(f'{name} nsR', w / 2 + 0.45, -l / 2 + 0.25, 0, 0.5, 0.42, 0.5, M['walnut'], bevel=0.01),
    ]
    _group(parts, cx, cy, z, rot)
    c, s = math.cos(rot), math.sin(rot)
    for sx in (-1, 1):
        x, y = sx * (w / 2 + 0.45), -l / 2 + 0.25
        lx, ly = cx + x * c - y * s, cy + x * s + y * c
        cylinder(f'{name} lamp{sx}', lx, ly, z + 0.5, 0.11, 0.32, K.principled('Lamp shade', K.srgb('#f4ead8'), rough=0.8, emission=K.srgb('#ffd9a0'), estrength=3.0))


def rug(name, cx, cy, z, w, d, M, rot=0.0):
    cbox(name, cx, cy, z, w, d, 0.012, M['rug'], rot=rot)


def plant(name, x, y, z, M, h=1.1):
    cylinder(f'{name} pot', x, y, z, 0.2, 0.4, M['pot'], r_top=0.24)
    o = cylinder(f'{name} leaves', x, y, z + 0.4, 0.32, h - 0.4, M['plant'], verts=10, r_top=0.12)
    o.modifiers.new('Sub', 'SUBSURF').levels = 2


def shelves(name, x0, y0, x1, y1, z, h, M, seed=1):
    """Bookshelf against a wall, from (x0, y0) to (x1, y1), with books."""
    box(f'{name} carcass', x0, y0, z, x1, y1, z + h, M['walnut'])
    rnd = random.Random(seed)
    along_x = abs(x1 - x0) > abs(y1 - y0)
    length = abs(x1 - x0) if along_x else abs(y1 - y0)
    cols = [K.srgb(c) for c in ('#1f3550', '#6b2e2a', '#2f4b3a', '#c9b58f', '#3b3f46', '#7d5a3a')]
    for shelf in range(4):
        zz = z + 0.35 + shelf * (h - 0.4) / 4
        pos = 0.05
        while pos < length - 0.1:
            bw = rnd.uniform(0.025, 0.05)
            bh = rnd.uniform(0.2, 0.3)
            mat = K.principled(f'Book{cols.index(rnd.choice(cols))}', rnd.choice(cols), rough=0.7)
            if along_x:
                xa = min(x0, x1) + pos
                box(f'{name} b', xa, min(y0, y1) - 0.02, zz, xa + bw, max(y0, y1) - 0.06, zz + bh, mat)
            else:
                ya = min(y0, y1) + pos
                box(f'{name} b', min(x0, x1) - 0.02, ya, zz, max(x0, x1) - 0.06, ya + bw, zz + bh, mat)
            pos += bw + rnd.uniform(0.0, 0.01)
            if rnd.random() < 0.06:
                pos += 0.25


def helm_console(name, cx, cy, z, w, M, facing=0.0):
    """Wrap-around helm console with chart, radar and conning screens, and two helm chairs."""
    parts = [
        cbox(f'{name} body', 0, 0, 0, w, 0.9, 0.85, M['walnut'], bevel=0.03),
        cbox(f'{name} top', 0, 0.05, 0.85, w + 0.04, 0.95, 0.04, M['stone_top'], bevel=0.01),
    ]
    _group(parts, cx, cy, z, facing)
    c, s = math.cos(facing), math.sin(facing)
    n = 4
    for i in range(n):
        x = -w / 2 + 0.45 + i * (w - 0.9) / (n - 1)
        y = 0.25
        sx, sy = cx + x * c - y * s, cy + x * s + y * c
        scr = cbox(f'{name} screen{i}', sx, sy, z + 0.89, 0.62, 0.04, 0.42, M['screen' if i % 2 == 0 else 'screen_warm'], rot=facing)
        scr.rotation_euler = (math.radians(-12), 0, facing)
    for sx_ in (-0.7, 0.7):
        x, y = sx_, -0.95
        hx, hy = cx + x * c - y * s, cy + x * s + y * c
        cylinder(f'{name} chairpost{sx_}', hx, hy, z, 0.06, 0.55, M['chrome'])
        armchair(f'{name} chair{sx_}', hx, hy, z + 0.33, facing, M, 'cognac')
    # Emergency stop on the console, always reachable.
    x, y = w / 2 - 0.25, -0.2
    cylinder(f'{name} estop', cx + x * c - y * s, cy + x * s + y * c, z + 0.89, 0.05, 0.05, M['red'])


# ---- Room fit-outs ----------------------------------------------------------------

def furnish(r: K.CadRoom, z: float, M: dict):
    f = r.furniture
    w, d = r.w, r.d
    cx, cy = r.cx, r.cy
    if f == 'salon':
        # Lounge aft, dining forward.
        lx = r.x0 + w * 0.3
        rug(f'{r.name} rug', lx, cy, z, min(5.5, w * 0.45), min(4.2, d * 0.65), M)
        sofa(f'{r.name} sofaA', lx, cy - d * 0.25, z, 3.2, 1.0, 0.0, M)
        sofa(f'{r.name} sofaB', lx, cy + d * 0.25, z, 3.2, 1.0, math.pi, M)
        table(f'{r.name} coffee', lx, cy, z, 1.4, 0.8, 0.4, M)
        armchair(f'{r.name} chairA', lx - 2.2, cy, z, -math.pi / 2, M)
        dx = r.x0 + w * 0.74
        tl = min(4.2, w * 0.32)
        table(f'{r.name} dining', dx, cy, z, tl, 1.2, 0.76, M)
        for i in range(int(tl / 0.75)):
            x = dx - tl / 2 + 0.4 + i * 0.75
            chair(f'{r.name} c{i}a', x, cy - 0.85, z, 0.0, M)
            chair(f'{r.name} c{i}b', x, cy + 0.85, z, math.pi, M)
        plant(f'{r.name} plant1', r.x0 + 0.5, r.y0 + 0.5, z, M)
        plant(f'{r.name} plant2', r.x0 + 0.5, r.y1 - 0.5, z, M)
        box(f'{r.name} sideboard', r.x1 - 0.5, cy - 1.5, z, r.x1 - 0.1, cy + 1.5, z + 0.8, M['walnut'])
    elif f in ('owner', 'vip', 'cabins', 'accessible'):
        if f == 'cabins':
            n = max(1, round(w / 4.5))
            step = w / n
            cabins = [(r.x0 + i * step, r.x0 + (i + 1) * step) for i in range(n)]
        else:
            cabins = [(r.x0, r.x1)]
        for i, (a, b) in enumerate(cabins):
            ccx = (a + b) / 2
            bw = 1.8 if f in ('owner', 'vip') else 1.6
            if f == 'accessible':
                bw = 1.6
            bl = 2.1
            if d >= 3.6:
                # Headboard against the outboard wall (larger |Y|).
                head_y = r.y1 if abs(r.y1) > abs(r.y0) else r.y0
                sgn = 1 if head_y == r.y1 else -1
                by = head_y - sgn * (bl / 2 + 0.15)
                bed(f'{r.name} bed{i}', ccx, by, z, bw, bl, 0 if sgn < 0 else math.pi, M)
            else:
                by = cy
                bed(f'{r.name} bed{i}', b - bl / 2 - 0.3, cy, z, bw, bl, math.pi / 2, M)
            if f == 'owner':
                sofa(f'{r.name} sofa', ccx, r.y0 + 0.7 if by > cy else r.y1 - 0.7, z, 2.4, 0.9, 0 if by > cy else math.pi, M)
                rug(f'{r.name} rug', ccx, by, z, 3.4, 2.8, M)
                box(f'{r.name} desk', r.x0 + 0.2, cy - 0.8, z, r.x0 + 0.85, cy + 0.8, z + 0.75, M['walnut'])
            if f == 'accessible':
                # Clear 1.525 m turning circle marked on the floor, beside the bed.
                cylinder(f'{r.name} turning', ccx - 1.4, cy, z + 0.002, 0.76, 0.004, K.principled('Turning space', K.srgb('#bfe3c2'), rough=0.9), verts=48)
            # Ensuite at one end of each cabin.
            ex = a + 0.05
            box(f'{r.name} ensuite{i}', ex, r.y0 + 0.05, z, ex + 1.6, r.y0 + min(2.2, d * 0.5), z + 0.03, K.floor_material('marble', 1.6, min(2.2, d * 0.5) - 0.05))
            cbox(f'{r.name} vanity{i}', ex + 0.8, r.y0 + 0.35, z, 1.1, 0.5, 0.85, M['stone_top'], bevel=0.01)
    elif f == 'crew':
        n = max(1, round(w / 3.0))
        step = w / n
        for i in range(n):
            a = r.x0 + i * step
            box(f'crew bunk{i}', a + 0.15, r.y1 - 0.95, z, a + 2.15, r.y1 - 0.1, z + 0.45, M['oak'])
            box(f'crew mattress{i}', a + 0.2, r.y1 - 0.9, z + 0.45, a + 2.1, r.y1 - 0.15, z + 0.6, M['linen'])
            box(f'crew locker{i}', a + 2.3, r.y1 - 0.65, z, a + step - 0.15, r.y1 - 0.1, z + 1.9, M['oak'])
    elif f == 'lido':
        pw, pl = min(6.0, w * 0.45), min(3.2, d * 0.5)
        px = r.x0 + w * 0.55
        box('pool coping', px - pl / 2 - 0.25, cy - pw / 2 - 0.25, z, px + pl / 2 + 0.25, cy + pw / 2 + 0.25, z + 0.06, M['stone_top'])
        box('pool basin', px - pl / 2, cy - pw / 2, z - 1.2, px + pl / 2, cy + pw / 2, z + 0.061, M['pool_tile'])
        K.plane('pool water', px - pl / 2, cy - pw / 2, px + pl / 2, cy + pw / 2, z + 0.03, M['water'])
        for i in range(4):
            ly = r.y0 + 0.9 + i * (d - 1.8) / 3
            lounger(f'lounger{i}', r.x0 + 1.6, ly, z, M)
        table('lido table', r.x1 - 2.2, cy, z, 2.4, 1.0, 0.74, M, top='teak_plain', legs='chrome')
        for i in range(3):
            chair(f'lido c{i}a', r.x1 - 3.0 + i * 0.8, cy - 0.8, z, 0.0, M, 'ivory')
            chair(f'lido c{i}b', r.x1 - 3.0 + i * 0.8, cy + 0.8, z, math.pi, M, 'ivory')
    elif f == 'bar':
        box('bar counter', r.x1 - 1.2, r.y0 + 0.8, z, r.x1 - 0.5, r.y1 - 0.8, z + 1.1, M['walnut'])
        box('bar top', r.x1 - 1.3, r.y0 + 0.75, z + 1.1, r.x1 - 0.45, r.y1 - 0.75, z + 1.14, M['stone_top'])
        for i in range(int((d - 1.6) / 0.7)):
            cylinder(f'stool{i}', r.x1 - 1.65, r.y0 + 1.1 + i * 0.7, z, 0.2, 0.75, M['cognac'])
        for j, tx in enumerate((r.x0 + 1.6, r.x0 + 3.8)):
            table(f'bar table{j}', tx, cy, z, 0.9, 0.9, 0.74, M)
            for k in range(4):
                a = k * math.pi / 2
                chair(f'bar c{j}{k}', tx + 0.75 * math.cos(a), cy + 0.75 * math.sin(a), z, a + math.pi / 2, M, 'ivory')
    elif f in ('lookout', 'lounge', 'seating'):
        if w > 3:
            rug(f'{r.name} rug', cx, cy, z, w * 0.7, d * 0.6, M)
        if f == 'seating':
            sofa(f'{r.name} banquette', cx, r.y0 + 0.55 if abs(r.y0) > abs(r.y1) else r.y1 - 0.55, z, w * 0.75, 0.95,
                 0.0 if abs(r.y0) > abs(r.y1) else math.pi, M, fabric='cognac', cushions='ivory')
            for i in range(3):
                table(f'{r.name} side{i}', r.x0 + w * (0.25 + i * 0.25), cy, z, 0.6, 0.6, 0.45, M)
        else:
            sofa(f'{r.name} sofaA', cx, cy - d * 0.28, z, min(3.6, w * 0.6), 1.0, 0.0, M)
            sofa(f'{r.name} sofaB', cx, cy + d * 0.28, z, min(3.6, w * 0.6), 1.0, math.pi, M)
            table(f'{r.name} coffee', cx, cy, z, min(1.6, w * 0.3), 0.8, 0.4, M)
            plant(f'{r.name} plant', r.x1 - 0.5, r.y0 + 0.5, z, M)
    elif f == 'library':
        wall_y = r.y1 if abs(r.y1) > abs(r.y0) else r.y0
        sgn = 1 if wall_y == r.y1 else -1
        shelves(f'{r.name} shelves', r.x0 + 0.3, wall_y - sgn * 0.4, r.x1 - 0.3, wall_y - sgn * 0.08, z, 2.1, M)
        table(f'{r.name} chart table', cx, cy - sgn * 0.2, z, 2.2, 0.9, 0.9, M)
        for i, xx in enumerate((cx - 2.2, cx + 2.2)):
            armchair(f'{r.name} chair{i}', xx, cy - sgn * 0.1, z, 0 if sgn < 0 else math.pi, M, 'cognac')
    elif f == 'helm':
        helm_console('helm', r.x1 - 0.7, cy, z, min(3.6, r.d - 0.2), M, facing=-math.pi / 2)
    elif f == 'galley':
        box('galley run A', r.x0 + 0.2, r.y0 + 0.1, z, r.x1 - 0.2, r.y0 + 0.75, z + 0.9, M['steel'])
        box('galley top A', r.x0 + 0.2, r.y0 + 0.1, z + 0.9, r.x1 - 0.2, r.y0 + 0.78, z + 0.94, M['stone_top'])
        box('galley run B', r.x0 + 0.2, r.y1 - 0.75, z, r.x1 - 0.2, r.y1 - 0.1, z + 0.9, M['steel'])
        box('galley top B', r.x0 + 0.2, r.y1 - 0.78, z + 0.9, r.x1 - 0.2, r.y1 - 0.1, z + 0.94, M['stone_top'])
        if r.d > 2.6:
            box('galley island', cx - w * 0.25, cy - 0.35, z, cx + w * 0.25, cy + 0.35, z + 0.92, M['steel'])
    elif f == 'laundry':
        for i in range(int((w - 0.6) / 0.7)):
            cbox(f'washer{i}', r.x0 + 0.6 + i * 0.7, r.y1 - 0.45, z, 0.6, 0.6, 0.85, M['steel_white'], bevel=0.03)
        box('folding table', r.x0 + 0.3, r.y0 + 0.2, z, r.x1 - 0.3, r.y0 + 0.9, z + 0.9, M['oak'])
    elif f == 'workshop':
        box('bench', r.x0 + 0.2, r.y0 + 0.2, z, r.x1 - 0.2, r.y0 + 0.9, z + 0.9, M['steel'])
        box('racking', r.x0 + 0.2, r.y1 - 0.6, z, r.x1 - 0.2, r.y1 - 0.1, z + 2.0, M['steel'])
    elif f == 'tank':
        box(f'{r.name} tank', r.x0 + 0.15, r.y0 + 0.15, z, r.x1 - 0.15, r.y1 - 0.15, z + 1.7, M['tank_paint'], bevel=0.05)
        for i in range(max(1, int(w / 3))):
            cylinder(f'{r.name} manhole{i}', r.x0 + 1.5 + i * 3, cy, z + 1.7, 0.3, 0.06, M['steel'])
    elif f == 'pumps':
        for i in range(max(1, int(w / 1.4))):
            cylinder(f'pump{i}', r.x0 + 0.7 + i * 1.4, cy, z, 0.3, 0.7, M['steel'])
    elif f == 'theatre':
        # Stage at the aft end, raked seating forward, across the beam.
        stage_x1 = r.x0 + w * 0.3
        box(f'{r.name} stage', r.x0 + 0.2, r.y0 + 0.2, z, stage_x1, r.y1 - 0.2, z + 0.6, M['walnut'])
        box(f'{r.name} screen', r.x0 + 0.1, r.y0 + 0.3, z + 0.6, r.x0 + 0.25, r.y1 - 0.3, z + 2.6, M['navy'])
        seats = max(1, int((d - 0.8) / 0.6))
        x = stage_x1 + 1.2
        i = 0
        while x <= r.x1 - 0.6:
            for j in range(seats):
                chair(f'{r.name} seat{i}-{j}', x, r.y0 + 0.5 + j * 0.6, z, math.pi / 2, M, 'navy')
            x += 0.95
            i += 1
    elif f == 'cinema':
        box(f'{r.name} screen', r.x0 + 0.1, r.y0 + 0.4, z + 0.8, r.x0 + 0.25, r.y1 - 0.4, z + 2.8, M['navy'])
        seats = max(1, int((d - 0.8) / 0.65))
        x = r.x0 + 2.2
        i = 0
        while x <= r.x1 - 0.6:
            for j in range(seats):
                chair(f'{r.name} seat{i}-{j}', x, r.y0 + 0.5 + j * 0.65, z, math.pi / 2, M, 'navy')
            x += 1.0
            i += 1
    elif f == 'stage':
        box(f'{r.name} set platform', r.x0 + 0.3, r.y0 + 0.3, z, r.x1 - 0.3, r.y1 - 0.3, z + 0.25, M['steel_white'])
        table(f'{r.name} presenter desk', cx, cy, z + 0.25, 1.6, 0.7, 0.75, M, top='walnut')
        cbox(f'{r.name} camera pedestal', r.x0 + 1.0, cy, z, 0.5, 0.5, 1.4, M['steel'])
    elif f == 'stage_side':
        box(f'{r.name} platform', r.x0 + 0.3, r.y0 + 0.3, z, r.x1 - 0.3, r.y1 - 0.3, z + 0.25, M['steel_white'])
        table(f'{r.name} stool desk', cx, cy, z + 0.25, 1.0, 0.6, 0.75, M, top='walnut')
    elif f == 'control':
        desk_y0, desk_y1 = r.y1 - 1.0, r.y1 - 0.45
        box(f'{r.name} console', r.x0 + 0.4, desk_y0, z, r.x1 - 0.4, desk_y1, z + 0.8, M['steel'])
        box(f'{r.name} console top', r.x0 + 0.4, desk_y0, z + 0.8, r.x1 - 0.4, desk_y1, z + 0.84, M['stone_top'])
        for k, xx in enumerate(range(int(r.x0 + 1), int(r.x1 - 1), 2)):
            cbox(f'{r.name} monitor{k}', xx + 0.5, desk_y1 - 0.15, z + 0.9, 0.7, 0.05, 0.5, M['steel'])
        chair(f'{r.name} operator', cx, desk_y0 - 0.6, z, 0.0, M, 'navy')
    elif f == 'racks':
        n = max(1, int((w - 0.6) / 0.7))
        for k in range(n):
            xx = r.x0 + 0.3 + k * 0.7
            box(f'{r.name} rack{k}', xx, r.y0 + 0.3, z, xx + 0.6, r.y0 + 1.2, z + 2.0, M['steel'])
    elif f == 'lift':
        box(f'{r.name} car', cx - 1.0, cy - 0.75, z, cx + 1.0, cy + 0.75, z + 0.02, M['brass'])
        for sx in (-1, 1):
            box(f'{r.name} side{sx}', cx + sx * 1.0 - 0.03, cy - 0.75, z, cx + sx * 1.0 + 0.03, cy + 0.75, z + 1.0, M['brass'])


def lounger(name, cx, cy, z, M):
    parts = [
        cbox(f'{name} frame', 0, 0, 0, 1.95, 0.72, 0.3, M['teak_plain'], bevel=0.02),
        cbox(f'{name} pad', 0.1, 0, 0.3, 1.75, 0.68, 0.08, M['ivory'], bevel=0.03),
    ]
    back = cbox(f'{name} back', -0.7, 0, 0.36, 0.6, 0.68, 0.08, M['ivory'], bevel=0.03)
    back.rotation_euler = (0, math.radians(-35), 0)
    parts.append(back)
    _group(parts, cx, cy, z, 0.0)
