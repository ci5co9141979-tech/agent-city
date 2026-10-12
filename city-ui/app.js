/* ============================================================
   AGENT CITY — interactive city engine
   Canvas 2.5D city. Click buildings, run weekly episodes.
   No dependencies. Data comes from city-data.js.
   ============================================================ */
(() => {
"use strict";

const D      = window.CITY_DATA;
const LIVE   = window.CITY_STATE || null;   // written by the Monday workflow (state.js)
const cvs    = document.getElementById("city");
const ctx    = cvs.getContext("2d");
const $      = (id) => document.getElementById(id);
const clamp  = (v, a, b) => Math.max(a, Math.min(b, v));
const wait   = (ms) => new Promise((r) => setTimeout(r, ms));

let W = 0, H = 0, DPR = 1, TILE = 48;
const cam = { x: 0, y: 0, zoom: 1 };
const N = D.gridSize;
const S = () => cam.zoom;
const SX = (wx) => wx * cam.zoom + cam.x;
const SY = (wy) => wy * cam.zoom + cam.y;

/* ---------------- palette ---------------- */
let night = true;
function pal() {
  return night
    ? { grass1:"#17213c", grass2:"#131b32", road:"#242e4c", roadEdge:"rgba(120,150,220,.30)",
        line:"#55659a", winOn:"#ffd782", winOff:"rgba(255,255,255,.06)", label:"#aab7e2",
        shadow:"rgba(0,0,0,.50)", haze:"rgba(110,168,254,.18)", stars:true }
    : { grass1:"#2c4270", grass2:"#263a63", road:"#414d70", roadEdge:"rgba(255,255,255,.28)",
        line:"#9fb0dd", winOn:"#fff4cc", winOff:"rgba(255,255,255,.16)", label:"#d3ddfb",
        shadow:"rgba(0,0,0,.32)", haze:"rgba(255,214,130,.22)", stars:false };
}

/* ---------------- color helpers ---------------- */
function hex2rgb(h) {
  h = h.replace("#", "");
  if (h.length === 3) h = h.split("").map((c) => c + c).join("");
  return [parseInt(h.slice(0,2),16), parseInt(h.slice(2,4),16), parseInt(h.slice(4,6),16)];
}
function mix(hex, to, amt) {
  const [r,g,b] = hex2rgb(hex), t = to === "white" ? 255 : 0;
  const f = (c) => Math.round(c + (t - c) * amt);
  return `rgb(${f(r)},${f(g)},${f(b)})`;
}
function rgba(hex, a) { const [r,g,b] = hex2rgb(hex); return `rgba(${r},${g},${b},${a})`; }
function hash(str) { let h = 2166136261; for (let i=0;i<str.length;i++){ h ^= str.charCodeAt(i); h = Math.imul(h, 16777619); } return (h>>>0)/4294967296; }

/* ---------------- layout ---------------- */
function layout() {
  W = window.innerWidth; H = window.innerHeight;
  DPR = Math.min(window.devicePixelRatio || 1, 2);
  cvs.width = Math.round(W * DPR); cvs.height = Math.round(H * DPR);
  cvs.style.width = W + "px"; cvs.style.height = H + "px";
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  TILE = clamp(Math.min(W / (N + 1.8), H / (N + 2.6)), 15, 76);
  recenter();
  makeStars();
}
function recenter() {
  const world = N * TILE;
  cam.x = W / 2 - (world * cam.zoom) / 2;
  cam.y = H / 2 - (world * cam.zoom) / 2 + H * 0.02;
}
window.addEventListener("resize", layout);

/* ---------------- atmosphere ---------------- */
let stars = [];
function makeStars() {
  stars = Array.from({ length: 90 }, () => ({
    x: Math.random(), y: Math.random() * 0.75,
    r: Math.random() * 1.3 + 0.3, a: Math.random() * 0.6 + 0.2,
    p: Math.random() * Math.PI * 2
  }));
}
let particles = [];

/* ---------------- building geometry ---------------- */
const padOf   = () => TILE * 0.10;
const skewOf  = () => TILE * 0.17;
const heightOf = (b) => b.height * (TILE / 68);

function box(b) {
  const pad = padOf(), skew = skewOf(), h = heightOf(b);
  const px = b.tile[0] * TILE + pad;
  const py = b.tile[1] * TILE + pad;
  const pw = TILE - pad * 2;
  const ph = TILE - pad * 2;
  return { px, py, pw, ph, h, skew, topY: py - h, cx: px + pw / 2 + skew / 2, cy: py + ph / 2 - h / 2 };
}

/* ---------------- deterministic noise ---------------- */
function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/* ---------------- draw: sky ---------------- */
function zSky() {
  const grd = ctx.createLinearGradient(0, 0, 0, H);
  if (night) { grd.addColorStop(0, "#05070f"); grd.addColorStop(0.5, "#0a0f1f"); grd.addColorStop(1, "#070a15"); }
  else       { grd.addColorStop(0, "#1c2848"); grd.addColorStop(0.5, "#26355f"); grd.addColorStop(1, "#1b2540"); }
  ctx.fillStyle = grd; ctx.fillRect(0, 0, W, H);

  if (pal().stars) {
    const t = performance.now() / 1400;
    for (const s of stars) {
      const tw = 0.55 + 0.45 * Math.sin(t + s.p);
      ctx.globalAlpha = s.a * tw * 0.9;
      ctx.fillStyle = "#dce7ff";
      ctx.beginPath(); ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2); ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  // soft aurora glow behind the city
  const cx = W / 2, cy = H / 2;
  const g2 = ctx.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W, H) * 0.55);
  g2.addColorStop(0, night ? "rgba(96,132,255,.16)" : "rgba(255,214,140,.22)");
  g2.addColorStop(0.6, night ? "rgba(80,110,220,.05)" : "rgba(255,200,120,.06)");
  g2.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = g2; ctx.fillRect(0, 0, W, H);
}

/* ---------------- draw: the city plate ---------------- */
function zPlate() {
  const P = pal();
  const Z = S();
  const x0 = SX(0), y0 = SY(0), s = N * TILE * Z;
  const rr = TILE * Z * 0.5;

  ctx.save();
  ctx.shadowColor = "rgba(0,0,0,.70)";
  ctx.shadowBlur = 70 * Z; ctx.shadowOffsetY = 26 * Z;
  ctx.fillStyle = P.grass2;
  roundRect(x0, y0, s, s, rr); ctx.fill();
  ctx.restore();

  ctx.save();
  roundRect(x0, y0, s, s, rr); ctx.clip();

  // terrain mottling
  const rnd = mulberry32(7);
  for (let i = 0; i < 26; i++) {
    const bx = x0 + rnd() * s, by = y0 + rnd() * s, br = (0.6 + rnd() * 1.5) * TILE * Z;
    const g = ctx.createRadialGradient(bx, by, 0, bx, by, br);
    g.addColorStop(0, night ? "rgba(120,160,255,.055)" : "rgba(255,255,255,.07)");
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(bx, by, br, 0, Math.PI * 2); ctx.fill();
  }
  // faint checker to help you read the grid without it shouting
  for (let gy = 0; gy < N; gy++) for (let gx = 0; gx < N; gx++) {
    if ((gx + gy) % 2) continue;
    ctx.fillStyle = night ? "rgba(255,255,255,.018)" : "rgba(255,255,255,.035)";
    ctx.fillRect(SX(gx * TILE), SY(gy * TILE), TILE * Z + 0.6, TILE * Z + 0.6);
  }

  // ---- roads ----
  const R = D.roads;
  const rx = SX(R.cols[0] * TILE), rw = R.cols.length * TILE * Z;
  const ry = SY(R.rows[0] * TILE), rh = R.rows.length * TILE * Z;
  ctx.fillStyle = P.road;
  ctx.fillRect(x0, ry, s, rh);
  ctx.fillRect(rx, y0, rw, s);

  // curbs
  ctx.strokeStyle = P.roadEdge; ctx.lineWidth = Math.max(1, 1.1 * Z);
  ctx.strokeRect(x0, ry, s, rh);
  ctx.strokeRect(rx, y0, rw, s);

  // centre dashes
  ctx.save();
  ctx.setLineDash([Math.max(5, TILE * Z * 0.26), Math.max(6, TILE * Z * 0.28)]);
  ctx.lineWidth = Math.max(1.2, 1.9 * Z);
  ctx.strokeStyle = P.line; ctx.globalAlpha = night ? 0.6 : 0.8;
  const midY = ry + rh / 2, midX = rx + rw / 2;
  ctx.beginPath(); ctx.moveTo(x0, midY); ctx.lineTo(x0 + s, midY); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(midX, y0); ctx.lineTo(midX, y0 + s); ctx.stroke();
  ctx.restore();

  // crossroads glow
  const g = ctx.createRadialGradient(midX, midY, 0, midX, midY, TILE * Z * 3.2);
  g.addColorStop(0, P.haze); g.addColorStop(1, "rgba(0,0,0,0)");
  ctx.fillStyle = g; ctx.fillRect(midX - TILE * 3.2 * Z, midY - TILE * 3.2 * Z, TILE * 6.4 * Z, TILE * 6.4 * Z);

  ctx.restore();

  // plate rim
  ctx.save();
  ctx.strokeStyle = night ? "rgba(120,165,255,.30)" : "rgba(255,255,255,.35)";
  ctx.lineWidth = Math.max(1.2, 1.6 * Z);
  roundRect(x0, y0, s, s, rr); ctx.stroke();
  ctx.restore();
}
function roundRect(x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

/* ---------------- props: trees, houses, lamps, cars ---------------- */
let props = [];
let scene = [];

function makeProps() {
  props = [];
  const rnd = mulberry32(20261012);
  const R = D.roads;
  const isRoad = (gx, gy) => R.rows.includes(gy) || R.cols.includes(gx);
  // leave a clear plot (the tile itself, its 8 neighbours and the label row) around each named building
  const taken = new Set();
  for (const b of D.buildings) {
    for (let dy = -1; dy <= 2; dy++) for (let dx = -1; dx <= 1; dx++) {
      taken.add((b.tile[0] + dx) + ',' + (b.tile[1] + dy));
    }
  }
  const houseCols = ["#46527a", "#4d4468", "#3f5670", "#54607f", "#4a5a6b", "#585070"];

  for (let gy = 0; gy < N; gy++) {
    for (let gx = 0; gx < N; gx++) {
      if (isRoad(gx, gy) || taken.has(gx + ',' + gy)) continue;
      const roll = rnd();
      if (roll < 0.26) {
        props.push({ kind: "house", gx, gy, h: TILE * (0.18 + rnd() * 0.20),
                     color: houseCols[(rnd() * houseCols.length) | 0], lit: rnd() > 0.35 });
      } else if (roll < 0.50) {
        props.push({ kind: "tree", gx, gy, r: TILE * (0.15 + rnd() * 0.09), tone: rnd() });
      } else if (roll < 0.62) {
        props.push({ kind: "bush", gx, gy, r: TILE * (0.09 + rnd() * 0.06) });
      } else if (roll < 0.68) {
        props.push({ kind: "lamp", gx, gy });
      }
    }
  }
  // parked cars on the road, hugging a kerb
  const carCols = ["#c94f6d", "#4f9ec9", "#c9a24f", "#7ec94f", "#9a6ac9"];
  for (let i = 0; i < 7; i++) {
    const horiz = rnd() > 0.5;
    if (horiz) props.push({ kind: "car", gx: rnd() * (N - 1), gy: R.rows[0] - 0.12 + rnd() * 0.24, rot: 0, color: carCols[(rnd() * carCols.length) | 0] });
    else       props.push({ kind: "car", gx: R.cols[0] - 0.12 + rnd() * 0.24, gy: rnd() * (N - 1), rot: 1, color: carCols[(rnd() * carCols.length) | 0] });
  }
}

function buildScene() {
  scene = [];
  for (const b of D.buildings) scene.push({ t: 0, gy: b.tile[1], gx: b.tile[0], b, key: b.tile[1] + "|" + b.tile[0] + "|b" });
  for (const p of props)      scene.push({ t: 1, gy: Math.round(p.gy), gx: Math.round(p.gx), p, key: Math.round(p.gy) + "|" + Math.round(p.gx) + "|p" });
  // painter's algorithm: back-to-front by the bottom edge of each footprint
  scene.sort((a, b) => (sceneBot(a) - sceneBot(b)) || (a.gx - b.gx) || (a.t - b.t));
}
const sceneBot = (o) => o.gy + 1;

function drawProp(p) {
  const P = pal(); const Z = S();
  const x = (p.gx + 0.5) * TILE, y = (p.gy + 0.5) * TILE;

  if (p.kind === "tree") {
    const r = p.r * Z;
    ctx.fillStyle = "rgba(0,0,0,.35)";
    ctx.beginPath(); ctx.ellipse(SX(x + r * 0.35), SY(y + r * 0.35), r * 0.9, r * 0.42, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = "#4a3a2c";
    ctx.fillRect(SX(x) - r * 0.1, SY(y) - r * 0.5, r * 0.2, r * 0.7);
    const leaf = p.tone > 0.5
      ? (night ? ["#1f4a37", "#2b6a4b"] : ["#2c6b4a", "#3d8f63"])
      : (night ? ["#22453f", "#2f6b5c"] : ["#2f6b62", "#439183"]);
    ctx.fillStyle = leaf[0];
    ctx.beginPath(); ctx.arc(SX(x), SY(y) - r * 0.9, r, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = leaf[1];
    ctx.beginPath(); ctx.arc(SX(x) - r * 0.28, SY(y) - r * 1.15, r * 0.62, 0, Math.PI * 2); ctx.fill();
  } else if (p.kind === "bush") {
    const r = p.r * Z;
    ctx.fillStyle = night ? "#2a5348" : "#3a7361";
    ctx.beginPath(); ctx.arc(SX(x), SY(y), r, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = night ? "#33635a" : "#48907a";
    ctx.beginPath(); ctx.arc(SX(x) - r * 0.3, SY(y) - r * 0.25, r * 0.6, 0, Math.PI * 2); ctx.fill();
  } else if (p.kind === "lamp") {
    const h = TILE * Z * 0.52;
    ctx.strokeStyle = night ? "#4a5680" : "#6b7699"; ctx.lineWidth = Math.max(1, Z * 1.4);
    ctx.beginPath(); ctx.moveTo(SX(x), SY(y)); ctx.lineTo(SX(x), SY(y) - h); ctx.stroke();
    const bulb = night ? "#ffd782" : "#fff2cc";
    ctx.save();
    if (night) {
      const g = ctx.createRadialGradient(SX(x), SY(y) - h, 0, SX(x), SY(y) - h, TILE * Z * 0.72);
      g.addColorStop(0, "rgba(255,215,130,.55)"); g.addColorStop(1, "rgba(255,215,130,0)");
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(SX(x), SY(y) - h, TILE * Z * 0.72, 0, Math.PI * 2); ctx.fill();
    }
    ctx.fillStyle = bulb;
    ctx.beginPath(); ctx.arc(SX(x), SY(y) - h, Math.max(1.4, Z * 2.2), 0, Math.PI * 2); ctx.fill();
    ctx.restore();
  } else if (p.kind === "car") {
    const Z2 = Z, w = TILE * 0.26 * Z2, l = TILE * 0.50 * Z2;
    ctx.save();
    ctx.translate(SX(x), SY(y));
    if (p.rot) ctx.rotate(Math.PI / 2);
    ctx.fillStyle = "rgba(0,0,0,.4)";
    ctx.beginPath(); ctx.ellipse(0, 2 * Z2, l * 0.5, w * 0.42, 0, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = p.color;
    roundRect(-l / 2, -w / 2, l, w, Math.max(2, w * 0.32)); ctx.fill();
    ctx.fillStyle = "rgba(255,255,255,.30)";
    roundRect(-l * 0.14, -w / 2 + w * 0.14, l * 0.34, w * 0.72, Math.max(1.5, w * 0.2)); ctx.fill();
    ctx.restore();
  } else if (p.kind === "house") {
    const pad = TILE * 0.16, skew = TILE * 0.10;
    const px = p.gx * TILE + pad, py = p.gy * TILE + pad;
    const pw = TILE - pad * 2, ph = TILE - pad * 2, h = p.h;
    ctx.fillStyle = "rgba(0,0,0,.22)";
    ctx.beginPath(); ctx.ellipse(SX(px + pw / 2 + skew / 2), SY(py + ph), pw * 0.50 * Z, ph * 0.26 * Z, 0, 0, Math.PI * 2); ctx.fill();

    ctx.beginPath();
    ctx.moveTo(SX(px + pw), SY(py)); ctx.lineTo(SX(px + pw), SY(py + ph));
    ctx.lineTo(SX(px + pw + skew), SY(py + ph - h)); ctx.lineTo(SX(px + pw + skew), SY(py - h));
    ctx.closePath(); ctx.fillStyle = mix(p.color, "black", 0.34); ctx.fill();

    ctx.beginPath();
    ctx.moveTo(SX(px), SY(py + ph)); ctx.lineTo(SX(px + pw), SY(py + ph));
    ctx.lineTo(SX(px + pw + skew), SY(py + ph - h)); ctx.lineTo(SX(px + skew), SY(py + ph - h));
    ctx.closePath(); ctx.fillStyle = mix(p.color, "black", 0.14); ctx.fill();

    if (night && p.lit) {
      ctx.fillStyle = "rgba(255,215,130,.75)";
      ctx.fillRect(SX(px + pw * 0.30 + skew * 0.5), SY(py + ph - h * 0.65), pw * 0.22 * Z, h * 0.34 * Z);
      ctx.fillRect(SX(px + pw * 0.62 + skew * 0.2), SY(py + ph - h * 0.65), pw * 0.22 * Z, h * 0.34 * Z);
    }
    ctx.beginPath();
    ctx.moveTo(SX(px + skew), SY(py - h)); ctx.lineTo(SX(px + pw + skew), SY(py - h));
    ctx.lineTo(SX(px + pw + skew), SY(py + ph - h)); ctx.lineTo(SX(px + skew), SY(py + ph - h));
    ctx.closePath(); ctx.fillStyle = mix(p.color, "white", 0.14); ctx.fill();
    ctx.strokeStyle = mix(p.color, "white", 0.30); ctx.lineWidth = Math.max(0.8, Z * 0.8); ctx.stroke();
  }
}

/* ---------------- draw: one building ---------------- */
let hovered = null, selected = null;
const hot = [];

function windowsOnFront(b, k) {
  const pad = padOf(), skew = skewOf(), h = heightOf(b);
  const px = b.tile[0] * TILE + pad, py = b.tile[1] * TILE + pad;
  const pw = TILE - pad * 2, ph = TILE - pad * 2;
  const cols = clamp(Math.round(pw / (TILE * 0.26)), 2, 5);
  const rows = clamp(Math.round(h / (TILE * 0.30)), 2, 6);
  const wgap = pw / cols, hgap = h / rows;
  const ww = wgap * 0.44, wh = hgap * 0.42;
  const seed = hash(b.id);
  const cells = [];
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const wx = px + c * wgap + wgap / 2 + skew * (1 - (r + 0.5) / rows);
      const wy = py + ph - h + r * hgap + hgap / 2;
      const noise = Math.sin((r * 12.9898 + c * 78.233 + seed * 43.7) * 43758.5453) % 1;
      cells.push({ x: wx - ww / 2, y: wy - wh / 2, w: ww, h: wh, lit: Math.abs(noise) > 0.42 });
    }
  }
  return cells;
}

function drawBuilding(b, t) {
  const P = pal();
  const { px, py, pw, ph, h, skew, topY } = box(b);
  const Z = S();
  const isHot = b === hovered || b === selected;

  // shadow
  ctx.save();
  ctx.globalAlpha = 1;
  ctx.fillStyle = P.shadow;
  ctx.beginPath();
  ctx.ellipse(SX(px + pw / 2 + skew / 2), SY(py + ph - h * 0.02), (pw * 0.58) * Z, (ph * 0.36) * Z, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // right wall
  ctx.beginPath();
  ctx.moveTo(SX(px + pw), SY(py));
  ctx.lineTo(SX(px + pw), SY(py + ph));
  ctx.lineTo(SX(px + pw + skew), SY(py + ph - h));
  ctx.lineTo(SX(px + pw + skew), SY(py - h));
  ctx.closePath();
  ctx.fillStyle = mix(b.color, "black", 0.55);
  ctx.fill();

  // front wall
  ctx.beginPath();
  ctx.moveTo(SX(px), SY(py + ph));
  ctx.lineTo(SX(px + pw), SY(py + ph));
  ctx.lineTo(SX(px + pw + skew), SY(py + ph - h));
  ctx.lineTo(SX(px + skew), SY(py + ph - h));
  ctx.closePath();
  ctx.fillStyle = mix(b.color, "black", 0.30);
  ctx.fill();

  // windows
  const base = mix(b.color, "black", 0.42);
  for (const c of windowsOnFront(b, t)) {
    ctx.fillStyle = (night && c.lit) ? P.winOn : mix(b.color, "black", 0.62);
    if (night && c.lit) ctx.fillStyle = rgba(P.winOn, 0.92);
    ctx.fillRect(SX(c.x), SY(c.y), c.w * Z, c.h * Z);
  }

  // top face
  ctx.beginPath();
  ctx.moveTo(SX(px + skew), SY(py - h));
  ctx.lineTo(SX(px + pw + skew), SY(py - h));
  ctx.lineTo(SX(px + pw + skew), SY(py + ph - h));
  ctx.lineTo(SX(px + skew), SY(py + ph - h));
  ctx.closePath();
  ctx.fillStyle = mix(b.color, "white", 0.16);
  ctx.fill();
  ctx.strokeStyle = rgba(b.color, 0.55); ctx.lineWidth = Math.max(1, Z); ctx.stroke();

  // roof ring on the top face
  ctx.beginPath();
  ctx.moveTo(SX(px + skew + pw * 0.18), SY(py - h + ph * 0.18));
  ctx.lineTo(SX(px + pw + skew - pw * 0.18), SY(py - h + ph * 0.18));
  ctx.lineTo(SX(px + pw + skew - pw * 0.18), SY(py + ph - h - ph * 0.18));
  ctx.lineTo(SX(px + skew + pw * 0.18), SY(py + ph - h - ph * 0.18));
  ctx.closePath();
  ctx.fillStyle = mix(b.color, "white", 0.30);
  ctx.fill();

  // selection / hover ring
  if (isHot) {
    const pulse = 0.5 + 0.5 * Math.sin(t / 320);
    ctx.save();
    ctx.strokeStyle = rgba("#ffffff", b === selected ? 0.85 : 0.45 + pulse * 0.25);
    ctx.lineWidth = Math.max(1.4, Z * 2);
    ctx.strokeRect(SX(px + skew) - 2, SY(topY) - 2, (pw + skew) * Z + 4, (ph + h) * Z + 4);
    ctx.restore();
  }

  // icon badge above the roof
  const ix = SX(px + pw / 2 + skew / 2), iy = SY(topY) - TILE * Z * 0.30;
  ctx.save();
  ctx.globalAlpha = 1;
  ctx.font = `${Math.round(TILE * Z * 0.52)}px system-ui, "Apple Color Emoji","Segoe UI Emoji",sans-serif`;
  ctx.textAlign = "center"; ctx.textBaseline = "middle";
  ctx.fillText(b.icon, ix, iy);
  ctx.restore();

  hot.push({ b, x0: SX(px) - 4, y0: SY(topY) - 4, x1: SX(px + pw + skew) + 4, y1: SY(py + ph) + TILE * Z * 0.45 });
}

function pulse(b) {
  b._pulse = performance.now();
}
function drawPulse(b, t) {
  if (!b._pulse) return;
  const age = t - b._pulse;
  if (age > 900) return;
  const k = age / 900;
  const { px, py, pw, ph, h, skew } = box(b);
  const cx = SX(px + pw / 2 + skew / 2), cy = SY(py + ph / 2 - h / 2);
  ctx.save();
  ctx.globalAlpha = (1 - k) * 0.8;
  ctx.strokeStyle = "#ffd782"; ctx.lineWidth = Math.max(2, S() * 2.4);
  ctx.beginPath(); ctx.arc(cx, cy, (TILE * S() * 0.6) + k * TILE * S() * 1.4, 0, Math.PI * 2); ctx.stroke();
  ctx.restore();
}

function drawLabels() {
  const P = pal(); const Z = S();
  ctx.save();
  ctx.textAlign = "center"; ctx.textBaseline = "top";
  ctx.font = `600 ${Math.round(clamp(TILE * Z * 0.21, 8, 14))}px system-ui, sans-serif`;
  for (const b of D.buildings) {
    const { px, py, pw, ph, skew } = box(b);
    const x = SX(px + pw / 2 + skew / 2);
    const y = SY(py + ph) + TILE * Z * 0.08;
    const on = b === hovered || b === selected;
    ctx.lineWidth = Math.max(2, Z * 2.6);
    ctx.strokeStyle = "rgba(4,7,16,.85)";
    ctx.strokeText(b.name, x, y);
    ctx.fillStyle = on ? "#ffffff" : P.label;
    ctx.fillText(b.name, x, y);
  }
  ctx.restore();
}

/* ---------------- agents ---------------- */
const agents = [];

function route(fromB, toB) {
  const f = [fromB.tile[0] + 0.5, fromB.tile[1] + 0.5];
  const t = [toB.tile[0] + 0.5, toB.tile[1] + 0.5];
  const r = D.roads;
  const rY = r.rows[0] + r.rows.length / 2;
  const rX = r.cols[0] + r.cols.length / 2;
  const pts = [f];

  const leftSide  = (gx) => gx < r.cols[0];
  const rightSide = (gx) => gx > r.cols[r.cols.length - 1];

  if ((leftSide(fromB.tile[0]) && leftSide(toB.tile[0])) ||
      (rightSide(fromB.tile[0]) && rightSide(toB.tile[0]))) {
    pts.push([f[0], rY], [t[0], rY], t);
  } else {
    pts.push([f[0], rY], [rX, rY], [rX, t[1]], t);
  }
  return pts;
}

function spawnAgent(fromB, toB, color) {
  const pts = route(fromB, toB).map(([x, y]) => [x * TILE, y * TILE]);
  let len = 0; const segs = [];
  for (let i = 1; i < pts.length; i++) {
    const d = Math.hypot(pts[i][0] - pts[i-1][0], pts[i][1] - pts[i-1][1]);
    segs.push({ a: pts[i-1], b: pts[i], d }); len += d;
  }
  const a = { segs, len, color, t: 0, dur: clamp(len / 0.22, 700, 2600), x: pts[0][0], y: pts[0][1], trail: [] };
  agents.push(a);
  return a;
}

function stepAgent(a, dt) {
  a.t += dt / a.dur;
  a.t = clamp(a.t, 0, 1);
  let want = a.t * a.len, acc = 0, x = 0, y = 0;
  for (const s of a.segs) {
    if (want <= acc + s.d || s === a.segs[a.segs.length - 1]) {
      const k = clamp((want - acc) / (s.d || 1), 0, 1);
      x = s.a[0] + (s.b[0] - s.a[0]) * k;
      y = s.a[1] + (s.b[1] - s.a[1]) * k;
      break;
    }
    acc += s.d;
  }
  a.x = x; a.y = y;
  a.trail.push([x, y]); if (a.trail.length > 16) a.trail.shift();
  return a.t >= 1;
}

function drawAgents() {
  const Z = S();
  for (const a of agents) {
    // trail
    ctx.save();
    ctx.strokeStyle = rgba(a.color, 0.45);
    ctx.lineWidth = Math.max(1.5, 2.2 * Z); ctx.lineJoin = "round"; ctx.lineCap = "round";
    ctx.beginPath();
    a.trail.forEach(([tx, ty], i) => i ? ctx.lineTo(SX(tx), SY(ty)) : ctx.moveTo(SX(tx), SY(ty)));
    ctx.stroke();
    ctx.restore();

    const x = SX(a.x), y = SY(a.y);
    const r = Math.max(4, TILE * Z * 0.14);
    ctx.save();
    const g = ctx.createRadialGradient(x, y, 0, x, y, r * 2.4);
    g.addColorStop(0, rgba(a.color, 0.65)); g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r * 2.4, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = a.color; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = "#ffffff"; ctx.globalAlpha = 0.85; ctx.lineWidth = Math.max(1, Z);
    ctx.stroke();
    ctx.restore();
  }
}

/* ---------------- particles ---------------- */
function confetti(x, y) {
  const colors = ["#f4c95d", "#6ea8fe", "#3ddc97", "#f72585", "#c77dff", "#ffb703"];
  for (let i = 0; i < 90; i++) {
    particles.push({
      x, y, vx: (Math.random() - 0.5) * 7, vy: -Math.random() * 8 - 2,
      g: 0.17 + Math.random() * 0.1, life: 1, size: 2 + Math.random() * 4,
      color: colors[(Math.random() * colors.length) | 0], rot: Math.random() * 6, vr: (Math.random() - .5) * .3
    });
  }
}
function drawParticles(dt) {
  for (let i = particles.length - 1; i >= 0; i--) {
    const p = particles[i];
    p.vy += p.g; p.x += p.vx; p.y += p.vy; p.rot += p.vr; p.life -= dt / 2400;
    if (p.life <= 0 || p.y > H + 40) { particles.splice(i, 1); continue; }
    ctx.save();
    ctx.globalAlpha = clamp(p.life, 0, 1);
    ctx.translate(p.x, p.y); ctx.rotate(p.rot);
    ctx.fillStyle = p.color;
    ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 1.6);
    ctx.restore();
  }
}

/* ---------------- render loop ---------------- */
let last = performance.now();
function frame(now) {
  const dt = Math.min(60, now - last); last = now;

  zSky();
  zPlate();

  hot.length = 0;
  for (const item of scene) {
    if (item.t === 0) drawBuilding(item.b, now);
    else drawProp(item.p);
  }
  drawAgents();

  for (let i = agents.length - 1; i >= 0; i--) {
    if (stepAgent(agents[i], dt)) agents.splice(i, 1);
  }
  for (const b of D.buildings) drawPulse(b, now);
  drawLabels();
  drawParticles(dt);

  requestAnimationFrame(frame);
}

/* ---------------- pointer interaction ---------------- */
let dragging = false, moved = false, lastX = 0, lastY = 0;
cvs.addEventListener("pointerdown", (e) => {
  dragging = true; moved = false; lastX = e.clientX; lastY = e.clientY;
  cvs.setPointerCapture(e.pointerId); cvs.style.cursor = "grabbing";
});
cvs.addEventListener("pointermove", (e) => {
  const x = e.clientX, y = e.clientY;
  if (dragging) {
    const dx = x - lastX, dy = y - lastY;
    if (Math.abs(dx) + Math.abs(dy) > 3) moved = true;
    cam.x += dx; cam.y += dy; lastX = x; lastY = y;
    return;
  }
  const hit = hitTest(x, y);
  const next = hit ? hit.b : null;
  if (next !== hovered) {
    hovered = next;
    cvs.style.cursor = hovered ? "pointer" : "default";
    $("hint").textContent = hovered ? hovered.name + " — click to inspect" : "Click a building to inspect it";
  }
});
cvs.addEventListener("pointerup", (e) => {
  dragging = false; cvs.style.cursor = hovered ? "pointer" : "default";
  if (!moved) {
    const hit = hitTest(e.clientX, e.clientY);
    if (hit) openPanel(hit.b); else closePanel();
  }
});
cvs.addEventListener("dblclick", () => { cam.zoom = 1; recenter(); });

cvs.addEventListener("wheel", (e) => {
  e.preventDefault();
  const before = cam.zoom;
  cam.zoom = clamp(cam.zoom * (e.deltaY < 0 ? 1.12 : 0.89), 0.55, 2.4);
  const k = cam.zoom / before;
  cam.x = e.clientX - (e.clientX - cam.x) * k;
  cam.y = e.clientY - (e.clientY - cam.y) * k;
}, { passive: false });

function hitTest(x, y) {
  for (let i = hot.length - 1; i >= 0; i--) {
    const h = hot[i];
    if (x >= h.x0 && x <= h.x1 && y >= h.y0 && y <= h.y1) return h;
  }
  return null;
}

/* ---------------- inspector panel ---------------- */
function openPanel(b) {
  selected = b;
  $("panel-icon").textContent = b.icon;
  $("panel-name").textContent = b.name;
  $("panel-role").textContent = b.role;
  $("panel-desc").textContent = b.desc;
  $("panel-last").textContent = b.last;
  $("panel-stat").textContent = b.stat;
  $("panel").classList.add("open");
  $("panel").setAttribute("aria-hidden", "false");
}
function closePanel() {
  selected = null;
  $("panel").classList.remove("open");
  $("panel").setAttribute("aria-hidden", "true");
}
$("panel-close").addEventListener("click", closePanel);

/* ---------------- event log ---------------- */
function log(html, kind = "work") {
  const el = document.createElement("div");
  el.className = "line " + kind;
  el.innerHTML = html;
  const box = $("log");
  box.appendChild(el);
  while (box.children.length > 5) box.removeChild(box.firstChild);
  setTimeout(() => { el.style.transition = "opacity .5s, transform .5s"; el.style.opacity = "0"; el.style.transform = "translateY(-6px)"; }, 7200);
  setTimeout(() => el.remove(), 7800);
}

/* ---------------- stats + countdown ---------------- */
let stats = { shipped: Number(D.stats.shipped) || 0, revenue: Number(D.stats.revenue) || 0 };
function setStat(id, value) {
  const el = $(id);
  if (el.textContent === String(value)) return;
  el.textContent = value;
  el.classList.remove("flash"); void el.offsetWidth; el.classList.add("flash");
}
function renderStats() {
  setStat("stat-shipped", stats.shipped);
  setStat("stat-revenue", "$" + Math.round(stats.revenue).toLocaleString());
}
function nextRun() {
  const Sch = D.schedule;
  const now = new Date();
  const d = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), Sch.hourUTC, 0, 0));
  let add = (Sch.weekday - d.getUTCDay() + 7) % 7;
  d.setUTCDate(d.getUTCDate() + add);
  if (d.getTime() <= now.getTime()) d.setUTCDate(d.getUTCDate() + 7);
  return d;
}
function renderCountdown() {
  const ms = nextRun().getTime() - Date.now();
  const h = ms / 3600000, days = Math.floor(h / 24), hrs = Math.floor(h % 24), mins = Math.floor((h * 60) % 60);
  const txt = days > 0 ? `${days}d ${hrs}h` : (hrs > 0 ? `${hrs}h ${mins}m` : `${mins}m`);
  setStat("stat-next", txt);
}

/* ---------------- live data overlay ----------------
   state.js (window.CITY_STATE) carries the real numbers. It is merged into
   CITY_DATA here, so the rest of the engine never has to know it exists.  */
function applyLive() {
  if (!LIVE) return false;
  const num = (v) => (Number.isFinite(+v) ? +v : null);

  if (LIVE.stats) {
    const sh = num(LIVE.stats.shipped), rev = num(LIVE.stats.revenue), av = num(LIVE.stats.avgPrice);
    if (sh !== null) D.stats.shipped = sh;
    if (rev !== null) D.stats.revenue = rev;
    if (av !== null && av > 0) D.stats.avgPrice = av;
  }
  if (LIVE.agents && typeof LIVE.agents === "object") {
    for (const b of D.buildings) {
      const a = LIVE.agents[b.id];
      if (!a) continue;
      if (a.note) b.last = a.note;
      b.status = a.status || "idle";
    }
  }
  stats.shipped = D.stats.shipped;
  stats.revenue = D.stats.revenue;
  return !!LIVE.source && LIVE.source !== "demo";
}

function ago(iso) {
  const t = Date.parse(iso);
  if (!t) return null;
  const s = Math.max(0, (Date.now() - t) / 1000);
  if (s < 90) return "just now";
  const m = s / 60; if (m < 90) return Math.round(m) + " min ago";
  const h = m / 60; if (h < 36) return Math.round(h) + " h ago";
  return Math.round(h / 24) + " d ago";
}

function renderLiveChrome(isLive) {
  const badge = $("live-badge");
  if (badge) {
    badge.textContent = isLive ? "\u25cf Live data" : "\u25cf Demo data";
    badge.className = "badge " + (isLive ? "on" : "off");
    badge.title = isLive
      ? "Real numbers, read from state.js" + (LIVE.generatedAt ? " (updated " + LIVE.generatedAt + ")" : "")
      : "These are placeholder numbers. Write state.js \u2014 see README \u2192 Wiring real data.";
  }

  const lr = LIVE && LIVE.lastRun;
  if (isLive && lr && lr.at) {
    const when = ago(lr.at);
    $("tagline").textContent = "Last build: " + (lr.product || "a new launch kit") + (when ? " \u00b7 " + when : "");
  }

  const st = LIVE && LIVE.store;
  const btn = $("store");
  if (btn && st && st.url) {
    btn.href = st.url;
    btn.textContent = "\ud83d\uded2 " + (st.label || "Store");
    btn.hidden = false;
  }
}

/* ---------------- the weekly episode ---------------- */
const btnRun = $("run-week");
let running = false;

async function runEpisode() {
  if (running) return;
  running = true; btnRun.disabled = true;
  const townHall = byId("town-hall") || D.buildings[0];
  closePanel();

  log("🛰️ <b>Monday 8:00 AM</b> — the city wakes up.", "ok");
  await wait(500);

  for (const step of D.episode) {
    const b = byId(step.id); if (!b) continue;
    const agent = spawnAgent(townHall, b, b.color);
    log(`${step.icon} <b>${b.name}</b> ${step.say}…`);
    while (agents.includes(agent)) await wait(60);
    pulse(b);
    log(`✅ ${step.ok}`, "ok");
    await wait(220);
  }

  stats.shipped += 1;
  stats.revenue = stats.shipped * D.stats.avgPrice;
  renderStats();

  const { px, py, pw, skew, topY } = box(townHall);
  confetti(SX(px + pw / 2 + skew / 2), SY(topY) - 40);
  log(`🎉 <b>Shipped product #${stats.shipped}</b> — launch kit ready to download.`, "ok");

  running = false; btnRun.disabled = false;
}
function byId(id) { return D.buildings.find((b) => b.id === id); }

/* ---------------- controls ---------------- */
btnRun.addEventListener("click", runEpisode);
$("toggle-time").addEventListener("click", () => {
  night = !night;
  $("toggle-time").textContent = night ? "🌗 Time" : "☀️ Time";
});
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closePanel();
  if (e.key === " ") { e.preventDefault(); runEpisode(); }
});

/* ---------------- boot ---------------- */
const isLive = applyLive();               // merge state.js into the city first
$("city-name").textContent = D.cityName;
$("tagline").textContent = D.tagline;
document.title = D.cityName + (isLive ? " — Live" : " — Demo");
layout();
makeProps();
buildScene();
renderStats();
renderLiveChrome(isLive);
renderCountdown();
setInterval(renderCountdown, 15000);
log(isLive
  ? `🏙️ <b>Agent City</b> online — live data: ${stats.shipped} shipped, $${Math.round(stats.revenue).toLocaleString()} earned.`
  : "🏙️ <b>Agent City</b> is online. Click a building, or press ▶ to run an episode.", "ok");
requestAnimationFrame(frame);

})();
