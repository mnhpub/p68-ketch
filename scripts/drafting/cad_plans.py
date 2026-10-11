"""Engineering deck plans as AutoCAD DXF source drawings, with plotted PDF and SVG sheets.

One DXF per level (drawings/cad/P68-ENG-0N-<deck>.dxf, AutoCAD 2018 format):

  Model space, 1 unit = 1 m. X runs from the stern (AP, X 0) to the bow (FP, X 68);
  Y is positive to port, so the plan reads bow-right with port up. Each room is a closed
  polyline on A-AREA carrying its name, status, finish and furniture as P68 XDATA, which
  the Blender scripts read. Walls are broken at indicative doors. Dimensions are real
  DIMENSION entities in the P68-200 style.

  Paper space, layout "A3 1-200", 1 unit = 1 mm: drawing frame, a viewport onto the plan
  at 1:200, room schedule, deck status panel, general notes, key plan, legend and a
  title block inserted from the P68-TITLE block with attributes.

The plots (drawings/eng-deck-NN-<deck>.svg for the app, drawings/P68-engineering-deck-plans.pdf
for print) are rendered from the paper-space layout of each DXF, so the DXF stays the
source. Schematic only: positions come from the GA schematic and are not dimensioned.
"""
from __future__ import annotations

import io
import math
from collections import defaultdict

import ezdxf
from ezdxf import colors, units
from ezdxf.addons.drawing import Frontend, RenderContext, layout, pymupdf, svg
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration, LineweightPolicy
from ezdxf.enums import TextEntityAlignment
import pymupdf as fitz

import p68

CAD = p68.OUT / 'cad'
SCALE = 200  # 1:200
M_PER_MM = SCALE / 1000  # model metres per paper millimetre
SHEET_W, SHEET_H = 420.0, 297.0

INK = (16, 32, 39)
MUTED = (84, 110, 122)
FAINT = (176, 190, 197)
ACCENT = (142, 59, 106)
LIFT = (25, 118, 210)
GOOD = (46, 125, 50)
STATUS_FILL = {'ga': (230, 240, 225), 'resolved': (223, 233, 246), 'inferred': (251, 239, 213)}
STATUS_EDGE = {'ga': (91, 138, 74), 'resolved': (61, 111, 168), 'inferred': (185, 131, 42)}
LIFT_FILL = (213, 236, 247)
DECK_FILL = (251, 250, 247)

# AIA / NCS-style layers: name, ACI colour, lineweight (1/100 mm), plot.
LAYERS = [
    ('A-FLOR-OTLN', 7, 50, True), ('A-AREA', 8, 13, True), ('A-AREA-PATT', 254, 0, True),
    ('A-AREA-IDEN', 7, 18, True), ('A-WALL', 7, 35, True), ('A-WALL-PRTN', 8, 18, True),
    ('A-DOOR', 7, 18, True), ('A-CONV', 5, 25, True), ('A-ROOF-OTLN', 6, 25, True),
    ('S-GRID', 9, 9, True), ('S-GRID-IDEN', 8, 13, True), ('S-MAST', 8, 25, True),
    ('A-ANNO-DIMS', 7, 13, True), ('A-ANNO-NOTE', 7, 13, True),
    ('G-ANNO-TTLB', 7, 35, True), ('G-ANNO-TABL', 7, 13, True), ('G-ANNO-NOTE', 7, 13, True),
    ('G-ANNO-LEGN', 7, 13, True), ('G-VIEW', 8, 9, False),
]

tc = colors.rgb2int


def Y(y: float) -> float:
    """Layout y (port negative) to model Y (port positive)."""
    return -y


def new_doc():
    doc = ezdxf.new('R2018', setup=True, units=units.M)
    doc.appids.add('P68')
    for name, aci, lw, plot in LAYERS:
        lay = doc.layers.add(name, color=aci, lineweight=lw)
        lay.dxf.plot = 1 if plot else 0
    st = doc.styles.add('P68', font='arial.ttf')
    st.dxf.width = 0.92
    doc.styles.add('P68-BOLD', font='arialbd.ttf')
    # Dimension style for 1:200 in a metre drawing: paper sizes times 0.2 m/mm.
    ds = doc.dimstyles.new('P68-200')
    k = M_PER_MM
    ds.dxf.dimtxt = 1.3 * k
    ds.dxf.dimtxsty = 'P68'
    ds.dxf.dimasz = 1.2 * k
    ds.dxf.dimtsz = 0.9 * k  # architectural ticks
    ds.dxf.dimexe = 1.0 * k
    ds.dxf.dimexo = 0.6 * k
    ds.dxf.dimgap = 0.5 * k
    ds.dxf.dimdec = 2
    ds.dxf.dimzin = 0
    ds.dxf.dimdsep = ord('.')
    ds.dxf.dimtad = 1
    ds.dxf.dimlunit = 2
    ds.dxf.dimclrd = 7
    ds.dxf.dimclre = 8
    ds.dxf.dimclrt = 7
    _title_block_def(doc)
    _tag_block_def(doc)
    return doc


def _tag_block_def(doc):
    blk = doc.blocks.new('P68-TAG')
    blk.add_circle((0, 0), 0.42, dxfattribs={'layer': '0', 'lineweight': 18})
    blk.add_attdef('NUM', (0, 0), dxfattribs={'height': 0.3, 'style': 'P68-BOLD', 'layer': '0'}).set_placement(
        (0, 0), align=TextEntityAlignment.MIDDLE_CENTER)


