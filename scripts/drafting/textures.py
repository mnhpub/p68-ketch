"""Procedural material textures for the finish-out plans and 3D renders.

Each function returns an RGB float array (H, W, 3) in 0..1 for a patch of floor
w_m by h_m metres at ppm pixels per metre. Textures are deterministic: the same
inputs give the same image, so rebuilds do not churn the repository.
"""
from __future__ import annotations

import hashlib

import numpy as np
from PIL import Image


def _rng(*key) -> np.random.Generator:
    seed = int(hashlib.sha1(repr(key).encode()).hexdigest()[:8], 16)
    return np.random.default_rng(seed)


def noise(h: int, w: int, cell: float, rng: np.random.Generator) -> np.ndarray:
    """Smooth value noise in 0..1 with features about `cell` pixels across."""
    gh, gw = max(2, int(h / cell) + 2), max(2, int(w / cell) + 2)
    g = (rng.random((gh, gw)) * 255).astype(np.uint8)
    img = Image.fromarray(g).resize((w, h), Image.BICUBIC)
    return np.asarray(img, dtype=np.float32) / 255.0


def fbm(h, w, cell, rng, octaves=4):
    out = np.zeros((h, w), np.float32)
    amp, total = 1.0, 0.0
    for _ in range(octaves):
        out += amp * noise(h, w, max(1.5, cell), rng)
        total += amp
        amp *= 0.5
        cell /= 2
    return out / total


