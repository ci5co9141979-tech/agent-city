"""Muse: decides what the city builds next, once a week.

Offline: rotates through product types and draws the next unused entry from the vetted
backlog (city/backlog.py). With ANTHROPIC_API_KEY: when the backlog for a type runs dry
(and for courses, which need real writing) it asks Claude to invent a new niche spec,
which is schema-checked before anything is built."""
import datetime as dt
import json
import re
from pathlib import Path

from . import backlog, llm
from .agents import Agent
from .catalog import CATALOG

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state" / "launched.json"

KINDS = {  # kind -> (catalog category, module, family, key prefix, backlog list)
    "calc": ("AI Micro Apps", "calc_app", "micro_app", "calc", backlog.CALCS),
    "lut": ("Niche Presets & Video LUTs", "lut_niche", "luts", "lut", backlog.LUT_NICHES),
    "printable": ("Classroom & Homeschool Printables", "printable_pack", "printables", "print", backlog.PRINT_PACKS),
    "vault": ("Template Vaults & Planners", "template_vault", "template_vault", "vault", backlog.VAULTS),
}
KINDS["course"] = ("Online Courses & Student Portals", "course", "course", "course", [])
BASE_ROTATION = ["calc", "lut", "printable", "vault"]


def rotation():
    return BASE_ROTATION + (["course"] if llm.available() else [])



def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"entries": {}, "history": []}


def save_state(st):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(st, indent=1))


def pretty(fname):
    return re.sub(r"^\d+_", "", fname.rsplit(".", 1)[0]).replace("_", " ")


def make_entry(kind, item):
    category, module, family, prefix, _ = KINDS[kind]
    spec = item["spec"]
    e = {"category": category, "name": item["name"], "module": module, "family": family, "price": item["price"],
         "buyer": item["buyer"], "angle": item["angle"], "keywords": item["keywords"], "spec": spec, "kind": kind}
    if kind == "calc":
        e["deliverables"] = ["Single-file calculator app (works offline in any browser)", "README with setup notes"]
        e["license"] = "Use for your own business. No resale or redistribution of the app."
    elif kind == "lut":
        e["deliverables"] = [f"{len(spec['looks'])} x .cube 33-point LUTs", "Before/after preview image", "Install guide for Resolve, Premiere and Final Cut"]
        e["license"] = "Personal and commercial use in your own video projects. No resale or redistribution of the LUT files."
    elif kind == "printable":
        e["deliverables"] = [f"{pretty(f['file'])} (PDF)" for f in spec["files"]] + ["US Letter, print at 100%"]
        e["license"] = "Personal and classroom/homeschool use. No resale or redistribution of the files."
    elif kind == "course":
        n = sum(len(m["lessons"]) for m in spec["modules"])
        e["deliverables"] = [f"Student portal: {len(spec['modules'])} modules, {n} lessons", "Quizzes, action checklists, notes and flashcards", "Completion certificate"]
        e["license"] = "Single-student license. Please don't share or redistribute the portal."
    elif kind == "vault":
        e["deliverables"] = ["Planning_Vault.xlsx (Google Sheets compatible)", "Notion-importable CSVs", "Caption kit"]
        e["license"] = "Personal and business use. No resale or redistribution of the files."
    return f"{prefix}_{item['slug']}", e


def extract_json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    return json.loads(m.group(0)) if m else None