def _title_block_def(doc):
    blk = doc.blocks.new('P68-TITLE')
    W, H = 192, 46
    a = {'layer': '0'}
    blk.add_lwpolyline([(0, 0), (W, 0), (W, H), (0, H)], close=True, dxfattribs={**a, 'lineweight': 50})
    blk.add_line((110, 0), (110, H), dxfattribs=a)
    blk.add_line((150, 0), (150, H), dxfattribs=a)
    for yy in (12, 24, 34):
        blk.add_line((110, yy), (W, yy), dxfattribs=a)

    def txt(s, x, y, h, color=INK, style='P68'):
        blk.add_text(s, height=h, dxfattribs={**a, 'style': style, 'true_color': tc(color)}).set_placement((x, y))

    txt('P68 KETCH', 4, H - 9, 5.2, style='P68-BOLD')
    txt(f'{p68.LOA:.0f} m expedition four-mast ketch · concept design', 4, H - 15, 1.8, MUTED)
    txt('PROVISIONAL SCHEMATIC · NOT FOR CONSTRUCTION · NOT FOR FABRICATION', 4, 4, 1.8, ACCENT, 'P68-BOLD')
    cells = [(112, 34, H, 'DRAWING NO.', 'DWGNO'), (152, 34, H, 'REVISION', 'REV'),
             (112, 24, 34, 'SCALE', 'SCALE'), (152, 24, 34, 'DATE', 'DATE'),
             (112, 12, 24, 'SOURCE', 'SOURCE'), (152, 12, 24, 'DATUM', 'DATUM'),
             (112, 0, 12, 'STATUS', 'STATUS'), (152, 0, 12, 'SHEET', 'SHEET')]
    for x, y0, y1, label, tag in cells:
        txt(label, x, y1 - 3.2, 1.3, MUTED)
        blk.add_attdef(tag, (x, y0 + 2.2), dxfattribs={**a, 'height': 2.0, 'style': 'P68-BOLD', 'true_color': tc(INK)})
    blk.add_attdef('TITLE', (4, H - 25), dxfattribs={**a, 'height': 2.8, 'style': 'P68-BOLD', 'true_color': tc(INK)})
    blk.add_attdef('SUBTITLE', (4, H - 31), dxfattribs={**a, 'height': 1.7, 'style': 'P68', 'true_color': tc(MUTED)})


# ---- Model space ---------------------------------------------------------------

def text(space, s, x, y, h, layer, color=INK, align=TextEntityAlignment.MIDDLE_CENTER, style='P68', rot=0):
    t = space.add_text(s, height=h, rotation=rot, dxfattribs={'layer': layer, 'style': style, 'true_color': tc(color)})
    t.set_placement((x, y), align=align)
    return t


def hatch_solid(space, pts, rgb, layer='A-AREA-PATT'):
    h = space.add_hatch(dxfattribs={'layer': layer})
    h.rgb = rgb
    h.paths.add_polyline_path(pts, is_closed=True)
    return h


def hatch_pattern(space, pts, pattern, scale, rgb, layer='A-AREA-PATT', angle=0):
    h = space.add_hatch(dxfattribs={'layer': layer, 'true_color': tc(rgb)})
    h.set_pattern_fill(pattern, scale=scale, angle=angle)
    h.paths.add_polyline_path(pts, is_closed=True)
    return h


def rect_pts(x0, y0, x1, y1):
    return [(x0, Y(y0)), (x1, Y(y0)), (x1, Y(y1)), (x0, Y(y1))]


def wall_segments(deck: p68.Deck, door_list):
    """Room edges merged into wall lines, broken at door openings."""
    edges = defaultdict(list)  # (orientation, fixed) -> [(lo, hi)]
    for r in deck.rooms:
        edges[('v', round(r.x0, 3))].append((r.y0, r.y1))
        edges[('v', round(r.x1, 3))].append((r.y0, r.y1))
        edges[('h', round(r.y0, 3))].append((r.x0, r.x1))
        edges[('h', round(r.y1, 3))].append((r.x0, r.x1))
    openings = defaultdict(list)
    for d in door_list:
        hw = d.width / 2
        if d.vertical:
            openings[('v', round(d.x, 3))].append((d.y - hw, d.y + hw))
        else:
            openings[('h', round(d.y, 3))].append((d.x - hw, d.x + hw))
    segs = []
    for key, spans in edges.items():
        spans.sort()
        merged = [list(spans[0])]
        for lo, hi in spans[1:]:
            if lo <= merged[-1][1] + 1e-6:
                merged[-1][1] = max(merged[-1][1], hi)
            else:
                merged.append([lo, hi])
        for lo, hi in merged:
            pieces = [(lo, hi)]
            for olo, ohi in sorted(openings.get(key, [])):
                nxt = []
                for a, b in pieces:
                    if ohi <= a or olo >= b:
                        nxt.append((a, b))
                        continue
                    if olo > a:
                        nxt.append((a, olo))
                    if ohi < b:
                        nxt.append((ohi, b))
                pieces = nxt
            for a, b in pieces:
                if b - a > 1e-3:
                    segs.append((key[0], key[1], a, b))
    return segs


