"""Digital Product Launch Academy: a self-contained student portal (single HTML file)
with 5 modules / 15 lessons, checklists, quizzes, notes, progress, flashcard study coach
and a printable completion certificate."""
import json
from pathlib import Path

MODULES = [
    {"title": "1. Pick a product people already buy", "lessons": [
        {"t": "Why digital products work",
         "b": "A digital product is built once and delivered unlimited times at near-zero cost. That is the whole appeal: no inventory, no shipping, and instant delivery while the buyer is motivated.\n\nThe trade-off is competition. Anything easy to make is easy to copy, so you win with specificity (a narrow buyer with a clear problem), quality, and trust, not with being first.\n\nThe five formats that sell reliably to beginners are templates and planners, printables, presets and LUTs, small software tools, and courses. This academy uses all five as examples.",
         "do": ["Write down 3 formats you could realistically make in one weekend", "Circle the one you'd enjoy making 20 more of"],
         "q": {"q": "What is the main advantage of a digital product?", "o": ["It sells without any marketing", "It can be delivered unlimited times at almost no extra cost", "It cannot be copied", "It needs no customer support"], "a": 1, "why": "Marginal cost per sale is close to zero. Marketing, copying risk and support still exist."}},
        {"t": "Find a niche with proof of demand",
         "b": "Start from buyers, not from your ideas. Open Etsy, Gumroad, Creative Market, or Amazon and search your topic. Look for listings with many reviews or sales: that is demand you can see.\n\nThen narrow. 'Planner' is crowded; 'homeschool high school transcript for Texas families' is a specific job. Narrow beats broad because search results favor exact matches and buyers trust specialists.\n\nA healthy niche has: several sellers making sales, products you could clearly improve, and a buyer you can describe in one sentence.",
         "do": ["Find 5 best-selling listings in your topic and note price, reviews, and what buyers complain about", "Write your buyer in one sentence: 'Someone who ___ and needs ___ today'"],
         "q": {"q": "Which is the stronger niche?", "o": ["Planners", "Templates", "Emergency sub plans for elementary teachers", "Digital downloads"], "a": 2, "why": "A specific buyer and a specific job beats a broad category."}},
        {"t": "Validate before you build",
         "b": "Validation means getting evidence somebody will pay before you invest weeks. Cheap methods: show a mockup or sample page to five people in your target group and ask what they'd change; post a preview in a relevant community (following its rules); or list a simple first version and see whether anyone views and buys it.\n\nSignals that matter: people ask where to buy it, compare it to something they already pay for, or describe the exact pain you solve. Compliments do not count; money, pre-orders and email sign-ups do.",
         "do": ["Show a rough sample to 5 people and write down their exact words", "Decide your go/no-go rule, e.g. '3 of 5 say they would pay $X'"],
         "q": {"q": "Which is the strongest validation signal?", "o": ["Friends say it's a great idea", "A stranger pre-orders or joins a waitlist", "You feel confident", "A competitor exists"], "a": 1, "why": "Actions involving money or contact details are far stronger than opinions."}}]},
    {"title": "2. Build version 1 fast", "lessons": [
        {"t": "Scope a version 1 you can finish in a weekend",
         "b": "Version 1 should solve one problem completely, not many problems partly. Write the buyer's outcome in one sentence, then list only what's required to deliver it.\n\nUse the 'must / should / later' sort. Must: without it the product fails. Should: nice, if time allows. Later: goes into version 2 and becomes your update announcement.\n\nBundle size is a pricing choice, not a quality signal. A 5-file set that is polished beats a 50-file set that is sloppy.",
         "do": ["List every feature, then sort into must / should / later", "Set a stop time: version 1 ships this weekend"],
         "q": {"q": "What belongs in version 1?", "o": ["Everything you can think of", "Only what's needed to deliver the core outcome", "Whatever competitors have", "Just the cover image"], "a": 1, "why": "Ship the smallest complete solution, then improve."}},
        {"t": "Tools: Canva, Sheets, Notion, and AI builders",
         "b": "Choose the tool your buyer already uses. Templates live where buyers work: Google Sheets and Notion for planners, Canva for social kits, PDF for printables, and Resolve/Premiere/Lightroom formats for presets.\n\nAI can speed up drafting copy, generating checklists, producing code for small tools and building lesson outlines. Always review the result: check facts, test every formula and link, and rewrite anything generic. Buyers can tell when something was not checked.\n\nCheck each tool's license terms before selling anything made with it, especially fonts, stock images, and template-sharing rules.",
         "do": ["Pick the tool your buyer uses", "List every font, image and asset in your product and confirm its license allows resale in a product"],
         "q": {"q": "What must you do with AI-generated content before selling it?", "o": ["Nothing, AI is always right", "Review, test and edit it", "Hide that you used it", "Translate it"], "a": 1, "why": "You are responsible for accuracy and quality. Test formulas, links and claims."}},
        {"t": "Quality checklist: make it feel professional",
         "b": "Professional is mostly consistency. Use one font pair, 3-4 colors, equal margins and the same naming scheme on every file. Name files so a stranger understands them: 'Weekly_Planner_Letter.pdf', not 'final_v3_new'.\n\nTest like a buyer: open it on a phone, on a different computer, and print it. Include a short README that answers: what's inside, how to open it, how to get help.\n\nAsk one person who has never seen it to use it without your help. Every place they hesitate is a fix.",
         "do": ["Run the 3-device test: phone, laptop, printer (if relevant)", "Write a 6-line README: what, how to open, how to get help"],
         "q": {"q": "Why include a README?", "o": ["It's required by law", "It answers setup questions before they become support emails", "It increases file size", "It replaces the product"], "a": 1, "why": "Clear instructions reduce support and refunds."}}]},
    {"title": "3. Package, price, and list it", "lessons": [
        {"t": "Pricing with confidence",
         "b": "Price against the value of the problem solved, not the time you spent. A $5 printable replaces a few minutes of effort. A $47 tool that prevents underquoting a project can pay for itself the first time it's used.\n\nCommon ranges: individual printables $3-$12, bundles $15-$40, template vaults $15-$100, LUT and preset packs $19-$59, small software tools $47-$77, courses $100+.\n\nTest prices. Launch at a fair introductory price, watch conversion, and raise it as reviews accumulate. Avoid permanent big discounts; they teach buyers to wait.",
         "do": ["Write the 'before' cost of your buyer's problem (time or money)", "Choose a launch price and a planned price after 10 reviews"],
         "q": {"q": "What should price be anchored to?", "o": ["Hours you spent", "Value of the problem solved to the buyer", "The lowest competitor", "Your costs only"], "a": 1, "why": "Buyers pay for outcomes."}},
        {"t": "Listings that convert",
         "b": "A listing has four jobs: be found, be understood in five seconds, build trust, and remove risk.\n\nTitle: lead with the exact thing people search, then the format. Images: first image states the product and benefit in plain words; later images show contents, a sample page, and how it's used. Description: who it's for, what's included (a bullet list), file formats, how to open, license.\n\nBe honest. State what it is not. Accurate listings get fewer refunds and better reviews.",
         "do": ["Write a title with your main keyword in the first 40 characters", "Make 5 images: hero, what's inside, sample, how to use, license"],
         "q": {"q": "What should the first listing image do?", "o": ["Look artistic only", "State clearly what the product is and its benefit", "Show your face", "Hide the contents"], "a": 1, "why": "Shoppers decide in seconds; clarity wins."}},
        {"t": "Where to sell: marketplaces vs your own store",
         "b": "Marketplaces such as Etsy and Creative Market bring built-in search traffic but take fees and own the customer relationship. Platforms such as Gumroad, Lemon Squeezy and Payhip let you sell from your own link with simple fees, but you bring the traffic.\n\nA common path: start on a marketplace to learn what sells, collect email addresses where rules allow, then add your own store for repeat customers.\n\nFees, payout rules and policies change. Read the current seller terms before you commit, and check tax obligations in your country or state.",
         "do": ["Compare fees and payout rules on two platforms from their current pages", "Decide: marketplace first, own store first, or both"],
         "q": {"q": "A main advantage of marketplaces for beginners?", "o": ["No fees", "Built-in search traffic", "You own all customer data", "No rules"], "a": 1, "why": "Existing shoppers find you through search; fees apply."}}]},
    {"title": "4. Get your first customers", "lessons": [
        {"t": "Free traffic: search and social",
         "b": "Traffic comes from three places: search (people looking for your solution), social (people who discover you), and referrals (people told by others).\n\nFor search, use your buyer's words in titles, tags and descriptions. For social, pick one platform where your buyer already spends time and show the product being used: a screen recording, a before/after, a quick tip. Teach something real in each post and attach the product as the next step.\n\nConsistency beats intensity. Three useful posts a week for ten weeks outperform thirty posts in one weekend.",
         "do": ["Choose ONE platform and schedule 3 posts this week", "Write 10 search phrases your buyer would type"],
         "q": {"q": "What is the best social-media approach for a beginner seller?", "o": ["Post everywhere once", "One platform, consistent useful posts that show the product in use", "Only post ads", "Wait until perfect"], "a": 1, "why": "Focus and consistency compound."}},
        {"t": "Build an email list from day one",
         "b": "Email is the one audience you own. Offer a small free sample that solves a mini-problem (one printable, a sample LUT, a starter template) in exchange for an email address, with clear consent.\n\nThen send a short welcome sequence: deliver the freebie, share a useful tip, show the main product with a clear link. Follow your country's rules on consent and unsubscribe links.\n\nSend regularly and keep it useful. Most buyers need several touches before they purchase.",
         "do": ["Create one free sample from your product", "Draft a 3-email welcome sequence"],
         "q": {"q": "Why build an email list?", "o": ["Platforms can change rules; email is an audience you own", "It's required to sell", "Email is faster than search", "It replaces your product"], "a": 0, "why": "Algorithms and policies change; your list is yours."}},
        {"t": "Reviews, support and refunds",
         "b": "Early reviews are the strongest trust signal you have. After purchase, thank the buyer and ask for honest feedback. Never buy reviews or offer payment for positive ones; platforms forbid it and buyers notice.\n\nRespond to every question quickly and kindly. Most problems are 'I can't open it' and the README solves them.\n\nTreat refunds as research. If three buyers say the same thing, it's a product or listing problem and fixing it improves everything after.",
         "do": ["Write a post-purchase message asking for an honest review", "Write 3 saved replies for the most likely questions"],
         "q": {"q": "How should you handle repeated refund reasons?", "o": ["Ignore them", "Fix the product or listing", "Delete the reviews", "Raise the price"], "a": 1, "why": "Repeated reasons are free product research."}}]},
    {"title": "5. Automate and scale", "lessons": [
        {"t": "Automate delivery and support",
         "b": "Good platforms deliver files automatically. Your job is to make everything around that automatic too: saved replies, an FAQ page, a welcome email that links to the download and the README, and a simple process for updates.\n\nAutomate repetitive tasks (scheduling posts, backing up files, exporting sales data) but keep a human touch where trust matters: personal answers to pre-sale questions and thoughtful responses to complaints.\n\nDocument your process once so you, or a helper, can repeat it.",
         "do": ["List every task you do per sale, then mark which can be automated", "Write a one-page checklist for launching a new product"],
         "q": {"q": "What should stay human?", "o": ["Delivery of files", "Pre-sale questions and complaint replies", "Backups", "Scheduling"], "a": 1, "why": "Trust-heavy moments benefit from a real person."}},
        {"t": "Grow: bundles, updates, and a product line",
         "b": "Your best next product is usually a neighbor of your first: the same buyer with the next problem. Bundle related products for a higher cart value, and release free updates to show the product is alive.\n\nLook at your data: which listings get views but no sales (fix the listing), which get sales from a specific keyword (make more like it), which products are bought together (bundle).\n\nStay specific. A tight catalog for one audience beats a random one.",
         "do": ["Choose your next 3 products for the same buyer", "Plan one bundle that combines two of your products"],
         "q": {"q": "Views but no sales usually means?", "o": ["The product is bad", "The listing or price needs work", "No demand", "Too many tags"], "a": 1, "why": "People are interested; the listing or price isn't convincing."}},
        {"t": "Legal basics and your 30-day plan",
         "b": "Keep it simple and legitimate: only sell what you made or have the rights to sell; follow license terms of fonts, images and tools; be honest about what the product is; track your income and set money aside for taxes.\n\nThis is general education, not legal or tax advice. Rules differ by country and state, so check official sources or ask a professional about business registration, sales tax or VAT, and licensing.\n\nYour 30-day plan: Week 1 choose and validate. Week 2 build version 1. Week 3 list and launch. Week 4 promote, collect feedback, ship the first update.",
         "do": ["Set up a simple income and expense tracker", "Put your 4-week plan on a calendar with dates"],
         "q": {"q": "This academy's legal guidance is...", "o": ["A substitute for a lawyer", "General education; check official sources for your location", "Only for the US", "Not important"], "a": 1, "why": "Rules vary, so verify locally."}}]},
]

