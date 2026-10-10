"""The P68 vessel model for exterior renders: hull, superstructure, rig and sails.

Main dimensions come from the repository (LOA 68.0 m, beam 12.1 m, deck levels from
the vertical space schedule, mast stations from the longitudinal section, the Lido
roof and pilot house cover heights from accessibility.json). Everything the data does
not set is illustrative and labelled as such in the renders: hull lines, superstructure
plan shape, rig heights (main about 55 m and mizzen about 42 m above the waterline),
sail plan and the tender.
"""
from __future__ import annotations

import math

import bpy
from PIL import Image, ImageDraw

import bkit as K
import p68

LOA = p68.LOA
HB = p68.BEAM / 2
MAIN_X, MIZZEN_X = p68.MASTS['Main'], p68.MASTS['Mizzen']
MAIN_TOP, MIZZEN_TOP = 55.0, 42.0  # illustrative air draft of each mast (m above DWL)
SHEER = 4.4  # bulwark top amidships (Main deck +3.35 plus bulwark)


def hb_render(x: float) -> float:
    """Half-breadth at the sheer: a transom aft and a fine entry forward (illustrative lines)."""
    if x <= 34:
        t = (34 - x) / 40
        return HB * math.sqrt(max(0.0, 1 - t * t))
    t = (x - 34) / 34
    return HB * max(0.0, 1 - t ** 1.9) ** 0.72


def sheer_z(x: float) -> float:
    return SHEER + 0.9 * max(0.0, (x - 40) / 28) ** 2 + 0.15 * max(0.0, (12 - x) / 12)


def keel_z(x: float) -> float:
    """Canoe-body bottom: -2.5 m amidships, rising to the transom and the stem."""
    if x <= 34:
        t = (34 - x) / 34
        return -2.5 + 2.75 * t ** 2.2
    t = (x - 34) / 34
    return -2.5 + (sheer_z(68) + 2.5) * t ** 3.2


def hull_paint():
    m = bpy.data.materials.new('Hull paint')
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.28
    bsdf.inputs['Coat Weight'].default_value = 0.3
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    map_ = nt.nodes.new('ShaderNodeMapRange')
    map_.inputs['From Min'].default_value = -1.0
    map_.inputs['From Max'].default_value = 1.0
    nt.links.new(sep.outputs['Z'], map_.inputs['Value'])
    nt.links.new(map_.outputs['Result'], ramp.inputs['Fac'])
    cr = ramp.color_ramp
    cr.interpolation = 'CONSTANT'
    cr.elements[0].position = 0.0
    cr.elements[0].color = (*K.srgb('#5a1f1f'), 1)  # antifoul below the boot top
    cr.elements[1].position = 0.5
    cr.elements[1].color = (*K.srgb('#eef0f1'), 1)  # boot top 0 to +0.35
    e = cr.elements.new(0.5 + 0.35 / 2)
    e.color = (*K.srgb('#0d1b2a'), 1)  # navy topsides
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    return m


def build_hull(M):
    stations = [i * 0.5 for i in range(0, 137)]
    ring = 40
    verts, faces = [], []
    for x in stations:
        hb = max(0.02, hb_render(x))
        zs, zb = sheer_z(x), keel_z(x)
        mid = 1 - abs(x - 34) / 34
        n = 2.0 + 1.6 * mid  # fuller sections amidships
        for j in range(ring + 1):
            th = -math.pi / 2 + math.pi * j / ring
            y = hb * math.copysign(abs(math.sin(th)) ** (2 / n), th)
            z = zs - (zs - zb) * abs(math.cos(th)) ** (2 / n)
            verts.append((x, y, z))
    rl = ring + 1
    for i in range(len(stations) - 1):
        for j in range(ring):
            a = i * rl + j
            faces.append((a, a + 1, a + rl + 1, a + rl))
    faces.append(tuple(range(rl - 1, -1, -1)))  # transom
    o = K.mesh('Hull', verts, faces, hull_paint(), smooth=True)
    # Teak deck inside the bulwark at the Main deck level, aft and forward of the superstructure.
    pts = [(x, hb_render(x) - 0.25) for x in stations[1:-4]] + [(x, -(hb_render(x) - 0.25)) for x in reversed(stations[1:-4])]
    K.extrude_polygon('Main deck', pts, 3.3, 3.35, K.floor_material('teak', 8, 4, 60))
    # Cap rail along the sheer.
    for side in (1, -1):
        for i in range(0, len(stations) - 3, 2):
            x0, x1 = stations[i], stations[i + 2]
            K.rod('Caprail', (x0, side * (hb_render(x0) - 0.05), sheer_z(x0)), (x1, side * (hb_render(x1) - 0.05), sheer_z(x1)), 0.08, M['teak_plain'], 6)
    return o


