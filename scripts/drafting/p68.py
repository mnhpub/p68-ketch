"""Shared data and helpers for the P68 drafting scripts.

Reads the layout, deck list, accessibility criteria, finish schedule and deck status
from the repository, and provides room status, door placement and indicative cabin
partitions. Everything here is schematic: positions come from layout/decks-layout.json,
which was read from the General Arrangement schematic and is not dimensioned.
"""
from __future__ import annotations

import json
import math
import re
import subprocess
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'drawings'
PUBLIC = ROOT / 'public' / 'drawings'


def load(rel: str):
    return json.loads((ROOT / rel).read_text())


LAYOUT = load('layout/decks-layout.json')
DECKS = load('decks.json')
ACCESS = load('layout/accessibility.json')
FINISHES = load('layout/finishes.json')
STATUS = load('layout/deck-status.json')
SYSTEMS = load('systems.json')

LOA = float(LAYOUT['loa'])
BEAM = float(LAYOUT['beam'])
ISSUE_DATE = date(2026, 10, 10).strftime('%d %b %Y')

# Deck floor heights (m above DWL), from the vertical space schedule (P68-KETCH-E).
FLOORS = {
    'Bridge': (9.3, 11.7),
    'Commander / Lido': (6.6, 9.3),
    'Main / Master': (3.35, 6.6),
    'Tween': (0.85, 3.35),
    'Tank / Technical': (-1.5, 0.85),
}
ROOF_Z = ACCESS['roof']['level_m']
COVER_Z = ACCESS['roof']['pilot_house_cover_top_m']

# Mast stations from layout/hull.json (via decks-layout.json): approximate, from the longitudinal section.
MASTS = {m['name']: float(m['x']) for m in LAYOUT['masts']}

ROUTE = re.compile(r'lobby|passage|corridor|circulation|access', re.I)
GUEST_LEVELS = set(ACCESS['public_levels'])


def slug(s: str) -> str:
    return re.sub(r'(^-|-$)', '', re.sub(r'[^a-z0-9]+', '-', s.lower()))


def half_beam(x: float) -> float:
    """Hull half-breadth at station x, from the sheet ellipse used for the deck outlines."""
    return (BEAM / 2) * math.sqrt(max(0.0, 1 - ((x - LOA / 2) / (LOA / 2)) ** 2))


@dataclass
class Room:
    name: str
    x0: float
    y0: float
    x1: float
    y1: float
    inferred: bool = False
    note: str = ''
    roof: bool = False
    num: int = 0
    finish: str = 'stone'
    furniture: str | None = None

    @property
    def w(self):  # along the length
        return self.x1 - self.x0

    @property
    def h(self):  # across the beam
        return self.y1 - self.y0

    @property
    def area(self):
        return self.w * self.h

    @property
    def cx(self):
        return (self.x0 + self.x1) / 2

    @property
    def cy(self):
        return (self.y0 + self.y1) / 2

    @property
    def is_route(self):
        return bool(ROUTE.search(self.name)) and 'Mag-rail' not in self.name

    @property
    def is_lift(self):
        return 'Mag-rail lift' in self.name

    @property
    def status(self) -> str:
        """Design status of the room: resolved decision, inferred, or read from the GA sheet."""
        n = self.note.lower()
        if 'resolved' in n or 'restored' in n:
            return 'resolved'
        if self.inferred:
            return 'inferred'
        return 'ga'


STATUS_LABEL = {
    'ga': 'Read from GA sheet',
    'resolved': 'Resolved decision',
    'inferred': 'Inferred, to check',
}


def finish_for(name: str):
    for rule in FINISHES['rules']:
        if rule['match'].lower() in name.lower():
            return rule['finish'], rule['furniture']
    return 'stone', None


@dataclass
class Deck:
    name: str
    index: int
    outline: list
    rooms: list
    roof: list = field(default_factory=list)

    @property
    def z(self):
        return FLOORS[self.name][0]

    @property
    def top(self):
        return FLOORS[self.name][1]

    @property
    def meta(self):
        return next(d for d in DECKS if d['name'] == self.name)

    @property
    def status(self):
        return STATUS['decks'][self.name]

    @property
    def outline_area(self):
        a = 0.0
        pts = self.outline
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            a += x1 * y2 - x2 * y1
        return abs(a) / 2

    @property
    def assigned(self):
        return sum(r.area for r in self.rooms)

    @property
    def extent(self):
        return min(r.x0 for r in self.rooms), max(r.x1 for r in self.rooms)

    @property
    def file_stem(self):
        return f'{self.index:02d}-{slug(self.name)}'