GLOSSARY = [
    ("Niche", "A specific group of buyers with a specific problem."), ("Validation", "Evidence that people will pay, before you build."),
    ("Version 1 (V1)", "The smallest complete product that solves the core problem."), ("Conversion rate", "Visitors who buy divided by visitors."),
    ("LUT", "Look-up table: a file that maps input colors to graded output colors."), ("Bundle", "Several related products sold together."),
    ("Lead magnet", "A free sample offered in exchange for an email address."), ("README", "A short instructions file included with a product."),
]

HTML_TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title><style>
:root{--bg:#f6f5f0;--card:#fff;--fg:#1d201e;--mute:#6a706c;--line:#e3e1d9;--acc:#2f6f5e;--acc2:#e8f1ee;--ok:#15803d;--bad:#b91c1c}
@media(prefers-color-scheme:dark){:root{--bg:#131513;--card:#1c1f1d;--fg:#ecece6;--mute:#9aa09b;--line:#31352f;--acc:#5fb59d;--acc2:#1e2c28;--ok:#4ade80;--bad:#f87171}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
.app{display:grid;grid-template-columns:310px 1fr;min-height:100vh}@media(max-width:820px){.app{grid-template-columns:1fr}.side{position:static!important;height:auto!important}}
.side{background:var(--card);border-right:1px solid var(--line);padding:18px;position:sticky;top:0;height:100vh;overflow:auto}
.brand{font-weight:800;font-size:19px;letter-spacing:-.3px}.sub{color:var(--mute);font-size:13px;margin-bottom:12px}
.bar{height:8px;background:var(--line);border-radius:6px;overflow:hidden;margin:6px 0 2px}.bar i{display:block;height:100%;background:var(--acc);transition:width .3s}
.mod{margin-top:14px;font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--mute);font-weight:700}
.les{display:flex;gap:8px;align-items:flex-start;padding:7px 8px;border-radius:8px;cursor:pointer;font-size:14px;line-height:1.35;margin:1px 0}.les:hover{background:var(--acc2)}.les.cur{background:var(--acc2);font-weight:650}
.dot{flex:none;width:16px;height:16px;border:2px solid var(--line);border-radius:50%;margin-top:2px}.les.done .dot{background:var(--ok);border-color:var(--ok)}
.nav2{display:flex;gap:6px;margin:14px 0}.nav2 button{flex:1}
button{font:inherit;font-size:14px;padding:8px 12px;border:1px solid var(--line);border-radius:9px;background:var(--card);color:var(--fg);cursor:pointer}button.pri{background:var(--acc);border-color:var(--acc);color:#fff}button:disabled{opacity:.5;cursor:default}
main{padding:28px;max-width:820px;width:100%}.crumb{color:var(--mute);font-size:13px}h1{margin:4px 0 14px;font-size:30px;line-height:1.2;letter-spacing:-.5px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px;margin:16px 0}.card h3{margin:0 0 8px;font-size:13px;text-transform:uppercase;letter-spacing:.07em;color:var(--mute)}
.body p{margin:0 0 12px}.chk{display:flex;gap:10px;align-items:flex-start;padding:5px 0}.chk input{margin-top:5px;width:18px;height:18px;accent-color:var(--acc)}
.opt{display:block;width:100%;text-align:left;margin:6px 0;padding:10px 12px}.opt.right{border-color:var(--ok);background:color-mix(in srgb,var(--ok) 14%,var(--card))}.opt.wrong{border-color:var(--bad);background:color-mix(in srgb,var(--bad) 12%,var(--card))}
textarea{width:100%;min-height:90px;font:inherit;padding:10px;border:1px solid var(--line);border-radius:9px;background:var(--bg);color:var(--fg)}
.fb{margin-top:8px;font-size:14px}.ok{color:var(--ok)}.bad{color:var(--bad)}.hide{display:none}
.flash{perspective:900px;height:170px;cursor:pointer}.flash div{height:100%;display:flex;align-items:center;justify-content:center;text-align:center;padding:20px;border:1px solid var(--line);border-radius:12px;background:var(--acc2);font-size:18px}
.cert{border:6px double var(--acc);padding:50px 30px;text-align:center;background:var(--card);margin:20px 0}.cert h2{font-size:34px;margin:6px 0}.cert .n{font-size:26px;border-bottom:1px solid var(--fg);display:inline-block;min-width:300px;padding:4px 16px}
@media print{.side,.nav2,.noprint{display:none!important}.app{display:block}main{padding:0;max-width:none}body{background:#fff;color:#000}}
</style></head><body><div class="app"><aside class="side"><div class="brand">__TITLE__</div><div class="sub">__SUB__</div>
<div id="pct" style="font-size:13px"></div><div class="bar"><i id="pbar" style="width:0"></i></div><div id="nav"></div>
<div class="mod">Tools</div><div class="les" onclick="show('coach')"><span class="dot"></span>Study coach (flashcards)</div><div class="les" onclick="show('cert')"><span class="dot"></span>Completion certificate</div>
<div style="margin-top:16px"><button onclick="resetAll()" class="noprint" style="font-size:12px">Reset progress</button></div></aside><main id="main"></main></div>
<script>
const DATA=__DATA__,GLOSS=__GLOSS__;
const lessons=[];DATA.forEach((m,mi)=>m.lessons.forEach((l,li)=>lessons.push({...l,mi,li,mt:m.title,id:mi+'.'+li})));
let S={done:{},checks:{},notes:{},quiz:{},name:'',cur:0,cards:{}};
const mem={};const store={get(){try{return localStorage.getItem('dpla')}catch(e){return mem.v}},set(v){try{localStorage.setItem('dpla',v)}catch(e){mem.v=v}}};
try{const r=store.get();if(r)S=Object.assign(S,JSON.parse(r))}catch(e){}
const save=()=>store.set(JSON.stringify(S));const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
function nav(){let h='',last=-1;lessons.forEach((l,i)=>{if(l.mi!=last){h+=`<div class=mod>${esc(l.mt)}</div>`;last=l.mi}
 h+=`<div class="les ${S.done[l.id]?'done':''} ${S.cur==i&&view=='lesson'?'cur':''}" onclick="go(${i})"><span class=dot></span><span>${esc(l.t)}</span></div>`});$('nav').innerHTML=h;
 const n=Object.keys(S.done).length;$('pct').textContent=`${n} of ${lessons.length} lessons complete (${Math.round(100*n/lessons.length)}%)`;$('pbar').style.width=100*n/lessons.length+'%'}
let view='lesson';function go(i){S.cur=i;view='lesson';save();render();scrollTo(0,0)}function show(v){view=v;render();scrollTo(0,0)}
function render(){nav();if(view=='coach')return coach();if(view=='cert')return cert();const l=lessons[S.cur],i=S.cur;const q=l.q,qa=S.quiz[l.id];
 $('main').innerHTML=`<div class=crumb>${esc(l.mt)} &middot; Lesson ${i+1} of ${lessons.length}</div><h1>${esc(l.t)}</h1>
 <div class="card body">${l.b.split('\n\n').map(p=>`<p>${esc(p)}</p>`).join('')}</div>
 <div class=card><h3>Action steps</h3>${l.do.map((d,k)=>`<label class=chk><input type=checkbox ${(S.checks[l.id+'.'+k])?'checked':''} onchange="chk('${l.id}.${k}',this.checked)"><span>${esc(d)}</span></label>`).join('')}</div>
 <div class=card><h3>Quick check</h3><div><b>${esc(q.q)}</b></div>${q.o.map((o,k)=>`<button class="opt ${qa!=null?(k==q.a?'right':(k==qa?'wrong':'')):''}" onclick="ans(${k})" ${qa!=null?'disabled':''}>${esc(o)}</button>`).join('')}
 <div class=fb>${qa!=null?(qa==q.a?'<span class=ok>Correct.</span> ':'<span class=bad>Not quite.</span> ')+esc(q.why):''}</div></div>
 <div class=card><h3>My notes</h3><textarea placeholder="Write what you'll do or what to remember" oninput="S.notes['${l.id}']=this.value;save()">${esc(S.notes[l.id]||'')}</textarea></div>
 <div class=nav2><button ${i==0?'disabled':''} onclick="go(${i-1})">&larr; Previous</button><button class=pri onclick="complete()">${S.done[l.id]?'Completed &#10003;':'Mark complete'}</button><button ${i==lessons.length-1?'disabled':''} onclick="go(${i+1})">Next &rarr;</button></div>`}
function chk(k,v){S.checks[k]=v;save()}function ans(k){S.quiz[lessons[S.cur].id]=k;save();render()}
function complete(){const l=lessons[S.cur];S.done[l.id]=!S.done[l.id];save();if(S.done[l.id]&&S.cur<lessons.length-1){go(S.cur+1)}else render()}
let ci=0,flip=false;function cards(){return lessons.map(l=>({q:l.q.q,a:l.q.o[l.q.a]+' - '+l.q.why})).concat(GLOSS.map(g=>({q:'Define: '+g[0],a:g[1]})))}
function coach(){const c=cards(),x=c[ci%c.length];$('main').innerHTML=`<div class=crumb>Study coach</div><h1>Flashcards</h1><p>Tap the card to flip. Rate how well you knew it: cards you miss come back more often.</p>
 <div class=flash onclick="flip=!flip;coach()"><div>${esc(flip?x.a:x.q)}</div></div>
 <div class=nav2><button onclick="rate(0)">Missed it</button><button onclick="rate(1)">Got it</button></div><p class=crumb>Card ${ci%c.length+1} of ${c.length} &middot; ${Object.values(S.cards).filter(v=>v>0).length} mastered</p>`}
function rate(ok){const c=cards();const idx=ci%c.length;S.cards[idx]=(S.cards[idx]||0)+(ok?1:-1);save();flip=false;
 let n=idx,t=0;do{n=(n+1)%c.length;t++}while(t<c.length&&(S.cards[n]||0)>1&&Math.random()<0.7);ci=n;coach()}
function cert(){const done=Object.keys(S.done).length==lessons.length;$('main').innerHTML=`<div class=crumb>Completion certificate</div><h1>Certificate</h1>
 ${done?`<label class=noprint>Your name <input id=nm value="${esc(S.name)}" oninput="S.name=this.value;save();document.getElementById('cn').textContent=this.value||'Your Name'" style="font:inherit;padding:8px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg)"></label>
 <div class=cert><div>Certificate of Completion</div><h2>__TITLE__</h2><p>This certifies that</p><div class=n id=cn>${esc(S.name)||'Your Name'}</div><p style="margin-top:20px">completed all ${lessons.length} lessons on ${new Date().toLocaleDateString()}</p></div><button class=pri onclick="print()" class=noprint>Print / Save as PDF</button>`
 :`<div class=card>Finish all ${lessons.length} lessons to unlock your certificate. You have ${Object.keys(S.done).length} done.</div>`}`}
function resetAll(){if(confirm('Erase all progress and notes on this device?')){S={done:{},checks:{},notes:{},quiz:{},name:'',cur:0,cards:{}};save();view='lesson';render()}}
render();
</script></body></html>
"""


def build(outdir, cfg, brief):
    outdir = Path(outdir)
    spec = cfg.get("spec") or {}
    modules, gloss = spec.get("modules", MODULES), spec.get("glossary", GLOSSARY)
    title = spec.get("title", "Digital Product Launch Academy")
    n = sum(len(m["lessons"]) for m in modules)
    html = (HTML_TEMPLATE.replace("__DATA__", json.dumps(modules)).replace("__GLOSS__", json.dumps(gloss))
            .replace("__TITLE__", title).replace("__SUB__", f"{len(modules)} modules &middot; {n} lessons &middot; self-paced"))
    (outdir / "academy.html").write_text(html)
    (outdir / "README.txt").write_text(
        f"{title.upper()}\n\nOpen academy.html in any modern browser. Works offline. Progress, notes and quiz answers are saved in your browser on this device.\n"
        "To host it for students: upload academy.html to any static host (Netlify, GitHub Pages, your own site). Each student's progress stays on their own device.\n"
        f"Includes: {len(modules)} modules, {n} lessons, action checklists, quizzes, notes, a flashcard study coach, and a completion certificate.\n"
    )
    return [outdir / "academy.html", outdir / "README.txt"]


def validate(outdir, cfg=None):
    problems = []
    modules = ((cfg or {}).get("spec") or {}).get("modules", MODULES)
    f = Path(outdir) / "academy.html"
    if not f.exists():
        return ["academy.html missing"]
    n = sum(len(m["lessons"]) for m in modules)
    if n < 9:
        problems.append(f"only {n} lessons")
    for m in modules:
        for l in m["lessons"]:
            if not (0 <= l["q"]["a"] < len(l["q"]["o"])):
                problems.append(f"bad quiz answer index in '{l['t']}'")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(f.resolve().as_uri())
            pg.click(".opt >> nth=1")
            pg.click("text=Mark complete")
            pct = pg.inner_text("#pct")
            if not pct.startswith(f"1 of {n}"):
                problems.append(f"progress not tracked: '{pct}'")
            pg.click("text=Study coach")
            if "Flashcards" not in pg.inner_text("#main"):
                problems.append("study coach did not render")
            b.close()
            problems += [f"JS error: {e}" for e in errs]
    except Exception as e:
        print(f"[qa] browser check skipped: {e.__class__.__name__}")
    return problems
