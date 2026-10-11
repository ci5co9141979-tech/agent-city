"""Renders the city's town square (messages), task board and product status to one HTML page."""
import html
import time
from pathlib import Path

from .catalog import CATALOG

COLORS = {"mayor": "#b45309", "scout": "#0f766e", "forge": "#1d4ed8", "sentinel": "#b91c1c",
          "scribe": "#7e22ce", "canvas": "#0e7490", "muse": "#a21caf", "herald": "#15803d", "all": "#475569"}


def render(board, out_path, llm_on):
    tasks, msgs = board.tasks(), board.messages()
    cards = []
    for key, c in CATALOG.items():
        ts = [t for t in tasks if t["category"] == key]
        if not ts:
            continue
        done = sum(1 for t in ts if t["status"] == "done")
        pill = "".join(
            f'<span class="p {t["status"]}" title="{html.escape(t["title"])}">{html.escape(t["role"])}</span>' for t in ts
        )
        cards.append(
            f'<div class="card"><h3>{html.escape(c["category"])}</h3><div class="n">{html.escape(c["name"])} &middot; ${c["price"]}</div>'
            f'<div class="bar"><i style="width:{100 * done // max(len(ts), 1)}%"></i></div>{pill}</div>'
        )
    t0 = msgs[0]["ts"] if msgs else time.time()
    rows = "".join(
        f'<div class="m"><span class="t">+{m["ts"] - t0:5.1f}s</span> '
        f'<b style="color:{COLORS.get(m["sender"], "#333")}">{m["sender"]}</b> &rarr; {m["recipient"]} '
        f'<span class="c">[{m["category"]}]</span><div>{html.escape(m["body"])}</div></div>'
        for m in msgs
    )
    page = f"""<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Agent City</title><style>
:root{{--bg:#f6f5f1;--fg:#1c1b19;--card:#fff;--line:#e3e0d8}}
@media(prefers-color-scheme:dark){{:root{{--bg:#151513;--fg:#ece9e1;--card:#201f1c;--line:#34322d}}}}
body{{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}}
h1{{margin:0 0 4px}}.sub{{opacity:.7;margin-bottom:16px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px;margin-bottom:20px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}}
.card h3{{margin:0;font-size:14px}}.n{{font-size:13px;opacity:.75;margin:2px 0 8px}}
.bar{{height:6px;background:var(--line);border-radius:3px;margin-bottom:8px}}.bar i{{display:block;height:6px;background:#15803d;border-radius:3px}}
.p{{display:inline-block;font-size:11px;padding:1px 7px;border-radius:9px;margin:0 4px 4px 0;border:1px solid var(--line)}}
.p.done{{background:#15803d;color:#fff}}.p.failed{{background:#b91c1c;color:#fff}}.p.superseded{{opacity:.4}}
.m{{padding:7px 0;border-bottom:1px solid var(--line)}}.m div{{margin-top:2px}}.t{{opacity:.5;font-size:12px;font-variant-numeric:tabular-nums}}.c{{opacity:.55;font-size:12px}}
</style><h1>Agent City</h1>
<div class=sub>{len(msgs)} messages &middot; {len(tasks)} tasks &middot; brain: {'Claude API' if llm_on else 'offline templates (set ANTHROPIC_API_KEY to upgrade)'}</div>
<div class=grid>{''.join(cards)}</div><h2>Town square</h2>{rows}"""
    Path(out_path).write_text(page)