def decks() -> list[Deck]:
    out = []
    for i, d in enumerate(LAYOUT['decks'], start=1):
        rooms, roof = [], []
        for r in d['rooms']:
            x0, y0, x1, y1 = r['rect']
            room = Room(r['name'], x0, y0, x1, y1, r.get('inferred', False), r.get('note', ''), r.get('roof', False))
            room.finish, room.furniture = finish_for(room.name)
            (roof if room.roof else rooms).append(room)
        # Number rooms from the bow aft, then port to starboard, for the schedule.
        for n, room in enumerate(sorted(rooms, key=lambda r: (-r.cx, r.cy)), start=1):
            room.num = n
        out.append(Deck(d['name'], i, d['outline'], rooms, roof))
    return out


# ---- Adjacency and doors ---------------------------------------------------------

@dataclass
class Door:
    x: float
    y: float
    vertical: bool  # True when the wall runs across the beam (door in an x = const wall)
    width: float
    swing_into: str  # name of the room the leaf swings into
    sign: int  # +1 or -1: which side of the wall the leaf swings to
    kind: str = 'door'  # 'door', 'lift' or 'open'


def shared_edge(a: Room, b: Room, tol=0.15):
    """Return (vertical, fixed, lo, hi) for the wall a and b share, or None."""
    for xa, xb in ((a.x1, b.x0), (a.x0, b.x1)):
        if abs(xa - xb) < tol:
            lo, hi = max(a.y0, b.y0), min(a.y1, b.y1)
            if hi - lo > 0.5:
                return True, xa, lo, hi
    for ya, yb in ((a.y1, b.y0), (a.y0, b.y1)):
        if abs(ya - yb) < tol:
            lo, hi = max(a.x0, b.x0), min(a.x1, b.x1)
            if hi - lo > 0.5:
                return False, ya, lo, hi
    return None


# Door clear width for the plans: above the ADA clear minimum, with a frame allowance.
DOOR_W = 0.9


def doors(deck: Deck) -> list[Door]:
    """Indicative doors. Each room and lift gets one door, on its longest wall shared with a
    route; routes that meet are left open. Schematic: real door positions are not set."""
    out: list[Door] = []
    routes = [r for r in deck.rooms if r.is_route]

    def make(room, e, kind, width):
        vertical, fixed, lo, hi = e
        # Doors sit near the forward or starboard end of the shared wall, clear of the room tag.
        mid = hi - min(1.0, (hi - lo) / 2) if kind != 'open' else (lo + hi) / 2
        if vertical:
            return Door(fixed, mid, True, width, room.name, 1 if room.cx > fixed else -1, kind)
        return Door(mid, fixed, False, width, room.name, 1 if room.cy > fixed else -1, kind)

    for room in deck.rooms:
        if room.finish == 'tank' or room.is_route:
            continue
        best = None
        for route in routes:
            e = shared_edge(room, route)
            if e and (best is None or e[3] - e[2] > best[3] - best[2]):
                best = e
        if best:
            out.append(make(room, best, 'lift' if room.is_lift else 'door', 1.1 if room.is_lift else DOOR_W))
    for i, a in enumerate(routes):
        for b in routes[i + 1:]:
            e = shared_edge(a, b)
            if e:
                out.append(make(a, e, 'open', min(e[3] - e[2] - 0.3, 1.8)))
    return out


# ---- Indicative partitions for cabin blocks ------------------------------------

def partitions(room: Room) -> list[Room]:
    """Split a cabin block into indicative cabins with an ensuite each. The cabin count is
    not set in the brief, so this is a planning sketch, sized at roughly 4.5 m per guest
    cabin and 3 m per crew cabin along the length."""
    if room.furniture == 'cabins':
        pitch = 4.5
    elif room.furniture == 'crew':
        pitch = 3.0
    else:
        return [room]
    n = max(1, round(room.w / pitch))
    step = room.w / n
    return [Room(f'{room.name} {i + 1}', room.x0 + i * step, room.y0, room.x0 + (i + 1) * step, room.y1,
                 room.inferred, room.note, False, room.num, room.finish, room.furniture) for i in range(n)]


# ---- Validators and systems ----------------------------------------------------

def run_validator(script: str) -> tuple[bool, str]:
    try:
        res = subprocess.run(['node', f'scripts/{script}'], cwd=ROOT, capture_output=True, text=True, timeout=60)
        line = (res.stdout.strip().splitlines() or [res.stderr.strip()])[-1]
        return res.returncode == 0, line
    except Exception as exc:  # node missing in some environments
        return False, f'not run ({exc.__class__.__name__})'


def systems_for(deck_name: str):
    """Systems related to a deck. Only systems cleared for public release are named,
    because the drawings ship in both builds. Restricted systems are counted only."""
    rel = [s for s in SYSTEMS if deck_name in s.get('related_decks', [])]
    named = [s for s in rel if s.get('public_release')]
    return named, len(rel) - len(named)


def lift_stops(deck_name: str):
    return [l['name'].replace('Mag-rail ', '') for l in ACCESS['lifts'] if deck_name in l['stops']]
