#!/usr/bin/env python3
"""
sync_state.py — fill city-ui/state.js with what the city has actually shipped.

It scans the repo for launch-kit folders (a folder holding a .zip and/or a
listing file) and writes the results into the marked block of city-ui/state.js
plus a machine-readable city-ui/state.json.

Run from anywhere:      python3 city-ui/scripts/sync_state.py
Preview only:           python3 city-ui/scripts/sync_state.py --dry-run
Override by hand:       python3 city-ui/scripts/sync_state.py --shipped 6 --product "X" \
                                                      --revenue 144 --store-url https://you.gumroad.com

It never fails the workflow: if it can find nothing it warns and leaves your
numbers alone (exit 0). Pass --strict to make that an error instead.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

START = "/* @@CITY_AUTO_START@@"
END = "/* @@CITY_AUTO_END@@ */"

# Folders that commonly hold a week's output, checked one level deep.
HINTS = [
    "products", "product", "launch_kits", "launch-kits", "launchkits",
    "kits", "kit", "builds", "releases", "output", "outputs", "dist", "runs",
]
SKIP_DIRS = {".git", ".github", "node_modules", "city-ui", "__pycache__", ".venv"}
LISTING_NAMES = {"listing.md", "listing.txt", "listing.json", "product.md", "description.md"}


def log(msg: str) -> None:
    print(f"[sync-state] {msg}")


def repo_root() -> Path:
    # <repo>/city-ui/scripts/sync_state.py -> <repo>
    return Path(__file__).resolve().parents[2]


def looks_like_kit(d: Path) -> bool:
    """A launch kit holds its zip and/or listing file directly (not in a subfolder),
    so a container like products/ that only holds subfolders is not itself a kit."""
    if not d.is_dir():
        return False
    try:
        for f in d.iterdir():
            if f.is_file() and (f.suffix.lower() == ".zip" or f.name.lower() in LISTING_NAMES):
                return True
    except OSError:
        return False
    return False


def kit_name(d: Path) -> str:
    for name in ("listing.md", "listing.txt", "product.md", "description.md"):
        f = d / name
        if f.is_file():
            try:
                for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                    line = line.strip().lstrip("#").strip()
                    if line:
                        return line[:70]
            except OSError:
                pass
    j = d / "listing.json"
    if j.is_file():
        try:
            data = json.loads(j.read_text(encoding="utf-8"))
            for key in ("title", "name", "product"):
                if isinstance(data.get(key), str) and data[key].strip():
                    return data[key].strip()[:70]
        except (OSError, ValueError):
            pass
    return d.name.replace("_", " ").replace("-", " ").strip().title()


def kit_mtime(d: Path) -> float:
    newest = d.stat().st_mtime
    for f in d.rglob("*"):
        if f.is_file():
            try:
                newest = max(newest, f.stat().st_mtime)
            except OSError:
                pass
    return newest


def discover(root: Path) -> list[dict]:
    seen: set[Path] = set()
    kits: list[dict] = []

    containers = [root] + [root / h for h in HINTS]
    for container in containers:
        if not container.is_dir():
            continue
        try:
            children = sorted(container.iterdir())
        except OSError:
            continue
        for child in children:
            if not child.is_dir() or child.name in SKIP_DIRS or child.name.startswith("."):
                continue
            if child.resolve() in seen:
                continue
            if looks_like_kit(child):
                seen.add(child.resolve())
                ts = kit_mtime(child)
                kits.append({
                    "name": kit_name(child),
                    "path": str(child.relative_to(root)).replace("\\", "/"),
                    "at": datetime.fromtimestamp(ts, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
                    "_ts": ts,
                })
    kits.sort(key=lambda k: k["_ts"], reverse=True)
    return kits


def read_previous_json(out_dir: Path) -> dict:
    p = out_dir / "state.json"
    if not p.is_file():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def render_auto_block(source: str, stats: dict, last_run: dict) -> tuple[str, dict]:
    payload = {
        "source": source,
        "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "stats": stats,
        "lastRun": last_run,
    }
    ind = lambda obj: json.dumps(obj, indent=2).replace("\n", "\n  ")
    lines = [
        f"  source: {json.dumps(payload['source'])},",
        f"  generatedAt: {json.dumps(payload['generatedAt'])},",
        f"  stats: {ind(stats)},",
        f"  lastRun: {ind(last_run)}",
    ]
    return f"{START} */\n" + "\n".join(lines) + f"\n  {END}", payload


def splice(state_js: Path, block: str) -> None:
    if state_js.is_file():
        text = state_js.read_text(encoding="utf-8")
        if START in text and END in text:
            head = text.split(START)[0]
            tail = text.split(END, 1)[1]
            state_js.write_text(head + block + tail, encoding="utf-8")
            return
        log("state.js has no @@CITY_AUTO markers — rewriting it from scratch.")
    state_js.write_text(
        "/* Generated by scripts/sync_state.py */\n"
        "window.CITY_STATE = {\n  schema: 1,\n  store: { label: \"Buy on Gumroad\", url: \"\" },\n  agents: {},\n  "
        + block + "\n};\n",
        encoding="utf-8",
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Write city-ui/state.js from what the city has shipped.")
    ap.add_argument("--repo", type=Path, default=None, help="repo root (default: two levels above this script)")
    ap.add_argument("--out", type=Path, default=None, help="city-ui folder (default: <repo>/city-ui)")
    ap.add_argument("--shipped", type=int, default=None, help="override the shipped count")
    ap.add_argument("--revenue", type=float, default=None, help="override dollars collected")
    ap.add_argument("--price", type=float, default=None, help="override your list price")
    ap.add_argument("--product", default=None, help="override the newest product name")
    ap.add_argument("--store-url", default=None, help="store URL written into state.js")
    ap.add_argument("--source", default="workflow", choices=["workflow", "manual"], help="value for 'source'")
    ap.add_argument("--dry-run", action="store_true", help="print what it found, write nothing")
    ap.add_argument("--strict", action="store_true", help="exit 1 when nothing is found")
    args = ap.parse_args()

    root = (args.repo or repo_root()).resolve()
    out_dir = (args.out or (root / "city-ui")).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    kits = discover(root)
    prev = read_previous_json(out_dir)
    prev_stats = prev.get("stats") or {}
    prev_run = prev.get("lastRun") or {}

    if not kits:
        log(f"no launch-kit folders found under {root} (looked in: {', '.join(HINTS)})")
        if args.shipped is None:
            log("leaving existing numbers untouched.")
            if args.strict:
                return 1
            return 0

    newest = kits[0] if kits else None
    shipped = args.shipped if args.shipped is not None else len(kits)

    price = args.price
    if price is None:
        price = prev_stats.get("avgPrice", 24)

    revenue = args.revenue
    if revenue is None:
        revenue = prev_stats.get("revenue", 0)

    product = args.product or (newest["name"] if newest else prev_run.get("product"))
    at = newest["at"] if newest else prev_run.get("at")
    kit = newest["path"] if newest else prev_run.get("kit")

    stats = {"shipped": int(shipped), "revenue": round(float(revenue), 2), "avgPrice": round(float(price), 2)}
    last_run = {"at": at, "product": product, "kit": kit, "run": prev_run.get("run")}

    log(f"repo root       : {root}")
    log(f"launch kits found: {len(kits)}")
    for k in kits[:6]:
        log(f"   - {k['path']}  ({k['name']})")
    log(f"shipped={stats['shipped']}  revenue={stats['revenue']}  avgPrice={stats['avgPrice']}")
    log(f"lastRun: {last_run['product']} @ {last_run['at']}")

    if args.dry_run:
        log("dry run — nothing written.")
        return 0

    block, payload = render_auto_block(args.source, stats, last_run)
    splice(out_dir / "state.js", block)
    (out_dir / "state.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    if args.store_url:
        js = (out_dir / "state.js").read_text(encoding="utf-8")
        if 'url: ""' in js:
            js = js.replace('url: ""', f'url: {json.dumps(args.store_url)}', 1)
            (out_dir / "state.js").write_text(js, encoding="utf-8")
            log(f"store url set to {args.store_url}")

    log("wrote city-ui/state.js + city-ui/state.json")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # never take the Monday build down over the UI
        print(f"[sync-state] unexpected error: {exc!r}", file=sys.stderr)
        sys.exit(0)