def _hex(c: str) -> np.ndarray:
    c = c.lstrip('#')
    return np.array([int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def _mix(a, b, t):
    return a[None, None, :] * (1 - t[..., None]) + b[None, None, :] * t[..., None]


def _planks(w_m, h_m, ppm, plank_w, light, dark, seam, rng, seam_w=0.006, butt=(2.4, 4.2), grain=0.22):
    """Planks running along the length (x), stacked across the beam (y)."""
    W, H = max(2, int(w_m * ppm)), max(2, int(h_m * ppm))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    y_m = yy / ppm
    row = np.floor(y_m / plank_w).astype(int)
    nrows = row.max() + 1
    tone = rng.random(nrows)[row]
    # Butt joints: each row has its own offset and plank length.
    lengths = rng.uniform(*butt, nrows)
    offs = rng.uniform(0, butt[1], nrows)
    x_m = xx / ppm
    pos = (x_m + offs[row]) / lengths[row]
    piece = np.floor(pos).astype(int)
    tone = (tone + ((piece * 7919 + row * 104729) % 97) / 97.0 * 0.6) % 1.0
    # Grain: noise stretched along the plank.
    g = noise(H, max(2, W // 12), max(2.0, ppm * plank_w * 0.25), rng)
    g = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    t = np.clip(0.35 * tone + grain * g + 0.25, 0, 1)
    col = _mix(_hex(light), _hex(dark), t)
    seam_px = max(1.0, seam_w * ppm)
    in_seam = ((y_m % plank_w) * ppm < seam_px) | (((pos % 1.0) * lengths[row]) * ppm < seam_px * 0.8)
    col[in_seam] = _hex(seam)
    return col


def _tiles(w_m, h_m, ppm, tw, th, base, grout, var, rng, joint=0.003, speck=0.0, veins=False):
    W, H = max(2, int(w_m * ppm)), max(2, int(h_m * ppm))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x_m, y_m = xx / ppm, yy / ppm
    ix, iy = np.floor(x_m / tw).astype(int), np.floor(y_m / th).astype(int)
    tone = ((ix * 73856093 ^ iy * 19349663) % 1000) / 1000.0
    f = fbm(H, W, ppm * 0.6, rng)
    col = _hex(base)[None, None, :] * (1 - var * (tone[..., None] - 0.5) - 0.06 * (f[..., None] - 0.5))
    if veins:
        turb = fbm(H, W, ppm * 0.8, rng, 5)
        v = np.abs(np.sin((x_m * 0.9 + y_m * 0.4 + turb * 4.5) * 3.1))
        vein = np.clip(1 - v / 0.06, 0, 1) * 0.35 + np.clip(1 - v / 0.25, 0, 1) * 0.06
        col = col * (1 - vein[..., None]) + _hex('#8a8f96')[None, None, :] * vein[..., None]
    if speck:
        s = rng.random((H, W)) < speck
        col[s] *= 0.82
    jp = max(1.0, joint * ppm)
    j = ((x_m % tw) * ppm < jp) | ((y_m % th) * ppm < jp)
    col[j] = _hex(grout)
    return np.clip(col, 0, 1)


def material(kind: str, w_m: float, h_m: float, ppm: float) -> np.ndarray:
    rng = _rng(kind, round(w_m, 2), round(h_m, 2), ppm)
    if kind == 'teak':
        return _planks(w_m, h_m, ppm, 0.12, '#c08a55', '#8a5a33', '#2b211b', rng, seam_w=0.007)
    if kind == 'walnut':
        return _planks(w_m, h_m, ppm, 0.19, '#7a5136', '#4a2f1f', '#3a2618', rng, seam_w=0.0025, grain=0.3)
    if kind == 'oak':
        return _planks(w_m, h_m, ppm, 0.18, '#d9c09a', '#b8996c', '#9c8360', rng, seam_w=0.0025)
    if kind == 'stone':
        return _tiles(w_m, h_m, ppm, 0.9, 0.6, '#e4dacb', '#cdbfa9', 0.06, rng, speck=0.002)
    if kind == 'marble':
        return _tiles(w_m, h_m, ppm, 1.2, 1.2, '#f1eee9', '#d8d2c8', 0.03, rng, veins=True)
    if kind == 'tile':
        return _tiles(w_m, h_m, ppm, 0.6, 0.6, '#c9ccce', '#9fa4a8', 0.05, rng)
    if kind == 'carpet':
        W, H = max(2, int(w_m * ppm)), max(2, int(h_m * ppm))
        f = fbm(H, W, ppm * 0.4, rng) * 0.6 + rng.random((H, W)).astype(np.float32) * 0.4
        return np.clip(_mix(_hex('#efe6d6'), _hex('#d9ccb5'), f), 0, 1)
    if kind == 'epoxy':
        W, H = max(2, int(w_m * ppm)), max(2, int(h_m * ppm))
        col = np.ones((H, W, 3), np.float32) * _hex('#9ea7ad')
        col *= (0.95 + 0.08 * fbm(H, W, ppm, rng))[..., None]
        col[rng.random((H, W)) < 0.01] *= 0.75
        return np.clip(col, 0, 1)
    if kind == 'steel':
        W, H = max(2, int(w_m * ppm)), max(2, int(h_m * ppm))
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) / ppm
        p = 0.035
        u, v = (xx % p) / p - 0.5, (yy % p) / p - 0.5
        alt = (np.floor(xx / p) + np.floor(yy / p)) % 2
        d = np.where(alt > 0, np.abs(u + v), np.abs(u - v))
        lug = (d < 0.12) & (np.abs(u) < 0.38) & (np.abs(v) < 0.38)
        col = np.ones((H, W, 3), np.float32) * _hex('#8d969b')
        col *= (0.94 + 0.1 * fbm(H, W, ppm * 1.5, rng))[..., None]
        col[lug] *= 1.18
        return np.clip(col, 0, 1)
    if kind == 'tank':
        W, H = max(2, int(w_m * ppm)), max(2, int(h_m * ppm))
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32) / ppm
        col = np.ones((H, W, 3), np.float32) * _hex('#b9c2bb')
        hatch = ((xx + yy) % 0.6) * ppm < max(1.0, 0.02 * ppm)
        col[hatch] = _hex('#8f9a92')
        return col
    if kind == 'lift':
        W, H = max(2, int(w_m * ppm)), max(2, int(h_m * ppm))
        f = fbm(H, W, ppm * 0.3, rng)
        return np.clip(_mix(_hex('#c9a45c'), _hex('#a27f3a'), f), 0, 1)
    if kind == 'water':
        W, H = max(2, int(w_m * ppm)), max(2, int(h_m * ppm))
        f = fbm(H, W, ppm * 0.35, rng, 5)
        c = np.abs(np.sin(f * 18))
        col = _mix(_hex('#2f9fc4'), _hex('#8fe0f0'), np.clip(1 - c / 0.35, 0, 1) * 0.55 + f * 0.25)
        return np.clip(col, 0, 1)
    raise KeyError(kind)


def to_image(arr: np.ndarray) -> Image.Image:
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
