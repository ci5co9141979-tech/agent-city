"""Real Estate Video LUT Pack: generates 10 real 33-point .cube LUTs with numpy,
plus a before/after preview strip and an install guide."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SIZE = 33

# name: (description, params)
LOOKS = {
    "01_Bright_Airy": ("Lifted, clean, high-key interiors. Best for light rooms.",
                       dict(exp=0.18, contrast=0.92, sat=0.95, temp=0.00, tint=0.0, lift=0.04, roll=0.35)),
    "02_Warm_Home": ("Inviting warm whites and honey wood tones for family homes.",
                     dict(exp=0.08, contrast=1.04, sat=1.06, temp=0.07, tint=0.01, lift=0.02, roll=0.30, wood=0.12)),
    "03_Crisp_Neutral": ("True-to-life neutral. Fixes dull camera profiles without a look.",
                         dict(exp=0.05, contrast=1.08, sat=1.02, temp=0.0, tint=0.0, lift=0.0, roll=0.25)),
    "04_Luxury_Contrast": ("Deeper blacks and rich contrast for high-end listings.",
                           dict(exp=-0.02, contrast=1.22, sat=1.04, temp=0.02, tint=0.0, lift=-0.01, roll=0.45, wood=0.08)),
    "05_Modern_Cool": ("Clean cool whites for contemporary, minimal, glass-heavy spaces.",
                       dict(exp=0.07, contrast=1.10, sat=0.98, temp=-0.06, tint=-0.01, lift=0.01, roll=0.30)),
    "06_Golden_Hour_Exterior": ("Warm sunset exteriors without burning the sky.",
                                dict(exp=0.02, contrast=1.12, sat=1.10, temp=0.10, tint=0.015, lift=0.0, roll=0.50, sky=0.08)),
    "07_Blue_Sky_Pop": ("Punchy exterior daylight: richer blue sky, green lawns, safe whites.",
                        dict(exp=0.0, contrast=1.14, sat=1.12, temp=-0.01, tint=0.0, lift=0.0, roll=0.50, sky=0.18, green=0.10)),
    "08_Drone_Clear": ("Cuts aerial haze and boosts clarity for drone footage.",
                       dict(exp=-0.03, contrast=1.12, sat=1.08, temp=-0.02, tint=0.0, lift=-0.01, roll=0.5, sky=0.12, green=0.08, dehaze=0.12)),
    "09_Soft_Film": ("Gentle filmic roll-off and muted saturation for lifestyle walkthroughs.",
                     dict(exp=0.03, contrast=0.98, sat=0.90, temp=0.03, tint=0.0, lift=0.06, roll=0.55)),
    "10_Log_To_Rec709_Base": ("Neutral starting point for flat/log footage (S-curve + saturation restore).",
                              dict(exp=0.12, contrast=1.30, sat=1.25, temp=0.0, tint=0.0, lift=0.0, roll=0.40)),
}


def luma(rgb):
    return rgb @ np.array([0.2126, 0.7152, 0.0722])


def hue_sat(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    m = d > 1e-6
    h = np.where(m & (mx == r), ((g - b) / np.where(m, d, 1)) % 6, h)
    h = np.where(m & (mx == g), (b - r) / np.where(m, d, 1) + 2, h)
    h = np.where(m & (mx == b), (r - g) / np.where(m, d, 1) + 4, h)
    return h * 60.0, d / np.where(mx > 1e-6, mx, 1)


def band(h, center, width):
    d = np.abs((h - center + 180) % 360 - 180)
    return np.clip(1 - d / width, 0, 1)


def grade(rgb, exp=0, contrast=1, sat=1, temp=0, tint=0, lift=0, roll=0.3, wood=0, sky=0, green=0, dehaze=0, fade=0, split=None):
    x = np.clip(rgb, 0, 1)
    x = x + exp * (1 - x) * 0.6 if exp >= 0 else x * (1 + exp)  # exposure that protects highlights
    x = x + lift * (1 - x) ** 2  # shadow lift
    x = np.clip(x, 0, 1)
    x = x * np.array([1 + temp * 0.4, 1.0, 1 - temp * 0.4])  # white balance (warm/cool)
    x[..., 1] *= 1 - tint  # tint (+ = magenta)
    x = np.clip(x, 0, 1)
    # S-curve contrast around mid grey
    mid = 0.5
    x = mid + (x - mid) * contrast
    # smooth S-shaping on top for contrast > 1
    if contrast > 1:
        s = x * x * (3 - 2 * np.clip(x, 0, 1))
        x = x * (1 - (contrast - 1) * 0.6) + s * (contrast - 1) * 0.6
    x = np.clip(x, 0, 1)
    # highlight roll-off: compress >0.8 so whites never clip harshly
    t = 0.8
    over = np.clip(x - t, 0, None)
    x = np.where(x > t, t + (1 - t) * (1 - np.exp(-over / (1 - t) * (1 + roll))) / (1 - np.exp(-(1 + roll))), x)
    if split:  # split toning: tint shadows and highlights
        yy = luma(x)[..., None]
        x = np.clip(x + (1 - yy) ** 2 * np.array(split[0]) + yy ** 2 * np.array(split[1]), 0, 1)
    if fade:  # lifted blacks
        x = fade + x * (1 - fade)
    # saturation (luma-preserving) + hue-targeted tweaks
    y = luma(x)[..., None]
    h, s = hue_sat(x)
    sat_map = np.full_like(h, sat) + wood * band(h, 30, 28) + sky * band(h, 215, 35) + green * band(h, 110, 40)
    sat_map = sat_map + dehaze * 0.5
    x = np.clip(y + (x - y) * sat_map[..., None], 0, 1)
    if dehaze:
        x = np.clip(0.5 + (x - 0.5) * (1 + dehaze) - dehaze * 0.04, 0, 1)
    return np.clip(x, 0, 1)


def lut_grid(params):
    n = SIZE
    ax = np.linspace(0, 1, n)
    # .cube order: red fastest, then green, then blue
    b, g, r = np.meshgrid(ax, ax, ax, indexing="ij")
    rgb = np.stack([r, g, b], -1).reshape(-1, 3)
    return grade(rgb, **params)


def write_cube(path, title, data):
    with open(path, "w") as f:
        f.write(f'TITLE "{title}"\n# Generated for the Real Estate Video LUT Pack\nLUT_3D_SIZE {SIZE}\n')
        f.write("DOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n")
        for r, g, b in data:
            f.write(f"{r:.6f} {g:.6f} {b:.6f}\n")


def apply_lut(img, data):
    """Trilinear apply of a LUT (data shaped [b][g][r]) to a float image."""
    n = SIZE
    cube = data.reshape(n, n, n, 3)
    p = np.clip(img, 0, 1) * (n - 1)
    i0 = np.floor(p).astype(int).clip(0, n - 2)
    f = p - i0
    r0, g0, b0 = i0[..., 0], i0[..., 1], i0[..., 2]
    fr, fg, fb = f[..., 0:1], f[..., 1:2], f[..., 2:3]
    out = 0
    for dr in (0, 1):
        for dg in (0, 1):
            for db in (0, 1):
                w = (fr if dr else 1 - fr) * (fg if dg else 1 - fg) * (fb if db else 1 - fb)
                out = out + w * cube[b0 + db, g0 + dg, r0 + dr]
    return out


def test_scene(w=360, h=220):
    """A synthetic 'listing' frame: sky, lawn, white wall, wood floor, skin patch, gray ramp."""
    img = np.zeros((h, w, 3))
    img[: h // 2] = np.array([0.45, 0.62, 0.85])           # sky
    img[: h // 2, :, :] *= np.linspace(1.15, 0.9, h // 2)[:, None, None]
    img[h // 2 : int(h * 0.62)] = np.array([0.30, 0.52, 0.22])  # lawn
    img[int(h * 0.62) : int(h * 0.82), : w // 2] = np.array([0.88, 0.86, 0.82])  # white wall
    img[int(h * 0.62) : int(h * 0.82), w // 2 :] = np.array([0.72, 0.52, 0.32])  # wood
    ramp = np.linspace(0.02, 0.98, w)
    img[int(h * 0.82) :] = ramp[None, :, None]
    return np.clip(img, 0, 1)


def build(outdir, cfg, brief):
    outdir = Path(outdir)
    niche = cfg.get("niche")
    if niche:
        from .lut_niches import NICHES
        looks, pack_name, pre = NICHES[niche]["looks"], cfg["name"], NICHES[niche]["short"][:3].upper()
    else:
        looks, pack_name, pre = LOOKS, "Real Estate Video LUT Pack", "RE"
    lutdir = outdir / "LUTs"
    lutdir.mkdir()
    scene = test_scene()
    tiles = [("Original", scene)]
    for name, (desc, params) in looks.items():
        data = lut_grid(params)
        write_cube(lutdir / f"{pre}_{name}.cube", name.replace("_", " "), data)
        tiles.append((name[3:].replace("_", " "), apply_lut(scene, data)))
    # preview strip: 4 columns
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    th, tw = scene.shape[:2]
    sheet = Image.new("RGB", (cols * tw, rows * (th + 22)), (24, 24, 24))
    d = ImageDraw.Draw(sheet)
    for i, (label, arr) in enumerate(tiles):
        x, y = (i % cols) * tw, (i // cols) * (th + 22)
        sheet.paste(Image.fromarray((arr * 255).astype("uint8")), (x, y + 22))
        d.text((x + 6, y + 5), label, fill=(235, 235, 235))
    sheet.save(outdir / "preview_strip.png")
    lines = "\n".join(f"  {pre}_{n}.cube - {d}" for n, (d, _) in looks.items())
    (outdir / "INSTALL_GUIDE.txt").write_text(
        f"""{pack_name.upper()} - INSTALL GUIDE
