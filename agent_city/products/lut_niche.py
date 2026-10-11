"""Generic niche LUT pack builder (spec-driven). Reuses the grading engine from luts.py."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from . import luts
from .luts import SIZE, apply_lut, lut_grid, luma, write_cube


def scene():
    """Test frame: sky, lawn, wall, wood, three skin tones, food colors, gray ramp."""
    w, h = 360, 240
    img = np.zeros((h, w, 3))
    img[:70] = np.array([0.45, 0.62, 0.85]) * np.linspace(1.15, 0.9, 70)[:, None, None]
    img[70:95] = np.array([0.30, 0.52, 0.22])
    img[95:140, :120] = np.array([0.88, 0.86, 0.82])
    img[95:140, 120:240] = np.array([0.72, 0.52, 0.32])
    img[95:140, 240:] = np.array([0.55, 0.57, 0.60])
    skin = [(0.87, 0.68, 0.55), (0.65, 0.45, 0.35), (0.45, 0.30, 0.22)]
    food = [(0.75, 0.15, 0.10), (0.92, 0.75, 0.25), (0.35, 0.55, 0.20)]
    for i, c in enumerate(skin + food):
        img[140:190, i * 60:(i + 1) * 60] = c
    img[190:] = np.linspace(0.02, 0.98, w)[None, :, None]
    return np.clip(img, 0, 1)


def build(outdir, cfg, brief):
    spec = cfg["spec"]
    outdir = Path(outdir)
    lutdir = outdir / "LUTs"
    lutdir.mkdir()
    prefix = spec.get("prefix", "LUT")
    sc = scene()
    tiles = [("Original", sc)]
    lines = []
    for i, look in enumerate(spec["looks"], 1):
        data = lut_grid(look["params"])
        fname = f"{prefix}_{i:02d}_{look['name'].replace(' ', '_')}.cube"
        write_cube(lutdir / fname, look["name"], data)
        tiles.append((look["name"], apply_lut(sc, data)))
        lines.append(f"  {fname} - {look['desc']}")
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    th, tw = sc.shape[:2]
    sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, (label, arr) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        sheet.paste(Image.fromarray((arr * 255).astype("uint8")), (x, y + 22))
        d.text((x + 6, y + 5), label, fill=(235, 235, 235))
    sheet.save(outdir / "preview_strip.png")
    (outdir / "INSTALL_GUIDE.txt").write_text(
        f"""{spec['pack_name'].upper()} - INSTALL GUIDE
{'=' * 50}

WHAT'S INSIDE
{chr(10).join(lines)}

{spec.get('intro', '')}

All LUTs are standard 33-point .cube files for Rec.709 footage.
preview_strip.png shows each look on a synthetic test frame (sky, lawn, white wall,
wood, gray, three skin tones, three food colors, gray ramp). Your footage will differ.

DAVINCI RESOLVE
  1. Copy the LUTs folder to:
     Mac:     /Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/
     Windows: C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\LUT\\
  2. Resolve > Preferences > Color Management > Update Lists
  3. Color page > right-click a node > LUT > pick a look
PREMIERE PRO: Lumetri Color > Creative > Look > Browse... > choose a .cube
FINAL CUT PRO: Inspector > Custom LUT effect > Choose Custom LUT

TIPS
  * Expose and white-balance first. A LUT is a finishing step, not a rescue tool.
  * Lower the LUT intensity to 60-80% if a look feels strong.
  * Check skin tones and highlights on a scope; adjust per shot.
  * Footage already clipped or very flat/log needs a conversion LUT before these looks.

LICENSE
  {spec.get('license', 'Personal and commercial use in your own video projects. No resale or redistribution of the LUT files.')}
"""
    )
    return sorted(p for p in outdir.rglob("*") if p.is_file())


def validate(outdir, cfg=None):
    expected = len(cfg["spec"]["looks"]) if cfg else None
    outdir, problems = Path(outdir), []
    cubes = sorted((outdir / "LUTs").glob("*.cube"))
    if not cubes or (expected and len(cubes) != expected):
        problems.append(f"expected {expected} LUTs, found {len(cubes)}")
    for c in cubes:
        lines = c.read_text().splitlines()
        data = [l for l in lines if l and l[0] in "0123456789."]
        if f"LUT_3D_SIZE {SIZE}" not in lines or len(data) != SIZE ** 3:
            problems.append(f"{c.name}: malformed ({len(data)} rows)")
            continue
        vals = np.array([[float(v) for v in l.split()] for l in data])
        if vals.min() < 0 or vals.max() > 1 or np.isnan(vals).any():
            problems.append(f"{c.name}: values out of range")
        g = vals.reshape(SIZE, SIZE, SIZE, 3)[np.arange(SIZE), np.arange(SIZE), np.arange(SIZE)]
        if np.any(np.diff(luma(g)) < -1e-4):
            problems.append(f"{c.name}: gray ramp not monotonic")
        # a look should not be a no-op or a wrecked image
        ident = np.linspace(0, 1, SIZE)
        if np.abs(g - ident[:, None]).max() < 0.005 and "Neutral" not in c.name:
            problems.append(f"{c.name}: indistinguishable from identity")
    for f in ("preview_strip.png", "INSTALL_GUIDE.txt"):
        if not (outdir / f).exists():
            problems.append(f"missing {f}")
    return problems
