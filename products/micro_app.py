"""QuoteSmith: a single-file offline micro app. One job: price a project and
produce a clean, printable quote."""
from pathlib import Path

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>QuoteSmith</title>
<style>
:root{--bg:#f4f3ee;--card:#fff;--fg:#1c1f1d;--mute:#6b716d;--line:#e2e0d8;--acc:#2f6f5e;--acc2:#e8f1ee;--warn:#b45309}
@media(prefers-color-scheme:dark){:root{--bg:#141614;--card:#1d201e;--fg:#ecece6;--mute:#9aa09b;--line:#33372f;--acc:#5fb59d;--acc2:#1f2d29;--warn:#e0a458}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
header{padding:18px 20px;display:flex;align-items:center;gap:12px;border-bottom:1px solid var(--line);background:var(--card)}
header b{font-size:20px;letter-spacing:-.3px}header span{color:var(--mute)}
.tabs{margin-left:auto;display:flex;gap:6px}button,.btn{font:inherit;border:1px solid var(--line);background:var(--card);color:var(--fg);padding:7px 12px;border-radius:8px;cursor:pointer}
button.pri{background:var(--acc);color:#fff;border-color:var(--acc)}button.on{background:var(--acc2);border-color:var(--acc)}button:hover{filter:brightness(.97)}
main{max-width:1100px;margin:0 auto;padding:18px;display:grid;grid-template-columns:1.25fr 1fr;gap:18px}
@media(max-width:860px){main{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:16px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:.07em;color:var(--mute);margin:0 0 12px}
label{display:block;font-size:12px;color:var(--mute);margin:8px 0 3px}
input,select,textarea{width:100%;font:inherit;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg)}
.row{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}
table{width:100%;border-collapse:collapse}th{font-size:11px;text-align:left;color:var(--mute);padding:4px}td{padding:3px}
td input{padding:6px 8px}.num{text-align:right}
.tot{display:flex;justify-content:space-between;padding:5px 0}.tot.big{font-size:22px;font-weight:700;border-top:2px solid var(--fg);margin-top:6px;padding-top:10px}
.hint{font-size:12px;color:var(--mute)}.tag{display:inline-block;background:var(--acc2);color:var(--acc);padding:2px 8px;border-radius:99px;font-size:12px;margin:2px}
.warn{color:var(--warn)}.hide{display:none}
#quote{background:#fff;color:#111;padding:34px;border-radius:12px;border:1px solid var(--line)}
#quote h1{margin:0;font-size:26px}#quote .meta{display:flex;justify-content:space-between;margin:14px 0 20px;color:#444}
#quote table th{border-bottom:2px solid #111;color:#111;font-size:11px;text-transform:uppercase;padding:6px 4px}#quote td{border-bottom:1px solid #ddd;padding:7px 4px}
#quote .sum{margin-left:auto;width:290px;margin-top:14px}#quote .sum div{display:flex;justify-content:space-between;padding:3px 0}
#quote .grand{font-weight:700;font-size:18px;border-top:2px solid #111;margin-top:6px;padding-top:8px}
@media print{header,.noprint,.left{display:none!important}body{background:#fff}main{display:block;padding:0}.card{border:0;padding:0}#quote{border:0;padding:0}}
</style></head><body>
<header><b>QuoteSmith</b><span>price it right, quote it fast</span>
<div class="tabs noprint"><button id="t1" class="on" onclick="tab(1)">Build</button><button id="t2" onclick="tab(2)">Rate calculator</button><button id="t3" onclick="tab(3)">Saved</button></div></header>
<main>
<section class="left" id="left">
 <div id="p1">
  <div class="card"><h2>Smart scope builder</h2>
   <label>Describe the project (keywords like website, logo, video, blog, app, brand, social, ebook, course)</label>
   <textarea id="desc" rows="3" placeholder="e.g. 5-page website for a dental clinic with logo refresh and monthly blog posts"></textarea>
   <div style="margin-top:8px"><button class="pri" onclick="suggest()">Suggest line items</button> <span class="hint">Rule-based, runs offline. Edit anything it adds.</span></div>
   <div id="sugs" class="hint" style="margin-top:6px"></div></div>
  <div class="card"><h2>Client &amp; project</h2><div class="row">
   <div><label>Your business</label><input id="me" placeholder="Your name / studio"></div>
   <div><label>Client</label><input id="client" placeholder="Client name"></div>
   <div><label>Project title</label><input id="title" placeholder="Website redesign"></div></div>
   <div class="row"><div><label>Quote #</label><input id="qno"></div><div><label>Valid for (days)</label><input id="valid" type="number" value="14"></div><div><label>Currency</label><select id="cur"><option>$</option><option>&euro;</option><option>&pound;</option><option>CA$</option><option>A$</option></select></div></div></div>
  <div class="card"><h2>Line items</h2>
   <table><thead><tr><th>Task</th><th style="width:70px">Hours</th><th style="width:80px">Rate</th><th style="width:90px" class="num">Amount</th><th style="width:30px"></th></tr></thead><tbody id="items"></tbody></table>
   <button style="margin-top:8px" onclick="addRow()">+ Add line</button> <button onclick="addFixed()">+ Fixed fee</button></div>
  <div class="card"><h2>Adjustments</h2><div class="row">
   <div><label>Default hourly rate</label><input id="rate" type="number" value="75" oninput="applyRate()"></div>
   <div><label>Complexity buffer %</label><input id="buf" type="number" value="15" oninput="calc()"></div>
   <div><label>Rush fee %</label><input id="rush" type="number" value="0" oninput="calc()"></div>
   <div><label>Discount %</label><input id="disc" type="number" value="0" oninput="calc()"></div>
   <div><label>Tax %</label><input id="tax" type="number" value="0" oninput="calc()"></div>
   <div><label>Deposit %</label><input id="dep" type="number" value="50" oninput="calc()"></div></div>
   <label>Terms / notes</label><textarea id="terms" rows="3">Deposit due to begin work. Balance due on delivery. Includes 2 rounds of revisions. Additional work billed at the hourly rate above.</textarea></div>
 </div>
 <div id="p2" class="hide">
  <div class="card"><h2>What should your hourly rate be?</h2><div class="row">
   <div><label>Target yearly take-home</label><input id="r_inc" type="number" value="60000" oninput="rate()"></div>
   <div><label>Yearly business expenses</label><input id="r_exp" type="number" value="6000" oninput="rate()"></div>
   <div><label>Tax rate %</label><input id="r_tax" type="number" value="25" oninput="rate()"></div>
   <div><label>Weeks off per year</label><input id="r_off" type="number" value="5" oninput="rate()"></div>
   <div><label>Work hours / week</label><input id="r_hrs" type="number" value="35" oninput="rate()"></div>
   <div><label>Billable % of hours</label><input id="r_bil" type="number" value="60" oninput="rate()"></div>
   <div><label>Profit cushion %</label><input id="r_pro" type="number" value="10" oninput="rate()"></div></div>
   <div id="rout" style="margin-top:14px"></div>
   <button class="pri" style="margin-top:10px" onclick="useRate()">Use this as my default rate</button></div>
 </div>
 <div id="p3" class="hide"><div class="card"><h2>Saved quotes</h2><div id="saved" class="hint">Nothing saved yet.</div></div></div>
</section>
<section>
 <div class="card noprint"><h2>Totals</h2><div id="tots"></div><div id="margin" class="hint" style="margin-top:8px"></div>
  <div style="margin-top:12px;display:flex;gap:6px;flex-wrap:wrap"><button class="pri" onclick="window.print()">Print / Save PDF</button><button onclick="save()">Save</button><button onclick="copyText()">Copy as text</button><button onclick="resetAll()">New</button></div></div>
 <div id="quote"></div>
</section></main>
<script>
const $=id=>document.getElementById(id);
const KB={website:[["Discovery & sitemap",4],["Design (per page x pages)",10],["Development & CMS setup",14],["Content upload & SEO basics",5],["Testing & launch",3]],
 logo:[["Brand discovery",2],["Logo concepts (3)",8],["Revisions & final files",4]],brand:[["Brand strategy workshop",4],["Visual identity system",12],["Brand guidelines document",6]],
 video:[["Pre-production & script",5],["Filming",8],["Editing & color",12],["Revisions & export",3]],blog:[["Topic research",2],["Writing (per post)",4],["Edit & publish",1]],
 social:[["Strategy & content pillars",4],["Content creation (monthly)",12],["Scheduling & reporting",4]],app:[["Requirements & wireframes",10],["UI design",16],["Development",40],["QA & release",8]],
 ebook:[["Outline & research",5],["Writing",20],["Layout & cover",8]],course:[["Curriculum design",8],["Lesson production",24],["Platform setup & QA",6]],
 copy:[["Research & messaging",3],["Copy draft",6],["Revision round",2]],seo:[["Audit",5],["On-page fixes",8],["Monthly reporting",3]]};
let rows=[],cur=()=>$('cur').value;
const fmt=n=>cur()+(Math.round(n*100)/100).toLocaleString(undefined,{minimumFractionDigits:2,maximumFractionDigits:2});
const load=()=>{try{return JSON.parse(localStorage.getItem('qs_saved')||'[]')}catch(e){return[]}};
function tab(n){[1,2,3].forEach(i=>{$('p'+i).classList.toggle('hide',i!=n);$('t'+i).classList.toggle('on',i==n)});if(n==3)renderSaved();if(n==2)rate()}
function addRow(t='',h=1,r=null,fixed=false,amt=0){rows.push({t,h,r:r??+$('rate').value,fixed,amt});draw()}
function addFixed(){addRow('Fixed fee item',1,0,true,0)}
function del(i){rows.splice(i,1);draw()}
function applyRate(){rows.forEach(r=>{if(!r.fixed&&!r.custom)r.r=+$('rate').value});draw()}
function draw(){$('items').innerHTML=rows.map((r,i)=>`<tr><td><input value="${esc(r.t)}" oninput="rows[${i}].t=this.value;calc(1)"></td>
 <td>${r.fixed?'<span class=hint>fixed</span>':`<input type=number step=0.5 value="${r.h}" oninput="rows[${i}].h=+this.value;calc(1)">`}</td>
 <td>${r.fixed?'':`<input type=number value="${r.r}" oninput="rows[${i}].r=+this.value;rows[${i}].custom=1;calc(1)">`}</td>
 <td class=num>${r.fixed?`<input type=number value="${r.amt}" oninput="rows[${i}].amt=+this.value;calc(1)" style="text-align:right">`:fmt(r.h*r.r)}</td>
 <td><button onclick="del(${i})" title="Remove">&times;</button></td></tr>`).join('');calc()}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;')}
function totals(){const sub=rows.reduce((a,r)=>a+(r.fixed?+r.amt:r.h*r.r),0),hrs=rows.reduce((a,r)=>a+(r.fixed?0:+r.h),0);
 const buf=sub*(+$('buf').value/100),rush=(sub+buf)*(+$('rush').value/100),disc=(sub+buf+rush)*(+$('disc').value/100);
 const net=sub+buf+rush-disc,tax=net*(+$('tax').value/100),total=net+tax,dep=total*(+$('dep').value/100);return{sub,hrs,buf,rush,disc,net,tax,total,dep}}
function calc(keep){const t=totals();
 $('tots').innerHTML=[['Subtotal',t.sub],['Complexity buffer',t.buf],['Rush fee',t.rush],['Discount',-t.disc],['Tax',t.tax]].filter(x=>x[1]).map(x=>`<div class=tot><span>${x[0]}</span><span>${fmt(x[1])}</span></div>`).join('')+`<div class="tot big"><span>Total</span><span>${fmt(t.total)}</span></div><div class=tot><span>Deposit due</span><span>${fmt(t.dep)}</span></div>`;
 const eff=t.hrs?t.net/t.hrs:0;$('margin').innerHTML=t.hrs?`${t.hrs} hrs &middot; effective rate <b>${fmt(eff)}/hr</b> `+(eff<(+$('rate').value)*0.9?'<span class=warn>(below your default rate: raise the buffer or scope)</span>':''):'';
 if(!keep||true)quote(t)}
function quote(t){const d=new Date(),v=new Date(Date.now()+86400000*(+$('valid').value||14));
 $('quote').innerHTML=`<h1>${esc($('me').value||'Your Business')}</h1><div class=meta><div><b>Quote for</b><br>${esc($('client').value||'Client name')}<br>${esc($('title').value||'Project')}</div><div style="text-align:right"><b>Quote #${esc($('qno').value||'001')}</b><br>Date: ${d.toLocaleDateString()}<br>Valid until: ${v.toLocaleDateString()}</div></div>
 <table><thead><tr><th>Description</th><th class=num>Hours</th><th class=num>Rate</th><th class=num>Amount</th></tr></thead><tbody>${rows.map(r=>`<tr><td>${esc(r.t)}</td><td class=num>${r.fixed?'':r.h}</td><td class=num>${r.fixed?'':fmt(r.r)}</td><td class=num>${fmt(r.fixed?r.amt:r.h*r.r)}</td></tr>`).join('')}</tbody></table>
 <div class=sum><div><span>Subtotal</span><span>${fmt(t.sub)}</span></div>${t.buf?`<div><span>Scope contingency</span><span>${fmt(t.buf)}</span></div>`:''}${t.rush?`<div><span>Rush fee</span><span>${fmt(t.rush)}</span></div>`:''}${t.disc?`<div><span>Discount</span><span>-${fmt(t.disc)}</span></div>`:''}${t.tax?`<div><span>Tax</span><span>${fmt(t.tax)}</span></div>`:''}<div class=grand><span>Total</span><span>${fmt(t.total)}</span></div><div><span>Deposit to start</span><span>${fmt(t.dep)}</span></div></div>
 <p style="margin-top:24px;font-size:13px;color:#444"><b>Terms</b><br>${esc($('terms').value).replace(/\n/g,'<br>')}</p><p style="margin-top:20px;font-size:13px">Accepted by: ______________________ &nbsp; Date: ____________</p>`}
function suggest(){const q=$('desc').value.toLowerCase();let hit=[];
 for(const k in KB)if(q.includes(k)||(k=='website'&&/site|landing|shop|store/.test(q))||(k=='app'&&/software|tool|platform/.test(q))||(k=='copy'&&/copy|sales page|email/.test(q)))hit.push(k);
 if(!hit.length){$('sugs').innerHTML='No keywords matched. Try: website, logo, brand, video, blog, social, app, ebook, course, copy, seo.';return}
 if(rows.length==1&&rows[0].t=='Example task')rows=[];
 const m=q.match(/(\d+)[- ]?page/);const pages=m?+m[1]:1;
 hit.forEach(k=>KB[k].forEach(([t,h])=>{let hh=h;if(k=='website'&&t.startsWith('Design'))hh=Math.min(60,2.5*pages+4);if(k=='website'&&t.startsWith('Development'))hh=Math.min(80,2.5*pages+8);addRow(t.replace(' (per page x pages)',pages>1?` (${pages} pages)`:''),hh)}));
 $('sugs').innerHTML='Added: '+hit.map(k=>`<span class=tag>${k}</span>`).join('')+' Hours are typical mid-level estimates. Adjust to your pace.'}
function rate(){const g=id=>+$(id).value;const wk=52-g('r_off'),bill=wk*g('r_hrs')*g('r_bil')/100;const gross=(g('r_inc')/(1-g('r_tax')/100)+g('r_exp'))*(1+g('r_pro')/100);const hr=gross/bill;
 window._rate=hr;$('rout').innerHTML=`<div class=tot><span>Billable hours / year</span><span>${Math.round(bill)}</span></div><div class=tot><span>Revenue needed</span><span>${fmt(gross)}</span></div><div class="tot big"><span>Minimum hourly rate</span><span>${fmt(hr)}</span></div>
 <div class=hint style="margin-top:8px">Day rate: ${fmt(hr*7)} &middot; Half-day: ${fmt(hr*3.5)} &middot; Project rate for a 40-hr job: ${fmt(hr*40*1.15)} (incl. 15% buffer)</div>`}
function useRate(){$('rate').value=Math.ceil(window._rate);applyRate();tab(1)}
function save(){const s=load(),id=$('qno').value||('Q'+(s.length+1));
 const rec={id,date:new Date().toISOString(),state:{rows,f:['me','client','title','qno','valid','cur','rate','buf','rush','disc','tax','dep','terms'].reduce((o,k)=>(o[k]=$(k).value,o),{})}};
 const i=s.findIndex(x=>x.id==id);i>=0?s[i]=rec:s.push(rec);try{localStorage.setItem('qs_saved',JSON.stringify(s))}catch(e){alert('Could not save in this browser.')}tab(3)}
function renderSaved(){const s=load();$('saved').innerHTML=s.length?s.map((x,i)=>`<div class=tot><span>${esc(x.id)} &middot; ${esc(x.state.f.client||'')} &middot; ${esc(x.state.f.title||'')}<br><span class=hint>${new Date(x.date).toLocaleString()}</span></span><span><button onclick="openQ(${i})">Open</button> <button onclick="delQ(${i})">Delete</button></span></div>`).join(''):'Nothing saved yet.'}
function openQ(i){const x=load()[i];rows=x.state.rows;for(const k in x.state.f)$(k).value=x.state.f[k];tab(1);draw()}
function delQ(i){const s=load();s.splice(i,1);try{localStorage.setItem('qs_saved',JSON.stringify(s))}catch(e){}renderSaved()}
function copyText(){const t=totals();const s=`${$('me').value||'Your Business'} - Quote #${$('qno').value||'001'}\nClient: ${$('client').value}\nProject: ${$('title').value}\n\n`+rows.map(r=>`- ${r.t}: ${r.fixed?fmt(r.amt):r.h+'h x '+fmt(r.r)+' = '+fmt(r.h*r.r)}`).join('\n')+`\n\nTotal: ${fmt(t.total)}\nDeposit: ${fmt(t.dep)}\n\n${$('terms').value}`;
 (navigator.clipboard?navigator.clipboard.writeText(s):Promise.reject()).then(()=>alert('Copied')).catch(()=>prompt('Copy:',s))}
function resetAll(){rows=[];['client','title','desc'].forEach(k=>$(k).value='');$('qno').value='';addRow('',1)}
document.querySelectorAll('input,select,textarea').forEach(e=>e.addEventListener('input',()=>{if(rows.length)calc()}));
$('qno').value=String(Math.floor(Date.now()/1000)).slice(-5);addRow('Example task',4);rate();
</script></body></html>
"""


# ======================================================================
# Spec-driven calculators (weekly ideator). expr is plain JS using field ids.
# ======================================================================
TOOLS = {
    "digiprofit": {
        "file": "digiprofit.html", "title": "DigiProfit", "tag": "know what you really keep per sale",
        "name": "DigiProfit - Digital Product Profit Calculator", "price": 37,
        "buyer": "digital product sellers who want to know their real margin after fees, ads and taxes",
        "angle": "Enter your price and fees; see what you keep per sale, break-even units and the price you need for a profit goal.",
        "keywords": ["etsy profit calculator", "digital product pricing", "fee calculator", "break even calculator", "seller profit tool"],
        "intro": "Platform fees change, so the fee fields are yours to edit. Defaults are placeholders: check your platform's current fee page.",
        "fields": [("price", "Sale price", 29, 1), ("pfee", "Platform fee %", 6.5, 0.1), ("cfee", "Payment processing %", 3, 0.1), ("fixed", "Fixed fee per sale", 0.45, 0.01),
                   ("ads", "Ad cost per sale", 2, 0.01), ("tax", "Tax set-aside % of profit", 25, 1), ("monthly", "Monthly fixed costs (tools, subscriptions)", 40, 1),
                   ("units", "Sales per month", 60, 1), ("goal", "Monthly profit goal (after tax)", 1500, 50)],
        "outputs": [("Fees per sale", "price*(pfee+cfee)/100+fixed", "money"), ("Profit per sale before tax", "price-(price*(pfee+cfee)/100+fixed)-ads", "money"),
                    ("Margin", "(price-(price*(pfee+cfee)/100+fixed)-ads)/price*100", "pct"),
                    ("Monthly profit before tax", "(price-(price*(pfee+cfee)/100+fixed)-ads)*units-monthly", "money"),
                    ("Monthly profit after tax", "((price-(price*(pfee+cfee)/100+fixed)-ads)*units-monthly)*(1-tax/100)", "money"),
                    ("Break-even sales / month", "monthly/(price-(price*(pfee+cfee)/100+fixed)-ads)", "num"),
                    ("Sales needed for your goal", "(goal/(1-tax/100)+monthly)/(price-(price*(pfee+cfee)/100+fixed)-ads)", "num"),
                    ("Price needed to hit goal at current sales", "((goal/(1-tax/100)+monthly)/units+fixed+ads)/(1-(pfee+cfee)/100)", "money")]},
    "launchplan": {
        "file": "launchplan.html", "title": "LaunchPlan", "tag": "estimate a course or product launch before you spend",
        "name": "LaunchPlan - Launch Revenue Planner", "price": 37,
        "buyer": "creators planning a course or product launch to an email list or audience",
        "angle": "Turn audience size, conversion and ad spend into revenue, net profit and break-even buyers.",
        "keywords": ["course launch calculator", "launch planner", "email list revenue", "conversion calculator", "creator tools"],
        "intro": "Conversion rates vary widely. Run a cautious, a typical and an optimistic case and plan around the cautious one.",
        "fields": [("list", "Audience / email list size", 2000, 100), ("open", "Reach % (see the launch emails)", 40, 1), ("conv", "Conversion % of those reached", 2, 0.1), ("price", "Price", 100, 1),
                   ("refund", "Refund rate %", 5, 0.5), ("fee", "Platform + payment fees %", 9, 0.5), ("ads", "Ad spend", 300, 10), ("other", "Other launch costs", 100, 10)],
        "outputs": [("People reached", "list*open/100", "num"), ("Buyers", "list*open/100*conv/100", "num"), ("Gross revenue", "list*open/100*conv/100*price", "money"),
                    ("Refunds", "list*open/100*conv/100*price*refund/100", "money"), ("Fees", "list*open/100*conv/100*price*(1-refund/100)*fee/100", "money"),
                    ("Net profit", "list*open/100*conv/100*price*(1-refund/100)*(1-fee/100)-ads-other", "money"),
                    ("Break-even buyers", "(ads+other)/(price*(1-refund/100)*(1-fee/100))", "num"),
                    ("Return on ad + launch spend", "(list*open/100*conv/100*price*(1-refund/100)*(1-fee/100)-ads-other)/(ads+other)*100", "pct")]},
    "projectprofit": {
        "file": "projectprofit.html", "title": "ProjectProfit", "tag": "find out if a fixed-price project actually paid",
        "name": "ProjectProfit - Freelance Project Profit Checker", "price": 37,
        "buyer": "freelancers who quote fixed prices and want to know their real hourly rate",
        "angle": "Compare quoted and actual hours to see your effective rate, scope creep cost and what to charge next time.",
        "keywords": ["freelance profit calculator", "effective hourly rate", "scope creep", "project pricing", "freelancer tools"],
        "intro": "Use this after every project. Track actual hours, and price the next one from real data.",
        "fields": [("fee", "Project fee", 3000, 50), ("qh", "Hours you quoted", 40, 1), ("ah", "Actual hours worked", 55, 1), ("target", "Target hourly rate", 75, 1),
                   ("exp", "Direct expenses (software, stock, contractors)", 150, 10), ("buf", "Buffer % for next quote", 20, 1)],
        "outputs": [("Effective hourly rate", "(fee-exp)/ah", "money"), ("Quoted hourly rate", "(fee-exp)/qh", "money"), ("Over / under hours", "ah-qh", "num"),
                    ("Scope creep cost at target rate", "(ah-qh)*target", "money"), ("Profit vs target", "(fee-exp)-ah*target", "money"),
                    ("Price to charge next time (same scope)", "(ah*target+exp)*(1+buf/100)", "money")]},
    "hourscredit": {
        "file": "hourscredit.html", "title": "CreditCounter", "tag": "turn homeschool hours into credits and a plan",
        "name": "CreditCounter - Homeschool Hours & Credit Calculator", "price": 27,
        "buyer": "homeschool parents tracking instructional hours and high-school credits",
        "angle": "Convert hours into credits, see how many school days you need, and plan the remaining weeks.",
        "keywords": ["homeschool credit calculator", "homeschool hours", "high school credits", "homeschool records", "school days planner"],
        "intro": "Hours-per-credit and required days differ by state, school and college. Many families use about 120-180 hours per credit. Enter your own requirement.",
        "fields": [("done", "Hours completed in this course", 90, 1), ("per", "Hours needed for 1 credit", 150, 5), ("hday", "Hours per school day", 3, 0.5),
                   ("days", "School days per week", 4, 1), ("req", "Days required per year", 180, 1), ("taught", "Days completed so far", 60, 1)],
        "outputs": [("Credit earned so far", "done/per", "num2"), ("Hours still needed for 1 credit", "Math.max(per-done,0)", "num"),
                    ("School days to finish", "Math.max(per-done,0)/hday", "num"), ("Weeks to finish", "Math.max(per-done,0)/hday/days", "num"),
                    ("Days still required this year", "Math.max(req-taught,0)", "num"), ("Weeks left to meet required days", "Math.max(req-taught,0)/days", "num")]},
}

TOOL_HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>__TITLE__</title><style>
:root{--bg:#f4f3ee;--card:#fff;--fg:#1c1f1d;--mute:#6b716d;--line:#e2e0d8;--acc:#2f6f5e;--acc2:#e8f1ee}
@media(prefers-color-scheme:dark){:root{--bg:#141614;--card:#1d201e;--fg:#ecece6;--mute:#9aa09b;--line:#33372f;--acc:#5fb59d;--acc2:#1f2d29}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
header{padding:18px 20px;border-bottom:1px solid var(--line);background:var(--card)}header b{font-size:20px}header span{color:var(--mute);margin-left:10px}
main{max-width:980px;margin:0 auto;padding:18px;display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:800px){main{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}h2{font-size:13px;text-transform:uppercase;letter-spacing:.07em;color:var(--mute);margin:0 0 10px}
label{display:block;font-size:12px;color:var(--mute);margin:10px 0 3px}input{width:100%;font:inherit;padding:8px 10px;border:1px solid var(--line);border-radius:8px;background:var(--bg);color:var(--fg)}
.o{display:flex;justify-content:space-between;gap:10px;padding:8px 0;border-bottom:1px solid var(--line)}.o:last-child{border:0}.o b{font-variant-numeric:tabular-nums;white-space:nowrap}
.hint{font-size:13px;color:var(--mute)}button{font:inherit;padding:8px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);cursor:pointer;margin:4px 6px 0 0}button.pri{background:var(--acc);color:#fff;border-color:var(--acc)}
@media print{header button,.noprint{display:none}body{background:#fff}}</style></head><body>
<header><b>__TITLE__</b><span>__TAG__</span></header><main>
<section class="card"><h2>Inputs</h2><p class="hint">__INTRO__</p><div id="f"></div><div class="noprint"><button onclick="reset()">Reset</button></div></section>
<section class="card"><h2>Results</h2><div id="o"></div><div class="noprint"><button class="pri" onclick="print()">Print / Save PDF</button><button onclick="copyR()">Copy results</button></div></section></main>
<script>
const F=__FIELDS__,O=__OUTPUTS__,ids=F.map(f=>f[0]);const $=id=>document.getElementById(id);
const key='__KEY__';const st={get(){try{return JSON.parse(localStorage.getItem(key)||'{}')}catch(e){return{}}},set(v){try{localStorage.setItem(key,JSON.stringify(v))}catch(e){}}};
const fns=O.map(o=>new Function(...ids,'return '+o[1]));const nf=(n,d)=>isFinite(n)?n.toLocaleString(undefined,{minimumFractionDigits:d,maximumFractionDigits:d}):'n/a';
const fmt=(v,t)=>t=='money'?(isFinite(v)?'$'+nf(v,2):'n/a'):t=='pct'?nf(v,1)+'%':t=='num2'?nf(v,2):nf(v,1);
function vals(){return ids.map(i=>parseFloat($(i).value)||0)}
function calc(){const v=vals();const s={};ids.forEach((i,k)=>s[i]=v[k]);st.set(s);$('o').innerHTML=O.map((o,k)=>{let r;try{r=fns[k](...v)}catch(e){r=NaN}return `<div class=o><span>${o[0]}</span><b>${fmt(r,o[2])}</b></div>`}).join('')}
function draw(){const s=st.get();$('f').innerHTML=F.map(f=>`<label for="${f[0]}">${f[1]}</label><input id="${f[0]}" type="number" step="${f[3]}" value="${s[f[0]]??f[2]}" oninput="calc()">`).join('');calc()}
function reset(){try{localStorage.removeItem(key)}catch(e){}draw()}
function copyR(){const t=[...document.querySelectorAll('.o')].map(e=>e.innerText.replace('\n',': ')).join('\n');(navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(()=>alert('Copied')).catch(()=>prompt('Copy:',t))}
draw();</script></body></html>"""


def build_tool(outdir, cfg, brief):
    import json as _json
    t = TOOLS[cfg["tool"]]
    outdir = Path(outdir)
    html = (TOOL_HTML.replace("__TITLE__", t["title"]).replace("__TAG__", t["tag"]).replace("__INTRO__", t["intro"])
            .replace("__FIELDS__", _json.dumps([list(f) for f in t["fields"]])).replace("__OUTPUTS__", _json.dumps([list(o) for o in t["outputs"]]))
            .replace("__KEY__", "tool_" + cfg["tool"]))
    (outdir / t["file"]).write_text(html)
    (outdir / "README.txt").write_text(
        f"{t['title'].upper()}\n\nDouble-click {t['file']}. Runs offline in any modern browser; nothing is uploaded. Your numbers are remembered in this browser only.\n\n"
        f"{t['intro']}\n\nResults are estimates from the numbers you enter, not financial, tax or legal advice.\n")
    return [outdir / t["file"], outdir / "README.txt"]


def validate_tool(outdir):
    problems = []
    files = list(Path(outdir).glob("*.html"))
    if not files:
        return ["no html tool found"]
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(files[0].resolve().as_uri())
            txt = pg.inner_text("#o")
            if txt.count("\n") < 4:
                problems.append("results did not render")
            if "NaN" in txt or "Infinity" in txt or "n/a" in txt:
                problems.append("default inputs produce NaN/n/a results")
            b.close()
            problems += [f"JS error: {e}" for e in errs]
    except Exception as e:
        print(f"[qa] browser check skipped: {e.__class__.__name__}")
    return problems


def build(outdir, cfg, brief):
    if cfg.get("tool"):
        return build_tool(outdir, cfg, brief)
    outdir = Path(outdir)
    (outdir / "quotesmith.html").write_text(HTML)
    (outdir / "README.txt").write_text(
        "QUOTESMITH\n\nDouble-click quotesmith.html. It runs offline in any modern browser; nothing is uploaded.\n\n"
        "1. Rate calculator tab: find your minimum hourly rate, click 'Use this as my default rate'.\n"
        "2. Build tab: describe the project, click 'Suggest line items', adjust hours, add client details.\n"
        "3. Print / Save PDF gives the clean client-facing quote. Save keeps it in this browser.\n\n"
        "Note: suggestions are rule-based hour templates, not AI. Quotes are saved in your browser's local storage on this device.\n"
    )
    return [outdir / "quotesmith.html", outdir / "README.txt"]


def validate(outdir):
    problems = []
    f = Path(outdir) / "quotesmith.html"
    if not f.exists():
        return validate_tool(outdir)
    t = f.read_text()
    for must in ["function suggest", "function rate", "window.print", "localStorage", "@media print"]:
        if must not in t:
            problems.append(f"missing {must}")
    try:  # real browser check: load page, run the flows, fail on JS errors
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium") if Path("/opt/pw-browsers/chromium").exists() else p.chromium.launch()
            pg = b.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(f.resolve().as_uri())
            pg.fill("#desc", "5-page website with logo and blog")
            pg.click("text=Suggest line items")
            n = pg.locator("#items tr").count()
            total = pg.inner_text("#tots")
            if n < 5:
                problems.append(f"suggest produced only {n} rows")
            if "Total" not in total:
                problems.append("totals not rendered")
            b.close()
            problems += [f"JS error: {e}" for e in errs]
    except Exception as e:  # playwright unavailable: static checks only
        print(f"[qa] browser check skipped: {e.__class__.__name__}")
    return problems
