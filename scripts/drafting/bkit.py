"""Blender toolkit for the P68 renders: scene set-up, materials, primitives, and the
reader that takes room and wall geometry from the DXF sources in drawings/cad/.

Coordinates follow the DXF model space: metres, X from the stern (AP) to the bow,
Y positive to port, Z up from the design waterline (DWL).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import bpy
import ezdxf

import p68
import textures

TEX_DIR = p68.ROOT / 'build' / 'textures'
CAD_DIR = p68.OUT / 'cad'


# ---- Scene -------------------------------------------------------------------

def reset(samples=96, width=1920, height=1080):
    global _COLL
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _MATS.clear()
    _COLL = None
    s = bpy.context.scene
    s.render.engine = 'CYCLES'
    s.cycles.device = 'CPU'
    s.cycles.samples = samples
    s.cycles.use_adaptive_sampling = True
    s.cycles.adaptive_threshold = 0.02
    s.cycles.use_denoising = True
    s.cycles.denoiser = 'OPENIMAGEDENOISE'
    s.cycles.max_bounces = 8
    s.cycles.glossy_bounces = 4
    s.cycles.transmission_bounces = 8
    s.cycles.caustics_reflective = False
    s.cycles.caustics_refractive = False
    s.cycles.blur_glossy = 1.0
    s.render.resolution_x = width
    s.render.resolution_y = height
    s.render.resolution_percentage = 100
    s.render.film_transparent = False
    s.view_settings.view_transform = 'AgX'
    s.view_settings.look = 'AgX - Medium High Contrast'
    s.render.image_settings.file_format = 'PNG'
    s.render.threads_mode = 'AUTO'
    return s


def sky(elevation_deg=35.0, rotation_deg=200.0, strength=1.0, sun_intensity=1.0, sun_disc=True):
    """Physical sky with a sun disc. Returns the sun direction as a vector for a matching sun lamp."""
    s = bpy.context.scene
    w = bpy.data.worlds.new('Sky')
    s.world = w
    nt = w.node_tree
    nt.nodes.clear()
    sk = nt.nodes.new('ShaderNodeTexSky')
    sk.sky_type = 'MULTIPLE_SCATTERING'
    sk.sun_elevation = math.radians(elevation_deg)
    sk.sun_rotation = math.radians(rotation_deg)
    sk.sun_intensity = sun_intensity
    sk.altitude = 50
    sk.sun_disc = sun_disc
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Strength'].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(sk.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    return sk


def flat_world(color=(0.95, 0.95, 0.95), strength=1.0):
    s = bpy.context.scene
    w = bpy.data.worlds.new('Flat')
    s.world = w
    nt = w.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs['Color'].default_value = (*color, 1)
    bg.inputs['Strength'].default_value = strength
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])


def sun(elev=40, azim=200, energy=3.5, angle=1.5, color=(1.0, 0.97, 0.92)):
    d = bpy.data.lights.new('Sun', 'SUN')
    d.energy = energy
    d.angle = math.radians(angle)
    d.color = color
    o = bpy.data.objects.new('Sun', d)
    bpy.context.scene.collection.objects.link(o)
    # Point the lamp along the sun direction (elevation, azimuth measured like the sky node).
    o.rotation_euler = (math.radians(90 - elev), 0, math.radians(azim + 90))
    return o


def area_light(loc, size, energy, rot=(0, 0, 0), color=(1, 0.95, 0.88), shape='RECTANGLE', size_y=None):
    d = bpy.data.lights.new('Area', 'AREA')
    d.energy = energy
    d.shape = shape
    d.size = size
    if size_y is not None:
        d.size_y = size_y
    d.color = color
    o = bpy.data.objects.new('Area', d)
    o.location = loc
    o.rotation_euler = rot
    bpy.context.scene.collection.objects.link(o)
    return o


def point_light(loc, energy, radius=0.05, color=(1, 0.9, 0.78)):
    d = bpy.data.lights.new('Point', 'POINT')
    d.energy = energy
    d.shadow_soft_size = radius
    d.color = color
    o = bpy.data.objects.new('Point', d)
    o.location = loc
    bpy.context.scene.collection.objects.link(o)
    return o


def camera(loc, target, lens=35.0, ortho_scale=None, name='Cam', shift=(0, 0)):
    c = bpy.data.cameras.new(name)
    if ortho_scale:
        c.type = 'ORTHO'
        c.ortho_scale = ortho_scale
    else:
        c.lens = lens
    c.clip_start = 0.05
    c.clip_end = 3000
    c.shift_x, c.shift_y = shift
    o = bpy.data.objects.new(name, c)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc
    look_at(o, target)
    bpy.context.scene.camera = o
    return o


def look_at(obj, target):
    from mathutils import Vector
    d = Vector(target) - Vector(obj.location)
    obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()


def render(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    s = bpy.context.scene
    s.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


# ---- Materials -------------------------------------------------------------------

_MATS: dict[str, bpy.types.Material] = {}


def principled(name, color, rough=0.5, metal=0.0, coat=0.0, sheen=0.0, transmission=0.0, ior=1.45, emission=None, estrength=0.0, alpha=1.0, spec=0.5):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    bsdf = m.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Coat Weight'].default_value = coat
    bsdf.inputs['Sheen Weight'].default_value = sheen
    bsdf.inputs['Transmission Weight'].default_value = transmission
    bsdf.inputs['IOR'].default_value = ior
    bsdf.inputs['Specular IOR Level'].default_value = spec
    bsdf.inputs['Alpha'].default_value = alpha
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1)
        bsdf.inputs['Emission Strength'].default_value = estrength
    _MATS[name] = m
    return m


def srgb(hexstr):
    """Hex colour to linear RGB for Blender."""
    h = hexstr.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


FLOOR_PBR = {
    'teak': dict(rough=0.6), 'walnut': dict(rough=0.3, coat=0.35), 'oak': dict(rough=0.45, coat=0.1),
    'stone': dict(rough=0.5), 'marble': dict(rough=0.15, coat=0.4), 'tile': dict(rough=0.4),
    'carpet': dict(rough=0.95, sheen=0.6), 'epoxy': dict(rough=0.35), 'steel': dict(rough=0.45, metal=0.5),
    'tank': dict(rough=0.7), 'lift': dict(rough=0.28, metal=0.9), 'water': dict(rough=0.02),
}


def floor_material(kind: str, w: float, h: float, ppm: float = 90):
    """Material with a procedural texture image sized exactly to a w × h metre floor."""
    key = f'floor-{kind}-{w:.2f}x{h:.2f}'
    if key in _MATS:
        return _MATS[key]
    ppm = min(ppm, 2400 / max(w, h))
    TEX_DIR.mkdir(parents=True, exist_ok=True)
    path = TEX_DIR / f'{key}.png'
    if not path.exists():
        textures.to_image(textures.material(kind, w, h, ppm)).save(path)
    m = bpy.data.materials.new(key)
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    pbr = FLOOR_PBR.get(kind, {})
    bsdf.inputs['Roughness'].default_value = pbr.get('rough', 0.5)
    bsdf.inputs['Metallic'].default_value = pbr.get('metal', 0.0)
    bsdf.inputs['Coat Weight'].default_value = pbr.get('coat', 0.0)
    bsdf.inputs['Sheen Weight'].default_value = pbr.get('sheen', 0.0)
    img = nt.nodes.new('ShaderNodeTexImage')
    img.image = bpy.data.images.load(str(path))
    img.interpolation = 'Cubic'
    nt.links.new(img.outputs['Color'], bsdf.inputs['Base Color'])
    # Subtle bump from the texture luminance.
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.002
    nt.links.new(img.outputs['Color'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    _MATS[key] = m
    return m


def lib():
    """Shared material library."""
    return {
        'wall': principled('Wall ivory', srgb('#eee8dc'), rough=0.85),
        'wall_cap': principled('Wall cut', srgb('#2b2f33'), rough=0.9),
        'walnut': principled('Walnut', srgb('#5a3a26'), rough=0.32, coat=0.4),
        'walnut_light': principled('Walnut light', srgb('#7a5236'), rough=0.35, coat=0.3),
        'oak': principled('Oak', srgb('#c9ad84'), rough=0.45),
        'brass': principled('Brass', srgb('#c9a35a'), rough=0.25, metal=1.0),
        'chrome': principled('Chrome', (0.8, 0.8, 0.82), rough=0.08, metal=1.0),
        'ivory': principled('Upholstery ivory', srgb('#efe7d8'), rough=0.85, sheen=0.5),
        'navy': principled('Upholstery navy', srgb('#1d2c4a'), rough=0.8, sheen=0.5),
        'cognac': principled('Leather cognac', srgb('#9a5a2c'), rough=0.42, coat=0.15),
        'linen': principled('Linen white', srgb('#f6f3ec'), rough=0.9, sheen=0.4),
        'throw': principled('Throw sand', srgb('#c8b89a'), rough=0.9, sheen=0.4),
        'stone_top': principled('Stone top', srgb('#e9e4dc'), rough=0.18, coat=0.3),
        'black_glass': principled('Screen off', (0.01, 0.012, 0.015), rough=0.05, coat=1.0),
        'screen': principled('Screen chart', srgb('#0d2a3e'), rough=0.1, emission=srgb('#4fa3c7'), estrength=1.2),
        'screen_warm': principled('Screen radar', srgb('#06140d'), rough=0.1, emission=srgb('#3ccf74'), estrength=0.8),
        'glass': principled('Glass', (0.85, 0.9, 0.92), rough=0.0, transmission=1.0, ior=1.5),
        'tinted_glass': principled('Tinted glass', srgb('#0b1218'), rough=0.06, coat=0.3, spec=0.35),
        'steel': principled('Steel grey', srgb('#8c969c'), rough=0.45, metal=0.6),
        'steel_white': principled('Steel white', srgb('#e6e8e8'), rough=0.5),
        'tank_paint': principled('Tank paint', srgb('#b4bdb6'), rough=0.6),
        'red': principled('Safety red', srgb('#b3261e'), rough=0.4),
        'water': principled('Pool water', srgb('#3aa7c9'), rough=0.02, transmission=0.85, ior=1.33),
        'pool_tile': principled('Pool tile', srgb('#9fd6e2'), rough=0.2),
        'plant': principled('Plant', srgb('#3f6b3a'), rough=0.7),
        'pot': principled('Pot', srgb('#d8d2c4'), rough=0.6),
        'books': principled('Books', srgb('#3b4a5f'), rough=0.7),
        'ceramic': principled('Ceramic', (0.95, 0.95, 0.94), rough=0.15, coat=0.5),
        'rug': principled('Rug', srgb('#cfc2a8'), rough=0.98, sheen=0.7),
        'hull': principled('Hull navy', srgb('#14273a'), rough=0.25, coat=0.5),
        'boot': principled('Boot top', srgb('#e9ecee'), rough=0.3, coat=0.8),
        'antifoul': principled('Antifoul', srgb('#5a1f1f'), rough=0.7),
        'super': principled('Superstructure', srgb('#f2f3f1'), rough=0.3, coat=0.8),
        'carbon': principled('Carbon', srgb('#1b1d1f'), rough=0.3, coat=0.6),
        'sail': principled('Sail', srgb('#efe9dc'), rough=0.7, sheen=0.3),
        'rope': principled('Rigging', srgb('#2a2a2a'), rough=0.4, metal=0.5),
        'teak_plain': principled('Teak plain', srgb('#a8784a'), rough=0.6),
        'quay': principled('Quay stone', srgb('#cbbfa8'), rough=0.85),
        'white_render': principled('Cycladic white', srgb('#f4f2ec'), rough=0.9),
        'blue_door': principled('Aegean blue', srgb('#1e5aa8'), rough=0.6),
        'rock': principled('Rock', srgb('#8a7a64'), rough=0.95),
        'scrub': principled('Scrub', srgb('#6f7a4a'), rough=0.95),
        'rubber': principled('Rubber', (0.03, 0.03, 0.03), rough=0.7),
        'tender': principled('Tender hull', srgb('#f1f1ef'), rough=0.25, coat=0.8),
        'fender': principled('Fender', srgb('#1d2c4a'), rough=0.5),
    }


# ---- Primitives -------------------------------------------------------------

_COLL: bpy.types.Collection | None = None


def collection(name):
    global _COLL
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    _COLL = c
    return c


def _link(obj):
    (_COLL or bpy.context.scene.collection).objects.link(obj)
    return obj


def mesh(name, verts, faces, mat=None, smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    if mat:
        o.data.materials.append(mat)
    return _link(o)


def box(name, x0, y0, z0, x1, y1, z1, mat, bevel=0.0, segments=2):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    o = mesh(name, v, f, mat)
    if bevel > 0:
        b = o.modifiers.new('Bevel', 'BEVEL')
        b.width = min(bevel, (x1 - x0) / 2.1, (y1 - y0) / 2.1, (z1 - z0) / 2.1)
        b.segments = segments
        b.limit_method = 'NONE'
        for p in o.data.polygons:
            p.use_smooth = True
        o.data.shade_smooth() if hasattr(o.data, 'shade_smooth') else None
    return o


def cbox(name, cx, cy, z0, w, d, h, mat, rot=0.0, bevel=0.0):
    """Box centred at (cx, cy), w along X before rotation, d along Y, from z0 up h."""
    o = box(name, -w / 2, -d / 2, 0, w / 2, d / 2, h, mat, bevel)
    o.location = (cx, cy, z0)
    o.rotation_euler = (0, 0, rot)
    return o


def cylinder(name, x, y, z0, r, h, mat, verts=32, r_top=None, axis='Z'):
    r_top = r if r_top is None else r_top
    v, f = [], []
    for i in range(verts):
        a = 2 * math.pi * i / verts
        v.append((r * math.cos(a), r * math.sin(a), 0))
    for i in range(verts):
        a = 2 * math.pi * i / verts
        v.append((r_top * math.cos(a), r_top * math.sin(a), h))
    for i in range(verts):
        j = (i + 1) % verts
        f.append((i, j, verts + j, verts + i))
    f.append(tuple(range(verts - 1, -1, -1)))
    f.append(tuple(range(verts, 2 * verts)))
    o = mesh(name, v, f, mat, smooth=True)
    o.location = (x, y, z0)
    return o


def rod(name, p0, p1, r, mat, verts=8):
    """Cylinder between two points (rigging, rails)."""
    from mathutils import Vector
    a, b = Vector(p0), Vector(p1)
    d = b - a
    o = cylinder(name, 0, 0, 0, r, d.length, mat, verts)
    o.location = a
    o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return o


def plane(name, x0, y0, x1, y1, z, mat):
    v = [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)]
    o = mesh(name, v, [(0, 1, 2, 3)], mat)
    uv = o.data.uv_layers.new(name='UVMap')
    for loop, (u, w) in zip(uv.data, [(0, 1), (1, 1), (1, 0), (0, 0)]):
        loop.uv = (u, w)
    return o


def extrude_polygon(name, pts, z0, z1, mat, cap_top=True, cap_bottom=True):
    n = len(pts)
    v = [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    f = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    if cap_bottom:
        f.append(tuple(range(n - 1, -1, -1)))
    if cap_top:
        f.append(tuple(range(n, 2 * n)))
    return mesh(name, v, f, mat)


# ---- DXF reader --------------------------------------------------------------------

@dataclass
class CadRoom:
    name: str
    status: str
    finish: str
    furniture: str
    num: int
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def w(self):
        return self.x1 - self.x0

    @property
    def d(self):
        return self.y1 - self.y0

    @property
    def cx(self):
        return (self.x0 + self.x1) / 2

    @property
    def cy(self):
        return (self.y0 + self.y1) / 2


@dataclass
class CadDeck:
    name: str
    index: int
    z: float
    top: float
    outline: list
    rooms: list
    walls: list  # ((x0, y0), (x1, y1))
    roof: list


def read_deck(deck: p68.Deck) -> CadDeck:
    path = CAD_DIR / f'P68-ENG-{deck.index:02d}-{p68.slug(deck.name)}.dxf'
    doc = ezdxf.readfile(path)
    msp = doc.modelspace()
    rooms = []
    for e in msp.query('LWPOLYLINE[layer=="A-AREA"]'):
        xd = [v for _, v in e.get_xdata('P68')]
        pts = [(p[0], p[1]) for p in e.get_points()]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        rooms.append(CadRoom(xd[0], xd[1], xd[2], xd[3] or None, int(xd[4]), min(xs), min(ys), max(xs), max(ys)))
    outline = None
    for e in msp.query('LWPOLYLINE[layer=="A-FLOR-OTLN"]'):
        outline = [(p[0], p[1]) for p in e.get_points()]
    walls = [((e.dxf.start.x, e.dxf.start.y), (e.dxf.end.x, e.dxf.end.y)) for e in msp.query('LINE[layer=="A-WALL"]')]
    roof = []
    for e in msp.query('LWPOLYLINE[layer=="A-ROOF-OTLN"]'):
        pts = [(p[0], p[1]) for p in e.get_points()]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        roof.append((min(xs), min(ys), max(xs), max(ys)))
    return CadDeck(deck.name, deck.index, deck.z, deck.top, outline, rooms, walls, roof)


def build_walls(cd: CadDeck, z0, height, mat, cap=None, t=0.12):
    """Extrude the DXF wall lines into walls t thick. Optional dark cap on top (plan poché)."""
    for i, ((x0, y0), (x1, y1)) in enumerate(cd.walls):
        if abs(x1 - x0) < 1e-6:
            box(f'Wall{i}', x0 - t / 2, min(y0, y1) - t / 2, z0, x0 + t / 2, max(y0, y1) + t / 2, z0 + height, mat)
            if cap:
                box(f'WallCap{i}', x0 - t / 2, min(y0, y1) - t / 2, z0 + height, x0 + t / 2, max(y0, y1) + t / 2, z0 + height + 0.01, cap)
        else:
            box(f'Wall{i}', min(x0, x1) - t / 2, y0 - t / 2, z0, max(x0, x1) + t / 2, y0 + t / 2, z0 + height, mat)
            if cap:
                box(f'WallCap{i}', min(x0, x1) - t / 2, y0 - t / 2, z0 + height, max(x0, x1) + t / 2, y0 + t / 2, z0 + height + 0.01, cap)


def build_floors(cd: CadDeck, z):
    for r in cd.rooms:
        plane(f'Floor {r.num} {r.name}', r.x0, r.y0, r.x1, r.y1, z, floor_material(r.finish, r.w, r.d))
