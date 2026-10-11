"""The citizens. Each agent only does its own job and talks through the Board."""
import importlib
import shutil
import zipfile
from pathlib import Path

from . import designer, llm
from .catalog import CATALOG

OUT = Path(__file__).resolve().parent.parent / "out"


class Agent:
    name = "agent"
    role = "agent"

    def __init__(self, board):
        self.board = board

    def say(self, to, cat, text):
        self.board.say(self.name, to, cat, text)

    def step(self):
        """Take one task if available. Returns True if work was done."""
        t = self.board.next_task(self.role)
        if not t:
            return False
        self.board.set_status(t["id"], "doing")
        try:
            result = self.work(t)
            self.board.set_status(t["id"], "done", result or "ok")
        except Exception as e:
            self.board.set_status(t["id"], "failed", f"{e.__class__.__name__}: {e}")
            self.say("mayor", t["category"], f"Task '{t['title']}' failed: {e}")
        return True


class Mayor(Agent):
    """Plans the pipeline per product line and writes the closing report."""
    name = "mayor"
    role = "mayor"

    def plan(self, keys):
        for key in keys:
            c = CATALOG[key]
            self.say("all", key, f"New line opened: {c['category']} -> '{c['name']}' at ${c['price']}.")
            r = self.board.add_task(key, "Research niche + positioning", "researcher")
            b = self.board.add_task(key, "Build the product", "builder", r)
            q = self.board.add_task(key, "QA the product", "qa", b)
            g = self.board.add_task(key, "Design listing images", "designer", q)
            w = self.board.add_task(key, "Write store listing", "copywriter", g)
            self.board.add_task(key, "Package + launch kit", "publisher", w)

    def supervise(self):
        """If QA failed, send the product back to the builder (max 2 retries)."""
        for t in self.board.tasks():
            if t["role"] == "qa" and t["status"] == "failed":
                key = t["category"]
                tries = self.board.recall(f"{key}:retries", 0)
                self.board.db.execute("UPDATE tasks SET status='superseded' WHERE id=?", (t["id"],))
                self.board.db.commit()
                if tries >= 2:
                    self.say("all", key, f"Giving up on {key} after {tries} retries: {t['result']}")
                    continue
                self.board.remember(f"{key}:retries", tries + 1)
                self.say("forge", key, f"Fix and rebuild (retry {tries + 1}): {t['result']}")
                b = self.board.add_task(key, "Rebuild the product", "builder")
                q = self.board.add_task(key, "QA the product (retry)", "qa", b)
                # re-point the downstream tasks at the new QA
                self.board.db.execute(
                    "UPDATE tasks SET depends_on=? WHERE category=? AND role='designer' AND status='open'",
                    (q, key),
                )
                self.board.db.commit()


class Researcher(Agent):
    name = "scout"
    role = "researcher"

    def work(self, t):
        key = t["category"]
        c = CATALOG[key]
        text = llm.ask(
            "You are a sharp digital-product market researcher.",
            f"Product: {c['name']} for {c['buyer']}. In 5 bullets: the buyer's top pains, "
            f"3 differentiators vs generic competitors, and one pricing note around ${c['price']}.",
        )
        brief = {
            "buyer": c["buyer"],
            "angle": c["angle"],
            "keywords": c["keywords"],
            "notes": text
            or f"Buyer: {c['buyer']}. Angle: {c['angle']} Differentiate by being niche-specific, "
            f"instantly usable, and clearly priced at ${c['price']}.",
        }
        self.board.remember(f"{key}:brief", brief)
        self.say("builder", key, f"Brief ready. Angle: {c['angle']}")
        self.say("scribe", key, f"Target keywords: {', '.join(c['keywords'])}")
        return "brief saved"


class Builder(Agent):
    name = "forge"
    role = "builder"

    def work(self, t):
        key = t["category"]
        c = CATALOG[key]
        brief = self.board.recall(f"{key}:brief", {})
        mod = importlib.import_module(f"products.{c['module']}")
        outdir = OUT / key / "product"
        if outdir.exists():
            shutil.rmtree(outdir)
        outdir.mkdir(parents=True)
        files = mod.build(outdir, c, brief)
        self.board.remember(f"{key}:files", [str(Path(f).relative_to(outdir)) for f in files])
        self.say("qa", key, f"Built {len(files)} files for '{c['name']}'. Ready for inspection.")
        return f"{len(files)} files"


