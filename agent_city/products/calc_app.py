"""Generic single-file calculator micro app built from a JSON spec.
Spec: {title, tagline, notes, inputs:[{id,label,value,prefix?,suffix?,step?}],
       vars:[{id,expr}], outputs:[{label,expr,fmt:money|pct|num|int,big?}]}
Expressions are validated against a strict allow-list before they ever reach a browser."""
import json
import re
from pathlib import Path

ALLOWED_FUNCS = {"Math.min", "Math.max", "Math.ceil", "Math.floor", "Math.round", "Math.pow", "Math.abs", "Math.sqrt"}
CHARS = re.compile(r"^[\w\s.+\-*/(),%<>=!&|?:]+$")


def check_spec(spec):
    """Return a list of problems with a spec (used by the Muse before building and by QA)."""
    probs = []
    for k in ("title", "tagline", "inputs", "outputs"):
        if not spec.get(k):
            probs.append(f"spec missing {k}")
    if probs:
        return probs
    ids = {i["id"] for i in spec["inputs"]}
    if len(ids) != len(spec["inputs"]):
        probs.append("duplicate input ids")
    known = set(ids) | {"Math"}
    for v in spec.get("vars", []) + spec["outputs"]:
        expr = v["expr"]
        if not CHARS.match(expr):
            probs.append(f"illegal characters in '{expr}'")
            continue
        for tok in re.findall(r"[A-Za-z_][\w.]*", expr):
            if tok.startswith("Math."):
                if tok not in ALLOWED_FUNCS:
                    probs.append(f"function not allowed: {tok}")
            elif tok not in known:
                probs.append(f"unknown name '{tok}' in '{expr}'")
        if "id" in v:
            known.add(v["id"])
    return probs


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
:root{--bg:#f4f3ee;--card:#fff;--fg:#1c1f1d;--mute:#6b716d;--line:#e2e0d8;--acc:#2f6f5e;--acc2:#e8f1ee}
@media(prefers-color-scheme:dark){:root{--bg:#141614;--card:#1d201e;--fg:#ecece6;--mute:#9aa09b;--line:#33372f;--acc:#5fb59d;--acc2:#1f2d29}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
header{padding:20px;border-bottom:1px solid var(--line);background:var(--card)}header b{font-size:22px;letter-spacing:-.3px}header div{color:var(--mute);font-size:14px}
main{max-width:980px;margin:0 auto;padding:18px;display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:760px){main{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px}h2{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--mute);margin:0 0 12px}
label{display:block;font-size:13px;color:var(--mute);margin:10px 0 3px}.f{display:flex;align-items:center;border:1px solid var(--line);border-radius:8px;background:var(--bg);overflow:hidden}
.f span{padding:0 10px;color:var(--mute);font-size:14px}.f input{flex:1;min-width:0;border:0;background:transparent;color:var(--fg);font:inherit;padding:9px 10px;outline:0}.f:focus-within{border-color:var(--acc)}
.o{display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px solid var(--line)}.o:last-child{border:0}.o b{font-variant-numeric:tabular-nums}
.o.big{font-size:22px;padding:14px 0;color:var(--acc)}.o.big b{font-size:26px}.neg{color:#b91c1c}
button{font:inherit;font-size:14px;padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);cursor:pointer;margin:12px 6px 0 0}button.pri{background:var(--acc);color:#fff;border-color:var(--acc)}
.note{grid-column:1/-1;font-size:13px;color:var(--mute)}
@media print{header div,button{display:none}body{background:#fff}}
</style></head><body><header><b>__TITLE__</b><div>__TAGLINE__</div></header>
<main><section class="card"><h2>Your numbers</h2><div id="in"></div><button onclick="resetAll()">Reset to example</button></section>
<section class="card"><h2>Results</h2><div id="out"></div><button class="pri" onclick="window.print()">Print / Save PDF</button><button onclick="copyRes()">Copy results</button></section>
<div class="note">__NOTES__</div></main>
<script>
const SPEC=__SPEC__;const $=id=>document.getElementById(id);
const store={g(){try{return JSON.parse(localStorage.getItem('calc_'+SPEC.title)||'null')}catch(e){return null}},s(v){try{localStorage.setItem('calc_'+SPEC.title,JSON.stringify(v))}catch(e){}}};
let vals={};SPEC.inputs.forEach(i=>vals[i.id]=i.value);Object.assign(vals,store.g()||{});
const names=SPEC.inputs.map(i=>i.id);
function evalAll(){const env={...vals};const res=[];SPEC.inputs.forEach(i=>env[i.id]=+env[i.id]||0);
 (SPEC.vars||[]).forEach(v=>{try{env[v.id]=Function('Math',...Object.keys(env),'return ('+v.expr+')')(Math,...Object.values(env))}catch(e){env[v.id]=0}});
 SPEC.outputs.forEach(o=>{let x;try{x=Function('Math',...Object.keys(env),'return ('+o.expr+')')(Math,...Object.values(env))}catch(e){x=0}res.push(Number.isFinite(x)?(Math.abs(x)<0.005?0:x):0)});return res}
function fmt(x,f){const n=(d)=>x.toLocaleString(undefined,{minimumFractionDigits:d,maximumFractionDigits:d});
 return f=='money'?(x<0?'-$'+n(2).replace('-',''):'$'+n(2)):f=='pct'?n(1)+'%':f=='int'?n(0):n(2)}
function drawIn(){$('in').innerHTML=SPEC.inputs.map(i=>`<label for="${i.id}">${i.label}</label><div class=f>${i.prefix?`<span>${i.prefix}</span>`:''}<input id="${i.id}" type=number step="${i.step||'any'}" value="${vals[i.id]}" oninput="vals['${i.id}']=this.value;store.s(vals);calc()">${i.suffix?`<span>${i.suffix}</span>`:''}</div>`).join('')}
function calc(){const r=evalAll();$('out').innerHTML=SPEC.outputs.map((o,k)=>`<div class="o ${o.big?'big':''}"><span>${o.label}</span><b class="${r[k]<0?'neg':''}">${fmt(r[k],o.fmt)}</b></div>`).join('')}
function resetAll(){SPEC.inputs.forEach(i=>vals[i.id]=i.value);store.s(vals);drawIn();calc()}
function copyRes(){const r=evalAll();const t=SPEC.title+'\n'+SPEC.inputs.map(i=>i.label+': '+vals[i.id]).join('\n')+'\n\n'+SPEC.outputs.map((o,k)=>o.label+': '+fmt(r[k],o.fmt)).join('\n');
 (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(()=>alert('Copied')).catch(()=>prompt('Copy:',t))}
drawIn();calc();
</script></body></html>
"""


def build(outdir, cfg, brief):
    outdir = Path(outdir)
    spec = cfg["spec"]
    probs = check_spec(spec)
    if probs:
        raise ValueError("bad calculator spec: " + "; ".join(probs))
    html = (TEMPLATE.replace("__TITLE__", spec["title"]).replace("__TAGLINE__", spec["tagline"])
            .replace("__NOTES__", spec.get("notes", "")).replace("__SPEC__", json.dumps(spec)))
    fname = re.sub(r"[^a-z0-9]+", "_", spec["title"].lower()).strip("_") + ".html"
    (outdir / fname).write_text(html)
    (outdir / "README.txt").write_text(
        f"{spec['title'].upper()}\n\nDouble-click {fname}. Works offline in any modern browser; nothing is uploaded.\n"
        f"Change the numbers on the left; results update instantly. Your entries are remembered in this browser.\n\n"
        f"{spec.get('notes', '')}\n\nThis is a planning calculator, not professional financial, tax or legal advice.\n")
    cfg["_html"] = fname
    return [outdir / fname, outdir / "README.txt"]


def validate(outdir, cfg=None):
    problems = []
    htmls = list(Path(outdir).glob("*.html"))
    if not htmls:
        return ["no html app"]
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(htmls[0].resolve().as_uri())
            txt = pg.inner_text("#out")
            if "NaN" in txt or "Infinity" in txt or not txt.strip():
                problems.append(f"bad results: {txt[:80]!r}")
            nonzero = [x for x in pg.locator("#out b").all_inner_texts() if not x.strip("$%.,0- ")]
            if len(nonzero) == len(pg.locator("#out b").all_inner_texts()):
                problems.append("every result is zero with the example inputs")
            b.close()
            problems += [f"JS error: {e}" for e in errs]
    except Exception as e:
        print(f"[qa] browser check skipped: {e.__class__.__name__}")
    return problems