==========================================

WHAT'S INSIDE
{lines}

All LUTs are standard 33-point .cube files designed for Rec.709 footage.
preview_strip.png shows each look on a synthetic test scene (sky, lawn,
white wall, wood floor, gray ramp). Your own footage will differ.

DAVINCI RESOLVE
  1. Copy the LUTs folder into:
     Mac:     /Library/Application Support/Blackmagic Design/DaVinci Resolve/LUT/
     Windows: C:\\ProgramData\\Blackmagic Design\\DaVinci Resolve\\Support\\LUT\\
  2. Resolve > Preferences > Color Management > Update Lists
  3. Color page > right-click a node > LUT > pick a look from this pack

PREMIERE PRO
  Lumetri Color > Creative > Look > Browse... and pick a .cube file.

FINAL CUT PRO
  Use the Custom LUT effect (Inspector > Choose Custom LUT) or a free LUT utility.

TIPS
  * Expose correctly first. A LUT is a finishing step, not a rescue tool.
  * Set white balance on a white wall BEFORE applying a look.
  * Drop the LUT intensity (Resolve: node Key gain; Premiere: Intensity slider) to 60-80% if it feels strong.
  * These LUTs assume Rec.709 footage. For log footage, convert to Rec.709 first (or use your camera's official conversion LUT), then add a look.
  * Check the sky and whites on a scope; every look rolls highlights off gently but your footage may already be clipped.

LICENSE
  Personal and commercial use in your own video projects. No resale or redistribution of the LUT files.
"""
    )
    return sorted(p for p in outdir.rglob("*") if p.is_file())


def validate(outdir):
    outdir, problems = Path(outdir), []
    cubes = sorted((outdir / "LUTs").glob("*.cube"))
    if len(cubes) not in (8, 10):
        problems.append(f"expected 8 or 10 LUTs, found {len(cubes)}")
    for c in cubes:
        lines = c.read_text().splitlines()
        data = [l for l in lines if l and l[0] in "0123456789."]
        if f"LUT_3D_SIZE {SIZE}" not in lines:
            problems.append(f"{c.name}: missing size header")
        if len(data) != SIZE ** 3:
            problems.append(f"{c.name}: {len(data)} rows, expected {SIZE ** 3}")
            continue
        vals = np.array([[float(v) for v in l.split()] for l in data])
        if vals.min() < 0 or vals.max() > 1:
            problems.append(f"{c.name}: values out of 0-1 range")
        # monotonic gray axis: neutral ramp must not invert
        g = vals.reshape(SIZE, SIZE, SIZE, 3)[np.arange(SIZE), np.arange(SIZE), np.arange(SIZE)]
        if np.any(np.diff(luma(g)) < -1e-4):
            problems.append(f"{c.name}: gray ramp not monotonic")
    for f in ("preview_strip.png", "INSTALL_GUIDE.txt"):
        if not (outdir / f).exists():
            problems.append(f"missing {f}")
    return problems
