/* ============================================================
   AGENT CITY — LIVE STATE
   ------------------------------------------------------------
   city-data.js  = the SHAPE of your city (agents, roads, schedule)
   state.js      = the LIVE numbers (what actually happened)

   Two ways to fill this in:

     1. AUTOMATIC — let the Monday workflow write it.
        Add the step in WORKFLOW_SNIPPET.yml, which runs:
            python3 city-ui/scripts/sync_state.py

     2. BY HAND — after each Monday, edit the numbers between the
        @@CITY_AUTO markers below. Set "source" to "manual".

   While "source" is "demo" the HUD shows a grey "Demo data" badge
   and every number is a placeholder. Flip it to "workflow" (the
   script does this) or "manual" and the badge turns green.
   ============================================================ */
window.CITY_STATE = {
  schema: 1,

  /* ---- yours to edit: the generator never touches these ---- */

  // The 🛒 button appears in the HUD once url is filled in.
  store: {
    label: "Buy on Gumroad",
    url: "https://ci5co.gumroad.com/"
  },

  // Per-agent notes shown in the inspector ("Does").
  // ids match city-data.js: town-hall, market-scout, product-forge,
  // image-studio, listing-writer, bundle-depot, archive, bank
  agents: {
    // "market-scout": { status: "ok", note: "Picked: Freelance Invoice Pack" }
  },

  /* ---- machine-managed: written by scripts/sync_state.py ---- */
  /* @@CITY_AUTO_START@@ */
  source: "workflow",
  generatedAt: "2026-10-12T05:35:53Z",
  stats: {
    "shipped": 4,
    "revenue": 0.0,
    "avgPrice": 24.0
  },
  lastRun: {
    "at": "2026-10-12",
    "product": "Fitness & Wellness Coach Content & Planning Vault",
    "kit": null,
    "run": null
  }
  /* @@CITY_AUTO_END@@ */
};