class QA(Agent):
    name = "sentinel"
    role = "qa"

    def work(self, t):
        key = t["category"]
        c = CATALOG[key]
        mod = importlib.import_module(f"products.{c['module']}")
        outdir = OUT / key / "product"
        import inspect
        params = inspect.signature(mod.validate).parameters
        problems = mod.validate(outdir, cfg=c) if "cfg" in params else mod.validate(outdir)
        if problems:
            self.say("forge", key, "QA FAILED: " + "; ".join(problems))
            raise RuntimeError("; ".join(problems))
        self.say("mayor", key, "QA passed: all checks green.")
        return "passed"


class Designer(Agent):
    """Builds the listing images from the real product."""
    name = "canvas"
    role = "designer"

    def work(self, t):
        key = t["category"]
        c = CATALOG[key]
        imgdir = OUT / key / "images"
        if imgdir.exists():
            shutil.rmtree(imgdir)
        files = designer.build_images(key, c, OUT / key / "product", imgdir)
        problems = designer.validate(imgdir)
        if problems:
            raise RuntimeError("; ".join(problems))
        self.say("scribe", key, f"{len(files)} listing images ready (hero, inside, preview, how-it-works, details, cover).")
        return f"{len(files)} images"


class Copywriter(Agent):
    name = "scribe"
    role = "copywriter"

    def work(self, t):
        key = t["category"]
        c = CATALOG[key]
        brief = self.board.recall(f"{key}:brief", {})
        files = c["deliverables"]
        text = llm.ask(
            "You write honest, specific, non-hypey digital product store listings.",
            f"Write an Etsy/Gumroad listing (title <=120 chars, 150-word description with a "
            f"'What's included' bullet list, 13 tags) for: {c['name']}, ${c['price']}. "
            f"Buyer: {c['buyer']}. Included: {files}. Notes: {brief.get('notes')}",
            max_tokens=900,
        )
        if not text:
            kw = c["keywords"]
            bullets = "\n".join(f"- {d}" for d in files)
            text = (
                f"TITLE: {c['name']} | {kw[0]} | Instant Download\n\n"
                f"DESCRIPTION:\nBuilt for {c['buyer']}.\n\n{c['angle']}\n\n"
                f"What's included:\n{bullets}\n\n"
                f"Instant digital download. No physical item is shipped. "
                f"See README inside for setup in under 5 minutes.\n\n"
                f"PRICE: ${c['price']}\n\nTAGS: {', '.join(kw)}, instant download, digital download"
            )
        self.board.remember(f"{key}:listing", text)
        self.say("sentinel", key, "Listing drafted. Please check claims match the product.")
        return "listing saved"


class Publisher(Agent):
    """Zips the product, writes the listing, and prepares the upload kit.

    Actually posting to Etsy/Gumroad needs the owner's seller account and
    OAuth, so this agent stops at an upload-ready kit (see LAUNCH.md)."""
    name = "herald"
    role = "publisher"

    def work(self, t):
        key = t["category"]
        c = CATALOG[key]
        base = OUT / key
        listing = self.board.recall(f"{key}:listing", "(listing missing)")
        (base / "listing.md").write_text(f"# {c['name']}\n\n{listing}\n\nIMAGE ORDER: 01_hero (main), 02_whats_inside, 03_preview, 04_how_it_works, 05_details. "
                                         f"Gumroad-style cover: cover_1280x720.png (see images/).\n")
        zpath = base / f"{key}_bundle.zip"
        with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted((base / "product").rglob("*")):
                if f.is_file():
                    z.write(f, f.relative_to(base / "product"))
        self.say("mayor", key, f"Launch kit ready: {zpath.name} ({zpath.stat().st_size // 1024} KB) + listing.md")
        return str(zpath)
