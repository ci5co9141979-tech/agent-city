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
    url: ""
  },

  // Per-agent notes shown in the inspector ("Does").
  // ids match city-data.js: town-hall, market-scout, product-forge,
  // image-studio, listing-writer, bundle-depot, archive, bank
  agents: {
    // "market-scout": { status: "ok", note: "Picked: Freelance Invoice Pack" }
  },

  /* ---- machine-managed: written by scripts/sync_state.py ---- */
  /* @@CITY_AUTO_START@@ */
  source: "demo",              // "demo" | "workflow" | "manual"
  generatedAt: null,           // ISO timestamp of the last sync
  stats: {
    shipped: 0,                // products the city has shipped
    revenue: 0,                // dollars collected (you keep this current)
    avgPrice: 24               // your list price
  },
  lastRun: {
    at: null,                  // ISO timestamp of the newest build
    product: null,             // e.g. "Freelance Invoice Pack"
    kit: null,                 // link to the download / store page
    run: null                  // e.g. "agent-city-weekly #7"
  }
  /* @@CITY_AUTO_END@@ */
};