def model(doc, deck: p68.Deck):
    msp = doc.modelspace()
    # Stations and buttocks.
    for x in range(0, 69):
        major = x % 10 == 0
        top = 7.55
        msp.add_line((x, top), (x, top - (0.55 if major else 0.3)), dxfattribs={'layer': 'S-GRID', 'true_color': tc(INK if major else FAINT)})
        if major:
            hb = p68.half_beam(x)
            msp.add_line((x, -hb - 0.25), (x, hb + 0.25), dxfattribs={'layer': 'S-GRID', 'linetype': 'DASHED', 'ltscale': 0.04, 'true_color': tc(FAINT)})
            text(msp, f'X {x}', x, top + 0.3, 0.26, 'S-GRID-IDEN', MUTED, TextEntityAlignment.BOTTOM_CENTER)
    for yb in (-4, -2, 2, 4):
        msp.add_line((0, yb), (68, yb), dxfattribs={'layer': 'S-GRID', 'true_color': tc((223, 229, 232))})
        text(msp, f'B{abs(yb)}{"P" if yb > 0 else "S"}', -0.5, yb, 0.22, 'S-GRID-IDEN', FAINT, TextEntityAlignment.MIDDLE_RIGHT)

    outline = [(x, Y(y)) for x, y in deck.outline]
    hatch_solid(msp, outline, DECK_FILL, 'A-FLOR-OTLN')
    msp.add_lwpolyline(outline, close=True, dxfattribs={'layer': 'A-FLOR-OTLN'})
    msp.add_line((-1.2, 0), (69.2, 0), dxfattribs={'layer': 'S-GRID', 'linetype': 'CENTER', 'ltscale': 0.05, 'true_color': tc(MUTED)})
    text(msp, 'CL', 69.4, 0, 0.3, 'S-GRID-IDEN', MUTED, TextEntityAlignment.MIDDLE_LEFT)

    door_list = p68.doors(deck)
    # Rooms: status fill, pattern, boundary polyline with XDATA.
    for r in deck.rooms:
        pts = rect_pts(r.x0, r.y0, r.x1, r.y1)
        hatch_solid(msp, pts, LIFT_FILL if r.is_lift else STATUS_FILL[r.status])
        if r.finish == 'tank':
            hatch_pattern(msp, pts, 'ANSI31', 0.14, (120, 130, 135))
        elif r.is_route:
            hatch_pattern(msp, pts, 'NET', 0.14, (196, 206, 212))
        pl = msp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'A-AREA'})
        pl.set_xdata('P68', [(1000, r.name), (1000, r.status), (1000, r.finish), (1000, r.furniture or ''),
                             (1070, r.num), (1000, p68.FINISHES['finishes'][r.finish]['label'])])
        for part in p68.partitions(r)[1:]:
            msp.add_line((part.x0, Y(r.y0)), (part.x0, Y(r.y1)), dxfattribs={'layer': 'A-WALL-PRTN', 'linetype': 'DASHED', 'ltscale': 0.03})

    for o, fixed, a, b in wall_segments(deck, door_list):
        p1, p2 = ((fixed, Y(a)), (fixed, Y(b))) if o == 'v' else ((a, Y(fixed)), (b, Y(fixed)))
        msp.add_line(p1, p2, dxfattribs={'layer': 'A-WALL', 'true_color': tc(INK)})

    # Doors: leaf and swing on A-DOOR; lift landing doors on A-CONV.
    for d in door_list:
        hw = d.width / 2
        if d.kind == 'open':
            continue
        if d.kind == 'lift':
            if d.vertical:
                msp.add_line((d.x - 0.12 * d.sign, Y(d.y - hw)), (d.x - 0.12 * d.sign, Y(d.y + hw)), dxfattribs={'layer': 'A-CONV', 'true_color': tc(LIFT), 'lineweight': 35})
            else:
                yy = Y(d.y) + 0.12 * d.sign
                msp.add_line((d.x - hw, yy), (d.x + hw, yy), dxfattribs={'layer': 'A-CONV', 'true_color': tc(LIFT), 'lineweight': 35})
            continue
        if d.vertical:
            hx, hy = d.x, Y(d.y) - hw
            s = d.sign
            msp.add_line((hx, hy), (hx + s * d.width, hy), dxfattribs={'layer': 'A-DOOR', 'lineweight': 25})
            a0, a1 = (0, 90) if s > 0 else (90, 180)
        else:
            hx, hy = d.x - hw, Y(d.y)
            s = -d.sign
            msp.add_line((hx, hy), (hx, hy + s * d.width), dxfattribs={'layer': 'A-DOOR', 'lineweight': 25})
            a0, a1 = (0, 90) if s > 0 else (270, 360)
        msp.add_arc((hx, hy), d.width, a0, a1, dxfattribs={'layer': 'A-DOOR', 'lineweight': 9})

    # Lifts: shaft cross and the car.
    cd, cw = p68.ACCESS['criteria']['lift_car_internal_m']  # 1.5 across, 2.0 along
    for r in deck.rooms:
        if not r.is_lift:
            continue
        msp.add_line((r.x0, Y(r.y0)), (r.x1, Y(r.y1)), dxfattribs={'layer': 'A-CONV', 'true_color': tc(LIFT)})
        msp.add_line((r.x0, Y(r.y1)), (r.x1, Y(r.y0)), dxfattribs={'layer': 'A-CONV', 'true_color': tc(LIFT)})
        car = rect_pts(r.cx - cw / 2, r.cy - cd / 2, r.cx + cw / 2, r.cy + cd / 2)
        hatch_solid(msp, car, (255, 255, 255), 'A-CONV')
        msp.add_lwpolyline(car, close=True, dxfattribs={'layer': 'A-CONV', 'true_color': tc(LIFT), 'lineweight': 25})
        text(msp, r.name[-1], r.cx, Y(r.cy), 0.5, 'A-CONV', LIFT, style='P68-BOLD')

    # Masts where they pass through the level.
    x0, x1 = deck.extent
    for label, mx in p68.MASTS.items():
        if x0 <= mx <= x1 and deck.name != 'Tank / Technical':
            msp.add_circle((mx, 0), 0.45, dxfattribs={'layer': 'S-MAST', 'lineweight': 35})
            hatch_pattern(msp, [(mx + 0.45 * math.cos(a / 16 * math.tau), 0.45 * math.sin(a / 16 * math.tau)) for a in range(16)], 'ANSI37', 0.04, (90, 100, 105), 'S-MAST')
            text(msp, f'{label.upper()} MAST (APPROX.)', mx, -0.75, 0.2, 'S-MAST', ACCENT, TextEntityAlignment.TOP_CENTER)

    # Roof overlay on the Commander level.
    for r in deck.roof:
        msp.add_lwpolyline(rect_pts(r.x0, r.y0, r.x1, r.y1), close=True,
                           dxfattribs={'layer': 'A-ROOF-OTLN', 'linetype': 'DASHED', 'ltscale': 0.06, 'true_color': tc(ACCENT)})
        text(msp, f'ROOF OVER (+{p68.ROOF_Z:.2f}): SUN DECK AND OUTDOOR PILOT HOUSE, COVER TO +{p68.COVER_Z:.2f}',
             r.cx, Y(r.y0) + 0.18, 0.22, 'A-ROOF-OTLN', ACCENT, TextEntityAlignment.BOTTOM_CENTER)

    # Room tags (block with attribute), names and areas.
    for r in deck.rooms:
        if r.is_lift:
            continue
        name = r.name if len(r.name) <= 26 else r.name[:24] + '…'
        if r.w >= 4.5 and r.h >= 2.4:
            # Stacked: tag, name, area.
            ref = msp.add_blockref('P68-TAG', (r.cx, Y(r.cy) + 0.45), dxfattribs={'layer': 'A-AREA-IDEN'})
            ref.add_auto_attribs({'NUM': str(r.num)})
            mt = msp.add_mtext(name.upper(), dxfattribs={'layer': 'A-AREA-IDEN', 'char_height': 0.24, 'style': 'P68', 'true_color': tc(INK)})
            mt.set_location((r.cx, Y(r.cy) - 0.32), attachment_point=5)
            mt.set_bg_color((255, 255, 255), scale=1.2)
            text(msp, f'{r.area:.1f} m²', r.cx, Y(r.cy) - 0.9, 0.22, 'A-AREA-IDEN', MUTED)
        elif r.w >= 7 and r.h >= 1.0:
            # Inline for long, narrow rooms: tag, then name and area on one line.
            ref = msp.add_blockref('P68-TAG', (r.x0 + 0.8, Y(r.cy)), dxfattribs={'layer': 'A-AREA-IDEN'})
            ref.add_auto_attribs({'NUM': str(r.num)})
            mt = msp.add_mtext(f'{name.upper()}  ·  {r.area:.1f} m²', dxfattribs={'layer': 'A-AREA-IDEN', 'char_height': 0.22, 'style': 'P68', 'true_color': tc(INK)})
            mt.set_location((r.x0 + 1.45, Y(r.cy)), attachment_point=4)
            mt.set_bg_color((255, 255, 255), scale=1.2)
        else:
            ref = msp.add_blockref('P68-TAG', (r.cx, Y(r.cy)), dxfattribs={'layer': 'A-AREA-IDEN'})
            ref.add_auto_attribs({'NUM': str(r.num)})
        if 'Accessible' in r.name:
            text(msp, 'ACCESSIBLE', r.x1 - 0.25, Y(r.y0) - 0.35, 0.2, 'A-AREA-IDEN', GOOD, TextEntityAlignment.TOP_RIGHT, 'P68-BOLD')

    # Dimensions: room-edge chain to starboard, overall length, beam.
    edges = sorted({round(v, 2) for r in deck.rooms for v in (r.x0, r.x1)})
    chain = [edges[0]]
    for e in edges[1:]:
        if e - chain[-1] >= 1.2:
            chain.append(e)
    for a, b in zip(chain, chain[1:]):
        msp.add_linear_dim(base=(a, -7.05), p1=(a, -6.4), p2=(b, -6.4), dimstyle='P68-200', dxfattribs={'layer': 'A-ANNO-DIMS'}).render()
    msp.add_linear_dim(base=(0, -7.95), p1=(0, -0.1), p2=(p68.LOA, -0.1), dimstyle='P68-200',
                       text=f'{p68.LOA:.2f} LOA  (AP X 0 to FP X {p68.LOA:.0f})', dxfattribs={'layer': 'A-ANNO-DIMS'}).render()
    msp.add_linear_dim(base=(p68.LOA + 2.4, 0), p1=(p68.LOA + 1.6, -p68.BEAM / 2), p2=(p68.LOA + 1.6, p68.BEAM / 2), angle=90, dimstyle='P68-200',
                       text=f'{p68.BEAM:.2f} MAX BEAM (X 34)', dxfattribs={'layer': 'A-ANNO-DIMS'}).render()

    text(msp, 'STERN · AP', -3.2, -8.2, 0.34, 'A-ANNO-NOTE', INK, TextEntityAlignment.BOTTOM_LEFT, 'P68-BOLD')
    text(msp, 'BOW · FP', 71.3, -8.2, 0.34, 'A-ANNO-NOTE', INK, TextEntityAlignment.BOTTOM_RIGHT, 'P68-BOLD')
    text(msp, 'PORT', -3.2, 6.2, 0.3, 'A-ANNO-NOTE', MUTED, TextEntityAlignment.MIDDLE_LEFT)
    text(msp, 'STARBOARD', -3.2, -6.2, 0.3, 'A-ANNO-NOTE', MUTED, TextEntityAlignment.MIDDLE_LEFT)
    arrow = [(60, 6.45), (64.2, 6.45), (64.2, 6.7), (65.2, 6.3), (64.2, 5.9), (64.2, 6.15), (60, 6.15)]
    hatch_solid(msp, arrow, INK, 'A-ANNO-NOTE')
    text(msp, 'FWD', 62, 6.95, 0.3, 'A-ANNO-NOTE', INK, TextEntityAlignment.BOTTOM_CENTER, 'P68-BOLD')