def rounded_plan(x0, x1, hw, r_fwd, r_aft=1.0, n=14):
    """Superstructure plan: straight sides, elliptical forward end, small aft radius."""
    pts = []
    for i in range(n + 1):
        a = -math.pi / 2 + math.pi * i / n
        pts.append((x1 - r_fwd + r_fwd * math.cos(a), hw * math.sin(a)))
    for i in range(n // 2 + 1):
        a = math.pi / 2 + math.pi * i / (n // 2)
        pts.append((x0 + r_aft + r_aft * math.cos(a), hw * math.sin(a) * (1 if abs(math.sin(a)) > 0.99 else 1)))
    return pts


def tier(name, x0, x1, hw, z0, z1, M, r_fwd, glass=(0.25, 0.85), night=False):
    """One superstructure level: white body, dark glazing band, white fascia and deck edge."""
    pts = rounded_plan(x0, x1, hw, r_fwd)
    g0 = z0 + (z1 - z0) * glass[0]
    g1 = z0 + (z1 - z0) * glass[1]
    K.extrude_polygon(f'{name} base', pts, z0, g0, M['super'])
    gl = K.principled('Window lit', K.srgb('#2c2a24'), rough=0.05, coat=1.0, emission=K.srgb('#ffcf8a'), estrength=2.2) if night else M['tinted_glass']
    K.extrude_polygon(f'{name} glass', [(x, y * 0.985) for x, y in pts], g0, g1, gl)
    K.extrude_polygon(f'{name} fascia', [(x, y * 1.0) for x, y in pts], g1, z1, M['super'])
    # Deck edge overhang above the tier.
    over = [(x + (0.25 if x > (x0 + x1) / 2 else -0.15), y * (hw + 0.3) / hw) for x, y in pts]
    K.extrude_polygon(f'{name} overhang', over, z1 - 0.12, z1 + 0.05, M['super'])


def glass_rail(name, pts, z, M, h=1.05):
    for i in range(len(pts) - 1):
        (xa, ya), (xb, yb) = pts[i], pts[i + 1]
        L = math.hypot(xb - xa, yb - ya)
        if L < 0.05:
            continue
        nx, ny = -(yb - ya) / L * 0.012, (xb - xa) / L * 0.012
        K.extrude_polygon(f'{name}{i}', [(xa - nx, ya - ny), (xb - nx, yb - ny), (xb + nx, yb + ny), (xa + nx, ya + ny)], z, z + h, M['glass'])
        K.rod(f'{name}top{i}', (xa, ya, z + h), (xb, yb, z + h), 0.03, M['chrome'], 6)


def build_superstructure(M, night=False):
    # Main tier over the hull deck (+3.35 to +6.60).
    tier('Main', 9.0, 58.5, 4.6, 3.35, 6.6, M, r_fwd=7.0, night=night)
    # Commander tier, enclosed forward of the Lido (+6.60 to +9.30).
    tier('Commander', 21.5, 53.5, 4.0, 6.6, 9.3, M, r_fwd=6.0, glass=(0.12, 0.92), night=night)
    # Aft Lido terrace deck with the pool, and the roof (sun deck) above on slim columns.
    lido = rounded_plan(6.5, 21.6, 4.3, 1.0, 1.4)
    K.extrude_polygon('Lido deck', lido, 6.45, 6.62, K.floor_material('teak', 15, 8.6, 50))
    pw, pl, px = 4.6, 3.0, 14.2
    K.box('Pool coping', px - pl / 2 - 0.3, -pw / 2 - 0.3, 6.62, px + pl / 2 + 0.3, pw / 2 + 0.3, 6.68, M['stone_top'])
    K.box('Pool', px - pl / 2, -pw / 2, 6.0, px + pl / 2, pw / 2, 6.69, M['pool_tile'])
    K.plane('Pool water', px - pl / 2, -pw / 2, px + pl / 2, pw / 2, 6.64, M['water'])
    roof = rounded_plan(6.9, 21.6, 3.9, 1.0, 1.0)
    K.extrude_polygon('Sun deck roof', roof, 9.1, 9.3, M['super'])
    K.extrude_polygon('Sun deck teak', [(x, y * 0.97) for x, y in roof], 9.3, 9.33, K.floor_material('teak', 15, 7.8, 50))
    for x in (8.0, 13.0, 18.0):
        for y in (-3.6, 3.6):
            K.cylinder('Lido column', x, y, 6.62, 0.09, 2.5, M['chrome'], 16)
    glass_rail('Lido rail', [(x, y * 1.02) for x, y in lido[len(lido) // 2:]] + [lido[0]], 6.62, M)
    glass_rail('Roof rail', [(x, y * 1.0) for x, y in roof], 9.33, M)
    # Outdoor pilot house cover at the aft end of the sun deck, to +11.70.
    cover = rounded_plan(7.2, 12.8, 2.8, 1.6, 0.8)
    K.extrude_polygon('Pilot house cover', cover, 11.5, 11.7, M['super'])
    for x, y in ((7.6, -2.4), (7.6, 2.4), (12.2, -2.4), (12.2, 2.4)):
        K.cylinder('Cover post', x, y, 9.33, 0.07, 2.2, M['chrome'], 16)
    K.box('Outdoor helm', 9.6, -1.4, 9.33, 10.4, 1.4, 10.3, M['walnut'], bevel=0.04)
    for y in (-0.6, 0.6):
        K.cylinder('Helm seat', 8.8, y, 9.33, 0.25, 0.75, M['cognac'], 20)
    # Bridge tier (+9.30 to +11.70) and its roof with radar and domes.
    tier('Bridge', 22.0, 51.0, 3.3, 9.3, 11.7, M, r_fwd=5.5, glass=(0.18, 0.9), night=night)
    K.cylinder('Radar post', 33, 0, 11.75, 0.18, 1.6, M['super'])
    K.cbox('Radar', 33, 0, 13.35, 4.2, 0.35, 0.22, M['steel_white'])
    for y in (-1.6, 1.6):
        dome = K.cylinder('Dome', 29, y, 11.75, 0.45, 0.6, M['steel_white'], 24, r_top=0.42)
        K.cylinder('Dome cap', 29, y, 12.35, 0.42, 0.18, M['steel_white'], 24, r_top=0.2)
    # Swim platform at the transom.
    K.box('Swim platform', -1.6, -2.8, 0.45, 0.4, 2.8, 0.75, K.floor_material('teak', 2, 5.6, 60))


def flag_material():
    path = K.TEX_DIR / 'flag-greece.png'
    if not path.exists():
        K.TEX_DIR.mkdir(parents=True, exist_ok=True)
        W, H = 540, 360
        im = Image.new('RGB', (W, H), (255, 255, 255))
        d = ImageDraw.Draw(im)
        blue = (13, 94, 175)
        for i in range(9):
            if i % 2 == 0:
                d.rectangle([0, i * H / 9, W, (i + 1) * H / 9], fill=blue)
        d.rectangle([0, 0, 5 * H / 9, 5 * H / 9], fill=blue)
        d.rectangle([2 * H / 9, 0, 3 * H / 9, 5 * H / 9], fill=(255, 255, 255))
        d.rectangle([0, 2 * H / 9, 5 * H / 9, 3 * H / 9], fill=(255, 255, 255))
        im.save(path)
    m = bpy.data.materials.new('Flag')
    nt = m.node_tree
    img = nt.nodes.new('ShaderNodeTexImage')
    img.image = bpy.data.images.load(str(path))
    nt.links.new(img.outputs['Color'], nt.nodes['Principled BSDF'].inputs['Base Color'])
    nt.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.8
    return m


def build_flag(M, x=0.2, wind=0.0):
    K.rod('Flagstaff', (x, 0, 4.4), (x - 0.9, 0, 7.4), 0.03, M['teak_plain'])
    v, f = [], []
    nx, ny = 10, 4
    for i in range(nx + 1):
        for j in range(ny + 1):
            u = i / nx
            v.append((x - 0.9 - u * 2.1, 0.12 * math.sin(u * 5 + wind) * u, 7.35 - j / ny * 1.4))
    for i in range(nx):
        for j in range(ny):
            a = i * (ny + 1) + j
            f.append((a, a + ny + 1, a + ny + 2, a + 1))
    o = K.mesh('Ensign', v, f, flag_material(), smooth=True)
    uv = o.data.uv_layers.new(name='UVMap')
    for poly in o.data.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            i, j = divmod(vi, ny + 1)
            uv.data[li].uv = (i / nx, 1 - j / ny)
    o.modifiers.new('Solid', 'SOLIDIFY').thickness = 0.01


def build_rig(M, sails=False, boom_angle=0.0, heel=0.0):
    """Masts, booms, spreaders and standing rigging; sails when underway."""
    objs = []
    for name, x, top in (('Main', MAIN_X, MAIN_TOP), ('Mizzen', MIZZEN_X, MIZZEN_TOP)):
        base = 9.3 if name == 'Main' else 9.33
        objs.append(K.cylinder(f'{name} mast', x, 0, base, 0.42, top - base, M['carbon'], 24, r_top=0.22))
        n_spr = 4 if name == 'Main' else 3
        for k in range(1, n_spr + 1):
            zz = base + (top - base) * k / (n_spr + 1)
            span = 2.6 * (1 - 0.18 * k)
            objs.append(K.rod(f'{name} spreader', (x - 0.4, -span, zz), (x - 0.4, span, zz), 0.07, M['carbon']))
        boom_z = 13.6 if name == 'Main' else 13.0
        boom_len = 16.5 if name == 'Main' else 12.5
        bx = x - boom_len * math.cos(boom_angle)
        by = -boom_len * math.sin(boom_angle)
        objs.append(K.rod(f'{name} boom', (x, 0, boom_z), (bx, by, boom_z), 0.3, M['carbon'], 16))
        for side in (-1, 1):
            chain_y = side * (hb_render(x) - 0.3)
            objs.append(K.rod(f'{name} shroud', (x - 0.3, 0, top - 1.5), (x - 0.6, chain_y, sheer_z(x)), 0.025, M['rope']))
            objs.append(K.rod(f'{name} lower', (x, 0, base + (top - base) * 0.4), (x + 1.2, chain_y, sheer_z(x)), 0.022, M['rope']))
        if sails:
            # Mainsail or mizzen: luff on the mast, foot on the boom, slight roach.
            head = (x - 0.4, 0, top - 2.0)
            tack = (x - 0.5, 0, boom_z + 0.4)
            clew = (bx + 0.6 * math.cos(boom_angle), by + 0.6 * math.sin(boom_angle), boom_z + 0.5)
            objs.append(sail(f'{name}sail', tack, head, clew, M, camber=0.07, side=-1 if boom_angle > 0 else 1))
    # Forestay and genoa, triatic and backstays.
    stem = (LOA + 0.6, 0, sheer_z(LOA) + 0.3)
    objs.append(K.rod('Forestay', (MAIN_X + 0.3, 0, MAIN_TOP - 1.0), stem, 0.03, M['rope']))
    objs.append(K.rod('Inner forestay', (MAIN_X + 0.3, 0, MAIN_TOP * 0.72), (LOA - 6.0, 0, sheer_z(LOA - 6)), 0.025, M['rope']))
    objs.append(K.rod('Triatic', (MAIN_X - 0.2, 0, MAIN_TOP - 1.5), (MIZZEN_X + 0.2, 0, MIZZEN_TOP - 0.6), 0.025, M['rope']))
    for side in (-1, 1):
        objs.append(K.rod('Backstay', (MIZZEN_X - 0.2, 0, MIZZEN_TOP - 0.6), (0.6, side * 2.6, 4.6), 0.025, M['rope']))
    if sails:
        clew = (MAIN_X + 4.0, -3.6 if boom_angle > 0 else 3.6, sheer_z(MAIN_X) + 1.6)
        objs.append(sail('Genoa', stem, (MAIN_X + 1.6, 0, MAIN_TOP - 3.5), clew, M, camber=0.09, side=-1 if boom_angle > 0 else 1))
    return objs


def sail(name, tack, head, clew, M, camber=0.07, side=1, nu=14, nv=18):
    """Triangular sail with camber, as a mesh over (u along the foot, v up the luff)."""
    from mathutils import Vector
    T, Hd, C = Vector(tack), Vector(head), Vector(clew)
    foot = C - T
    up = Hd - T
    nrm = foot.cross(up).normalized() * side
    verts, faces = [], []
    for j in range(nv + 1):
        v = j / nv
        for i in range(nu + 1):
            u = i / nu * (1 - v)
            p = T + foot * u + up * v
            depth = camber * foot.length * (1 - v) * math.sin(math.pi * (u / max(1e-6, 1 - v))) if v < 1 else 0
            verts.append(tuple(p + nrm * depth))
    for j in range(nv):
        for i in range(nu):
            a = j * (nu + 1) + i
            faces.append((a, a + 1, a + nu + 2, a + nu + 1))
    o = K.mesh(name, verts, faces, M['sail'], smooth=True)
    o.modifiers.new('Solid', 'SOLIDIFY').thickness = 0.01
    return o


def build_tender(M, x, y, rot=0.0):
    """A 7 m tender, illustrative."""
    pts = [(-3.5, 0.0), (-3.4, 1.15), (2.0, 1.25), (3.5, 0.0), (2.0, -1.25), (-3.4, -1.15)]
    c, s = math.cos(rot), math.sin(rot)
    P = [(x + px * c - py * s, y + px * s + py * c) for px, py in pts]
    K.extrude_polygon('Tender hull', P, -0.25, 0.6, M['tender'])
    K.extrude_polygon('Tender tube', [(x + px * 1.03 * c - py * 1.05 * s, y + px * 1.03 * s + py * 1.05 * c) for px, py in pts], 0.25, 0.65, M['fender'])
    K.cbox('Tender console', x - 0.2 * c, y - 0.2 * s, 0.6, 1.0, 0.8, 0.7, M['tender'], rot=rot, bevel=0.05)
    K.cbox('Tender seat', x - 1.8 * c, y - 1.8 * s, 0.6, 1.0, 1.8, 0.4, M['ivory'], rot=rot, bevel=0.05)


def hull_windows(M, night=False):
    """Rows of guest cabin windows in the topsides at Tween level (illustrative)."""
    mat = K.principled('Hull window lit', K.srgb('#2c2a24'), rough=0.05, coat=1.0, emission=K.srgb('#ffcf8a'), estrength=2.0) if night else M['tinted_glass']
    for side in (1, -1):
        for x in [10 + 2.6 * k for k in range(7)] + [28 + 2.6 * k for k in range(7)]:
            y = side * (hb_render(x) + 0.004)
            K.cbox('Hull window', x, y, 1.6, 1.7, 0.12, 0.42, mat, bevel=0.06)


def build_vessel(M, sails=False, boom_angle=0.0, night=False):
    K.collection('Vessel')
    build_hull(M)
    hull_windows(M, night=night)
    build_superstructure(M, night=night)
    build_rig(M, sails=sails, boom_angle=boom_angle)
    build_flag(M)
    # Stanchions and wires along the Main deck sheer, forward of the superstructure.
    for side in (1, -1):
        prev = None
        for x in range(58, 67):
            y = side * (hb_render(x) - 0.2)
            K.cylinder('Stanchion', x, y, sheer_z(x), 0.025, 0.75, M['chrome'], 8)
            if prev:
                K.rod('Guardwire', (prev[0], prev[1], sheer_z(prev[0]) + 0.75), (x, y, sheer_z(x) + 0.75), 0.012, M['chrome'], 6)
            prev = (x, y)


def vessel_parent(heel_deg=0.0, pitch_deg=0.0, yaw_deg=0.0, z=0.0):
    """Parent every vessel object to an empty so the boat can heel and turn as one."""
    e = bpy.data.objects.new('VesselRoot', None)
    bpy.context.scene.collection.objects.link(e)
    for o in bpy.data.collections['Vessel'].objects:
        o.parent = e
    e.location = (0, 0, z)
    e.rotation_euler = (math.radians(heel_deg), math.radians(pitch_deg), math.radians(yaw_deg))
    return e


# ---- Environment ------------------------------------------------------------------

def water(M, size=3000, wave_scale=0.6, wind=6.0, chop=0.8, color='#1b5a7a', shallow=None, resolution=14, foam=False, time=4.0):
    K.collection('Sea')
    bpy.ops.mesh.primitive_plane_add(size=2, location=(34, 0, 0))
    o = bpy.context.object
    bpy.context.scene.collection.objects.unlink(o) if o.name in bpy.context.scene.collection.objects else None
    bpy.data.collections['Sea'].objects.link(o) if o.name not in bpy.data.collections['Sea'].objects else None
    oc = o.modifiers.new('Ocean', 'OCEAN')
    oc.geometry_mode = 'GENERATE'
    oc.size = 1.0
    oc.spatial_size = 220
    oc.resolution = resolution
    oc.repeat_x = 12
    oc.repeat_y = 12
    oc.wave_scale = wave_scale
    oc.wind_velocity = wind
    oc.choppiness = chop
    oc.time = time
    oc.use_normals = True
    if foam:
        oc.use_foam = True
        oc.foam_layer_name = 'foam'
        oc.foam_coverage = 0.25
    o.location = (34 - 220 * 6, -220 * 6, 0)
    o.scale = (1, 1, 1)
    m = bpy.data.materials.new('Sea')
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*K.srgb(color), 1)
    bsdf.inputs['Roughness'].default_value = 0.04
    bsdf.inputs['IOR'].default_value = 1.333
    bsdf.inputs['Transmission Weight'].default_value = 0.0
    bsdf.inputs['Specular IOR Level'].default_value = 0.6
    bsdf.inputs['Subsurface Weight'].default_value = 0.0
    if shallow:
        bsdf.inputs['Base Color'].default_value = (*K.srgb(shallow), 1)
    if foam:
        attr = nt.nodes.new('ShaderNodeAttribute')
        attr.attribute_name = 'foam'
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        mix.inputs['A'].default_value = (*K.srgb(shallow or color), 1)
        mix.inputs['B'].default_value = (0.9, 0.92, 0.93, 1)
        ramp = nt.nodes.new('ShaderNodeMapRange')
        ramp.inputs['From Min'].default_value = 0.35
        ramp.inputs['From Max'].default_value = 1.0
        nt.links.new(attr.outputs['Fac'], ramp.inputs['Value'])
        nt.links.new(ramp.outputs['Result'], mix.inputs['Factor'])
        nt.links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    o.data.materials.append(m)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def island(M, cx, cy, rx, ry, h, seed=3, z0=-3.0, village_at=None, n=140):
    """An Aegean island as a heightfield: fbm terrain under a radial falloff, rock on the
    steep faces and olive scrub on the gentle ones. Optional village of white houses."""
    import random

    import numpy as np

    import textures
    rng = np.random.default_rng(seed)
    f1 = textures.noise(n, n, n / 5, rng)
    f2 = textures.noise(n, n, n / 14, rng)
    f3 = textures.noise(n, n, n / 40, rng)
    terrain = 0.55 * f1 + 0.3 * f2 + 0.15 * f3
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1) * 2 - 1
    r = np.sqrt(xx ** 2 + yy ** 2)
    fall = np.clip(1 - r, 0, 1) ** 1.3
    z = z0 + (h - z0) * fall * (0.35 + 0.95 * terrain)
    verts = [(cx + xx[j, i] * rx, cy + yy[j, i] * ry, float(z[j, i])) for j in range(n) for i in range(n)]
    faces = [(j * n + i, j * n + i + 1, (j + 1) * n + i + 1, (j + 1) * n + i) for j in range(n - 1) for i in range(n - 1)]
    o = K.mesh('Island', verts, faces, None, smooth=True)
    mat = bpy.data.materials.new('Island ground')
    nt = mat.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.95
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(geo.outputs['Normal'], sep.inputs['Vector'])
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 0.35
    noise.inputs['Detail'].default_value = 10
    add = nt.nodes.new('ShaderNodeMath')
    add.operation = 'MULTIPLY_ADD'
    add.inputs[1].default_value = 0.25
    nt.links.new(noise.outputs['Fac'], add.inputs[0])
    nt.links.new(sep.outputs['Z'], add.inputs[2])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.elements[0].position = 0.78
    cr.elements[0].color = (*K.srgb('#9a8466'), 1)
    cr.elements[1].position = 0.9
    cr.elements[1].color = (*K.srgb('#6d7448'), 1)
    e = cr.elements.new(0.84)
    e.color = (*K.srgb('#a99a78'), 1)
    nt.links.new(add.outputs['Value'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.4
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    o.data.materials.append(mat)
    if village_at:
        vx, vy, spread, count = village_at
        rnd = random.Random(seed)
        for k in range(count):
            u = vx + rnd.gauss(0, spread)
            v = vy + rnd.gauss(0, spread * 0.6)
            i = int(np.clip((u - cx) / rx * 0.5 + 0.5, 0, 1) * (n - 1))
            j = int(np.clip((v - cy) / ry * 0.5 + 0.5, 0, 1) * (n - 1))
            zz = float(z[j, i])
            if zz < 1.5:
                continue
            w, d, hh = rnd.uniform(5, 9), rnd.uniform(5, 8), rnd.uniform(3.5, 6)
            K.box('Village house', u - w / 2, v - d / 2, zz - 3, u + w / 2, v + d / 2, zz + hh, M['white_render'], bevel=0.2)
            if rnd.random() < 0.08:
                K.cylinder('Village dome', u, v, zz + hh, w * 0.35, w * 0.3, M['blue_door'], 24, r_top=0.4)
    return o