class Muse(Agent):
    name = "muse"
    role = "muse"

    def invent(self, kind, used_names):
        """Ask Claude for a brand-new niche in this product type. Returns an item dict or None."""
        if not llm.available():
            return None
        schemas = {
            "calc": 'spec = {"title","tagline","notes","inputs":[{"id","label","value","prefix"?,"suffix"?,"step"?}],"vars":[{"id","expr"}],"outputs":[{"label","expr","fmt":"money|pct|num|int","big"?}]}. '
                    "Expressions use only input ids, earlier var ids, numbers, + - * / ( ) ? : comparisons, and Math.min/max/ceil/floor/round/pow/abs/sqrt. Avoid division by zero.",
            "lut": 'spec = {"pack_name","prefix","intro","looks":[{"name","desc","params":{"exp","contrast","sat","temp","tint","lift","roll", optional "wood","sky","green","dehaze"}}]} with 8 looks; '
                   "exp -0.05..0.2, contrast 0.9..1.3, sat 0..1.25, temp -0.1..0.1, tint -0.02..0.02, lift -0.02..0.08, roll 0.25..0.65.",
            "printable": 'spec = {"pack_name","files":[{"file":"1_Name.pdf","pages":[page]}]} with 5 files. page types: '
                         '{"type":"log","title","cols":[[name,weight]],"rows"} | {"type":"checklist","title","sections":[{"h","items"}]} | {"type":"grid","title","first","cols":[..],"items":[..]} | '
                         '{"type":"seating","title"} | {"type":"lined","title","prompts":[..]} | {"type":"month","title"} | {"type":"weekly","title","rows":[..]}',
            "course": 'spec = {"title","glossary":[[term,definition]x8],"modules":[{"title","lessons":[{"t","b":"120-170 words, paragraphs separated by blank line","do":[2 action steps],"q":{"q","o":[4 options],"a":index 0-3,"why"}}]}]} '
                      "with 5 modules x 3 lessons. Practical, accurate, no income promises, no invented statistics.",
            "vault": 'spec = {"title","defaults":{"business","topic","goal","product","customer"},"income":[4 lines],"expenses":[7 lines],"ideas":{"Educate":[6],"Behind the scenes":[6],"Social proof":[6],"Offer / promo":[6],"Personal story":[6],"Engage / community":[6]}}. '
                     "Ideas may use {topic} {goal} {product} {customer}.",
        }
        text = llm.ask(
            "You design honest, genuinely useful digital products for small buyers. Reply with ONE JSON object and nothing else.",
            f"Invent a NEW niche product of type '{kind}' that is not any of: {sorted(used_names)}. "
            f'Return {{"slug","name","price","buyer","angle","keywords":[5],"spec":...}}. {schemas[kind]} '
            f"Prices: calc 47, lut 24-29, printable 12-18, vault 29, course 79-100.",
            max_tokens=3500,
        )
        try:
            item = extract_json(text)
            if not item or not all(k in item for k in ("slug", "name", "price", "buyer", "angle", "keywords", "spec")):
                return None
            if kind == "calc":
                from products.calc_app import check_spec
                if check_spec(item["spec"]):
                    return None
            if kind == "lut" and len(item["spec"].get("looks", [])) < 6:
                return None
            if kind == "course":
                mods = item["spec"].get("modules", [])
                if len(mods) < 3 or any(not (0 <= l["q"]["a"] < len(l["q"]["o"])) for m in mods for l in m["lessons"]):
                    return None
            if kind == "printable" and len(item["spec"].get("files", [])) < 3:
                return None
            item["slug"] = re.sub(r"[^a-z0-9]+", "", item["slug"].lower())[:20] or "new"
            return item
        except Exception:
            return None

    def pick(self, today=None):
        """Return (key, entry) for this week's product, or (None, reason)."""
        today = today or dt.date.today()
        st = load_state()
        n = len(st["history"])
        rot = rotation()
        order = [rot[(n + i) % len(rot)] for i in range(len(rot))]
        for kind in order:
            items = KINDS[kind][4]
            used = {e["name"] for e in st["entries"].values()}
            fresh = [it for it in items if f"{KINDS[kind][3]}_{it['slug']}" not in st["entries"]]
            item = fresh[0] if fresh else self.invent(kind, used)
            if item:
                key, entry = make_entry(kind, item)
                st["entries"][key] = entry
                st["history"].append({"week": today.isocalendar()[:2], "date": today.isoformat(), "key": key})
                save_state(st)
                src = "backlog" if fresh else "invented by Claude"
                self.say("mayor", key, f"This week's pick: '{entry['name']}' ({entry['category']}, {src}). "
                         f"Rotation slot {n % len(rot) + 1}/{len(rot)}; {len(st['history'])} weekly products so far.")
                return key, entry
        return None, "backlog empty for every product type and no ANTHROPIC_API_KEY to invent more"