# ---- Paper space -------------------------------------------------------------

VIEW = {'x0': -3.6, 'x1': 71.6, 'y0': -8.5, 'y1': 8.5}  # model window shown in the viewport


def ptext(psp, s, x, y, h=1.6, color=INK, style='P68', align=TextEntityAlignment.LEFT, layer='G-ANNO-NOTE'):
    t = psp.add_text(s, height=h, dxfattribs={'layer': layer, 'style': style, 'true_color': tc(color)})
    t.set_placement((x, y), align=align)
    return t


def wrap(s, n):
    out, cur = [], ''
    for w in s.split():
        if len(cur) + len(w) + 1 > n and cur:
            out.append(cur)
            cur = w
        else:
            cur = f'{cur} {w}'.strip()
    if cur:
        out.append(cur)
    return out


def paper(doc, deck: p68.Deck, checks):
    psp = doc.layouts.new('A3 1-200')
    psp.page_setup(size=(SHEET_W, SHEET_H), margins=(0, 0, 0, 0), units='mm')
    # Frame and zone markers.
    for inset, lw in ((8, 70), (10, 18)):
        psp.add_lwpolyline([(inset, inset), (SHEET_W - inset, inset), (SHEET_W - inset, SHEET_H - inset), (inset, SHEET_H - inset)],
                           close=True, dxfattribs={'layer': 'G-ANNO-TTLB', 'lineweight': lw})
    for i in range(8):
        for yy in (9, SHEET_H - 9):
            ptext(psp, str(i + 1), 10 + 50 * i + 25, yy, 1.2, MUTED, align=TextEntityAlignment.MIDDLE_CENTER)
    for i in range(6):
        for xx in (9, SHEET_W - 9):
            ptext(psp, 'FEDCBA'[i], xx, 10 + 50 * i + 25, 1.2, MUTED, align=TextEntityAlignment.MIDDLE_CENTER)

    # Header.
    ptext(psp, f'{deck.name.upper()}  ·  {deck.meta["elevation"]}', 14, SHEET_H - 19, 3.6, style='P68-BOLD')
    ptext(psp, f'{deck.meta["zone"]} · {deck.status["stage"]}', 14, SHEET_H - 24.5, 1.9, MUTED)
    ptext(psp, p68.STATUS['stage'].upper(), SHEET_W - 14, SHEET_H - 19, 1.9, ACCENT, 'P68-BOLD', TextEntityAlignment.RIGHT)

    # Viewport at 1:200.
    vw = (VIEW['x1'] - VIEW['x0']) / M_PER_MM
    vh = (VIEW['y1'] - VIEW['y0']) / M_PER_MM
    vtop = SHEET_H - 28
    vcx, vcy = SHEET_W / 2, vtop - vh / 2
    vp = psp.add_viewport(center=(vcx, vcy), size=(vw, vh),
                          view_center_point=((VIEW['x0'] + VIEW['x1']) / 2, (VIEW['y0'] + VIEW['y1']) / 2),
                          view_height=VIEW['y1'] - VIEW['y0'], dxfattribs={'layer': 'G-VIEW'})
    vp.dxf.status = 2
    top = vtop - vh - 5

    # Room schedule.
    x0 = 14
    ptext(psp, 'ROOM SCHEDULE', x0, top - 3, 2.2, style='P68-BOLD')
    cols = [(0, 'NO.'), (9, 'ROOM'), (70, 'L × B (m)'), (93, 'AREA m²'), (110, 'FLOOR FINISH (PROPOSED)'), (158, 'STATUS')]
    y = top - 9
    for cx, t in cols:
        ptext(psp, t, x0 + cx, y, 1.35, MUTED, 'P68-BOLD')
    psp.add_line((x0, y - 1.6), (x0 + 186, y - 1.6), dxfattribs={'layer': 'G-ANNO-TABL', 'lineweight': 35})
    rows = sorted(deck.rooms, key=lambda r: r.num)
    step = 4.3
    for i, r in enumerate(rows):
        yy = y - 5 - i * step
        if i % 2 == 0:
            hatch_solid(psp, [(x0, yy - 2.0), (x0 + 186, yy - 2.0), (x0 + 186, yy + 2.3), (x0, yy + 2.3)], (245, 247, 248), 'G-ANNO-TABL')
        fin = p68.FINISHES['finishes'][r.finish]['label']
        vals = [str(r.num), r.name, f'{r.w:.2f} × {r.h:.2f}', f'{r.area:.1f}', fin, p68.STATUS_LABEL[r.status]]
        for (cx, _), v in zip(cols, vals):
            ptext(psp, v, x0 + cx + (4.5 if cx == 158 else 0), yy - 0.6, 1.45, layer='G-ANNO-TABL')
        sw = [(x0 + 158, yy - 1.1), (x0 + 161.4, yy - 1.1), (x0 + 161.4, yy + 1.5), (x0 + 158, yy + 1.5)]
        hatch_solid(psp, sw, STATUS_FILL[r.status], 'G-ANNO-TABL')
        psp.add_lwpolyline(sw, close=True, dxfattribs={'layer': 'G-ANNO-TABL', 'true_color': tc(STATUS_EDGE[r.status])})
    yy = y - 5 - len(rows) * step + 1.4
    psp.add_line((x0, yy), (x0 + 186, yy), dxfattribs={'layer': 'G-ANNO-TABL', 'lineweight': 35})
    ptext(psp, 'ASSIGNED', x0 + 9, yy - 3.6, 1.45, style='P68-BOLD')
    ptext(psp, f'{deck.assigned:.1f}', x0 + 93, yy - 3.6, 1.45, style='P68-BOLD')
    ptext(psp, f'of {deck.outline_area:.0f} m² deck outline ({deck.assigned / deck.outline_area * 100:.0f}%)', x0 + 110, yy - 3.6, 1.4, MUTED)

    # General notes, below the schedule.
    ny = yy - 12
    ptext(psp, 'GENERAL NOTES', x0, ny, 2.0, style='P68-BOLD')
    notes = [
        'Dimensions in metres. X is measured from the aft perpendicular (AP, X 0) toward the bow; Y is positive to port. Levels are above the design waterline (DWL).',
        'Room positions were read from the General Arrangement schematic (P68-KETCH-D) at about 14 px per metre. They are not dimensioned. Do not scale for construction.',
        'Doors and partitions are indicative and placed by rule: one 0.90 m door per room onto the nearest route. Clear widths exceed the 0.815 m ADA minimum.',
        'Lift shafts are schematic footprints. Cars are shown at 1.5 × 2.0 m internal, which clears the ADA minimum of 1.372 × 1.73 m.',
        'Mast positions are approximate, read from the longitudinal section. Tank outlines are gross envelopes; capacities are not calculated.',
        'Room data (status, finish, furniture) is stored as P68 XDATA on each A-AREA polyline. Regenerate with npm run build:cad.',
    ]
    ny -= 5
    for i, n in enumerate(notes, start=1):
        lines = wrap(n, 128)
        ptext(psp, f'{i}.', x0, ny, 1.4, ACCENT)
        for ln in lines:
            ptext(psp, ln, x0 + 4, ny, 1.4)
            ny -= 3.3
        ny -= 0.9

    # Revisions and reference drawings, lower left beside the title block.
    rx, ry = x0, 14
    ptext(psp, 'REVISIONS', rx, ry + 41, 1.9, style='P68-BOLD')
    rcols = [(0, 'REV'), (12, 'DATE'), (34, 'DESCRIPTION'), (150, 'BY'), (168, 'CHK')]
    for cx, t in rcols:
        ptext(psp, t, rx + cx, ry + 36, 1.3, MUTED, 'P68-BOLD')
    psp.add_line((rx, ry + 34.6), (rx + 186, ry + 34.6), dxfattribs={'layer': 'G-ANNO-TABL', 'lineweight': 25})
    for cx, t in zip([c for c, _ in rcols], ['A', p68.ISSUE_DATE, 'First issue. Generated from layout/decks-layout.json, draft 00.', 'P68', '—']):
        ptext(psp, t, rx + cx, ry + 31, 1.4, layer='G-ANNO-TABL')
    psp.add_line((rx, ry + 29), (rx + 186, ry + 29), dxfattribs={'layer': 'G-ANNO-TABL', 'true_color': tc(FAINT)})
    ptext(psp, 'REFERENCE DRAWINGS', rx, ry + 22, 1.9, style='P68-BOLD')
    refs = ['P68-KETCH-D  General Arrangement schematic (source of room positions)',
            'P68-KETCH-E  Vertical space schedule (deck levels)',
            'P68-ENG-01 to 05  Engineering deck plans, this set · drawings/cad/*.dxf',
            'elevation-port.svg, elevation-aft.svg  Schematic elevations · layout/accessibility.json  Criteria']
    for i, t in enumerate(refs):
        ptext(psp, t, rx, ry + 17 - i * 3.6, 1.4)

    # Deck status panel.
    sx, sw_ = 206, 118
    sbot = 64
    psp.add_lwpolyline([(sx, sbot), (sx + sw_, sbot), (sx + sw_, top), (sx, top)], close=True, dxfattribs={'layer': 'G-ANNO-TABL', 'lineweight': 25})
    hatch_solid(psp, [(sx, sbot), (sx + sw_, sbot), (sx + sw_, top), (sx, top)], (250, 251, 251), 'G-ANNO-TABL')
    ptext(psp, 'DECK STATUS', sx + 3, top - 5, 2.2, style='P68-BOLD')
    y = top - 11
    st = deck.status
    counts = {s: sum(1 for r in deck.rooms if r.status == s) for s in p68.STATUS_LABEL}
    named, restricted = p68.systems_for(deck.name)
    sys_txt = ', '.join(s['name'] for s in named) or 'None cleared for release'
    if restricted:
        sys_txt += f' (+{restricted} restricted)'
    rows_kv = [
        ('Stage', st['stage'], INK),
        ('Datum', f"{deck.meta['elevation']} above DWL, to +{deck.top:.2f}", INK),
        ('Zone', deck.meta['zone'], INK),
        ('Assigned', f'{deck.assigned:.0f} m² of {deck.outline_area:.0f} m² ({deck.assigned / deck.outline_area * 100:.0f}%)', INK),
        ('Rooms', f"{counts['ga']} from GA · {counts['resolved']} resolved · {counts['inferred']} inferred", INK),
        ('Lift stops', ', '.join(p68.lift_stops(deck.name)) or 'None on this level', INK),
        ('Guest level', 'Yes: accessible route required' if deck.name in p68.GUEST_LEVELS else 'No: crew and technical', INK),
        *[(f'{n} check', ('PASS  ' if ok else 'CHECK  ') + line, GOOD if ok else (198, 40, 40)) for n, ok, line in checks],
        ('Systems', sys_txt, INK),
    ]
    for k, v, c in rows_kv:
        ptext(psp, k, sx + 3, y, 1.35, MUTED)
        for ln in wrap(v, 62):
            ptext(psp, ln, sx + 27, y, 1.4, c)
            y -= 3.3
        y -= 0.9
    psp.add_line((sx + 3, y + 1.5), (sx + sw_ - 3, y + 1.5), dxfattribs={'layer': 'G-ANNO-TABL', 'true_color': tc(FAINT)})
    y -= 2.5
    ptext(psp, 'OPEN ITEMS', sx + 3, y, 1.9, ACCENT, 'P68-BOLD')
    y -= 5
    for i, item in enumerate(st['open'], start=1):
        ptext(psp, f'{i}.', sx + 3, y, 1.4, ACCENT)
        for ln in wrap(item, 76):
            ptext(psp, ln, sx + 7, y, 1.4)
            y -= 3.3
        y -= 0.9

    # Key plan.
    kx, ky = 330, top - 40
    ptext(psp, 'KEY PLAN · LONGITUDINAL', kx, top - 3, 1.8, style='P68-BOLD')
    ks = 1.05  # mm per metre
    kp = lambda x, z: (kx + 2 + x * ks, ky + 6 + z * ks * 1.5)  # noqa: E731
    hull = [kp(x / 2, -2.5 * max(0.0, 1 - ((x / 2 - 34) / 34) ** 2) ** 0.5) for x in range(0, 137)]
    hatch_solid(psp, hull + [kp(68, 0), kp(0, 0)], (207, 216, 220), 'G-ANNO-LEGN')
    for d in p68.decks():
        a, b = d.extent
        pts = [kp(a, d.z), kp(b, d.z), kp(b, d.top), kp(a, d.top)]
        hatch_solid(psp, pts, ACCENT if d.name == deck.name else (236, 239, 241), 'G-ANNO-LEGN')
        psp.add_lwpolyline(pts, close=True, dxfattribs={'layer': 'G-ANNO-LEGN', 'lineweight': 13})
    psp.add_line(kp(-2, 0), kp(70, 0), dxfattribs={'layer': 'G-ANNO-LEGN', 'true_color': tc((42, 159, 214)), 'linetype': 'DASHED', 'ltscale': 0.2})
    ptext(psp, 'DWL', *kp(70.8, -0.4), 1.1, (42, 159, 214))

    # Legend.
    ly = top - 50
    ptext(psp, 'LEGEND', kx, ly, 1.9, style='P68-BOLD')
    items = [(STATUS_FILL['ga'], STATUS_EDGE['ga'], None, 'Room read from the GA sheet'),
             (STATUS_FILL['resolved'], STATUS_EDGE['resolved'], None, 'Resolved decision'),
             (STATUS_FILL['inferred'], STATUS_EDGE['inferred'], None, 'Inferred from schematic, to check'),
             ((255, 255, 255), INK, 'NET', 'Route: lobby, passage, corridor'),
             ((255, 255, 255), INK, 'ANSI31', 'Tank or void, gross envelope'),
             (LIFT_FILL, LIFT, None, 'Lift shaft, car 1.5 × 2.0 m')]
    for i, (fc, ec, pat, label) in enumerate(items):
        yy = ly - 6 - i * 4.6
        sw = [(kx, yy - 1.3), (kx + 5, yy - 1.3), (kx + 5, yy + 1.5), (kx, yy + 1.5)]
        hatch_solid(psp, sw, fc, 'G-ANNO-LEGN')
        if pat:
            hatch_pattern(psp, sw, pat, 0.28, (120, 130, 135), 'G-ANNO-LEGN')
        psp.add_lwpolyline(sw, close=True, dxfattribs={'layer': 'G-ANNO-LEGN', 'true_color': tc(ec)})
        ptext(psp, label, kx + 7, yy - 0.5, 1.4)
    yy = ly - 6 - len(items) * 4.6
    psp.add_arc((kx + 0.5, yy - 1.3), 3.2, 0, 90, dxfattribs={'layer': 'G-ANNO-LEGN'})
    psp.add_line((kx + 0.5, yy - 1.3), (kx + 0.5, yy + 1.9), dxfattribs={'layer': 'G-ANNO-LEGN', 'lineweight': 25})
    ptext(psp, 'Indicative door, 0.90 m leaf', kx + 7, yy - 0.5, 1.4)
    yy -= 4.6
    psp.add_line((kx, yy), (kx + 5, yy), dxfattribs={'layer': 'G-ANNO-LEGN', 'linetype': 'DASHED', 'ltscale': 0.15})
    ptext(psp, 'Indicative partition, count not set', kx + 7, yy - 0.5, 1.4)
    yy -= 4.6
    psp.add_circle((kx + 2.5, yy), 1.3, dxfattribs={'layer': 'G-ANNO-LEGN'})
    ptext(psp, '3', kx + 2.5, yy, 1.2, style='P68-BOLD', align=TextEntityAlignment.MIDDLE_CENTER)
    ptext(psp, 'Room tag, see schedule', kx + 7, yy - 0.5, 1.4)

    # Title block.
    tb = psp.add_blockref('P68-TITLE', (214, 14), dxfattribs={'layer': 'G-ANNO-TTLB'})
    tb.add_auto_attribs({
        'DWGNO': f'P68-ENG-{deck.index:02d}', 'REV': 'A · draft 00', 'SCALE': '1:200 @ A3', 'DATE': p68.ISSUE_DATE,
        'SOURCE': 'decks-layout.json', 'DATUM': 'DWL · X from AP', 'STATUS': 'Concept · for review',
        'SHEET': f'{deck.index} of {len(p68.LAYOUT["decks"])}',
        'TITLE': f'ENGINEERING DECK PLAN · {deck.name.upper()}',
        'SUBTITLE': 'Deck status, room schedule, indicative doors and partitions',
    })
    doc.layouts.set_active_layout('A3 1-200')
    return psp


