# Agent City — interactive city UI

A single-page, dependency-free visualisation of your `agent-city` pipeline.
Every building is an agent; painting the town green = a shipped product.

## Run it

Open `index.html` in a browser, or serve the folder:

```bash
python3 -m http.server 3000 --directory city-ui
# then visit http://localhost:3000
```

## Files

| File | What it is | Do you edit it? |
| --- | --- | --- |
| `index.html` | the page | rarely |
| `styles.css` | the look | rarely |
| `app.js` | the engine (canvas, roads, agents) | no |
| `city-data.js` | **the shape of your city** — agents, roads, schedule, wording | yes |
| `state.js` | **the live numbers** — what actually shipped | yes, or let the workflow |
| `scripts/sync_state.py` | writes `state.js` from your repo contents | no |
| `WORKFLOW_SNIPPET.yml` | the step to paste into `city.yml` | copy from it |
| `design_notes.md` | why it looks and behaves the way it does | read |

## What you can do

| Action | Result |
| --- | --- |
| **Click a building** | Opens the inspector: what that agent does and which tool it uses |
| **▶ Run an episode** (or `Space`) | Plays one Monday: agents drive out of Town Hall, work, and the city ships a product |
| **🌗 Time** | Toggles day / night (windows light up at night) |
| **🛒 Store** | Opens your shop — only appears once `store.url` is set in `state.js` |
| **Drag** | Pans the city |
| **Double-click** | Re-centres and resets the zoom |
| **Scroll / pinch** | Zooms |
| **Esc** | Closes the inspector |

The **Next build** counter counts down to the next Monday 13:00 UTC run.

## Wiring real data

The HUD shows a badge: **● Demo data** (grey) means the numbers are placeholders,
**● Live data** (green) means they came from `state.js`.

### The shape of `state.js`

```js
window.CITY_STATE = {
  source: "workflow",              // "demo" | "workflow" | "manual"
  stats:  { shipped: 4, revenue: 96, avgPrice: 24 },
  lastRun:{ at: "2026-10-13T13:04:11Z", product: "Weekly Meal Planner", kit: "products/2026-10-13_meal-planner" },
  store:  { label: "Buy on Gumroad", url: "https://you.gumroad.com" },
  agents: { "market-scout": { status: "ok", note: "Picked: Weekly Meal Planner" } }
};
```

- `shipped` / `lastRun` / `generatedAt` → written for you by the script.
- `revenue` → **yours to keep current.** No automation can know what you actually sold.
- `store.url` → paste your Gumroad/Etsy link here and the 🛒 button appears.
- `agents` → optional per-agent notes shown in the inspector.

### Option A — automatic (recommended)

1. Copy the whole `city-ui` folder into your repo, next to `.github/`.
2. Open **`city-ui/WORKFLOW_SNIPPET.yml`** and paste the step it shows into
   `.github/workflows/city.yml`, after the product is built and before the commit step.
3. Make sure that commit step includes `city-ui/state.js` (it usually uses `git add -A`).
4. Run the workflow once. `state.js` gets rewritten, and the city flips to **Live**.

`sync_state.py` scans the usual output folders (`products/`, `launch_kits/`, `kits/`,
`builds/`, `releases/`, `output/`, `dist/`, …) for folders that directly contain a
`.zip` or a listing file, counts them, and takes the newest as the last build.
It never fails the build: if it finds nothing it leaves your numbers alone.

```bash
python3 city-ui/scripts/sync_state.py --dry-run        # show what it found, change nothing
python3 city-ui/scripts/sync_state.py --shipped 6 --revenue 144 --product "X" --store-url https://you.gumroad.com
```

If your repo uses a different folder name, either pass `--out`/move things, or just
use Option B — or tell me the layout and I'll point the script at it.

### Option B — by hand (30 seconds a week)

Skip the workflow step. After each Monday, open `state.js` and change the numbers
between the `@@CITY_AUTO` markers, then set `source` to `"manual"`.

## Make it *your* city

Everything about the city itself lives in **`city-data.js`**:

```js
window.CITY_DATA = {
  cityName: "Agent City",
  gridSize: 14,
  roads: { rows: [6,7], cols: [6,7] },   // keep buildings off these rows/cols
  schedule:{ weekday: 1, hourUTC: 13 },  // 1 = Monday — must match your cron
  stats:   { avgPrice: 24 },
  buildings: [
    { id, name, role, icon, tile:[gx,gy], height, color, desc, last, stat }
  ],
  episode: [ { id, say, icon, ok } ]     // the order of a weekly run
};
```

- **Add an agent:** append a building (and optionally an `episode` step with the same `id`).
- **Change the schedule:** edit `schedule` to match the `cron:` line in `city.yml`.
- **Reorder the week:** reorder `episode` — that array *is* the state machine.