# ---- Plotting --------------------------------------------------------------------

PLOT_CFG = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR,
                         lineweight_policy=LineweightPolicy.ABSOLUTE, min_lineweight=0.09)


def plot(doc, name):
    psp = doc.layouts.get(name)
    page = layout.Page(SHEET_W, SHEET_H, layout.Units.mm, margins=layout.Margins.all(0))
    settings = layout.Settings(fit_page=False, scale=1)
    ctx = RenderContext(doc)
    sb = svg.SVGBackend()
    Frontend(ctx, sb, config=PLOT_CFG).draw_layout(psp, finalize=True)
    svg_str = sb.get_string(page, settings=settings)
    pb = pymupdf.PyMuPdfBackend()
    Frontend(RenderContext(doc), pb, config=PLOT_CFG).draw_layout(psp, finalize=True)
    pdf_bytes = pb.get_pdf_bytes(page, settings=settings)
    return svg_str, pdf_bytes


def main():
    CAD.mkdir(parents=True, exist_ok=True)
    checks = [('Layout', *p68.run_validator('validate-layout.mjs')), ('Access', *p68.run_validator('validate-access.mjs'))]
    book = fitz.open()
    files = []
    for deck in p68.decks():
        doc = new_doc()
        doc.header['$PROJECTNAME'] = 'P68 Ketch'
        model(doc, deck)
        paper(doc, deck, checks)
        stem = f'P68-ENG-{deck.index:02d}-{p68.slug(deck.name)}'
        doc.saveas(CAD / f'{stem}.dxf')
        svg_str, pdf_bytes = plot(doc, 'A3 1-200')
        app_name = f'eng-deck-{deck.file_stem}.svg'
        (p68.OUT / app_name).write_text(svg_str)
        book.insert_pdf(fitz.open(stream=io.BytesIO(pdf_bytes).getvalue(), filetype='pdf'))
        files.append(app_name)
        print(f'wrote drawings/cad/{stem}.dxf, drawings/{app_name}')
    book.set_metadata({'title': 'P68 Ketch engineering deck plans (schematic)', 'author': 'P68 Ketch design team', 'creationDate': '', 'modDate': ''})
    book.save(p68.OUT / 'P68-engineering-deck-plans.pdf', garbage=4, deflate=True)
    print('wrote drawings/P68-engineering-deck-plans.pdf')
    return files


if __name__ == '__main__':
    main()
