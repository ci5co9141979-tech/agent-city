# Design notes

**Goal:** make a black-box automation job feel like a place you can visit.

- **2.5D box renderer, no WebGL.** Each building is an extruded quad with a skewed top
  face, flat-shaded from its own base colour (front −30%, side −55%, roof +16%). It reads
  as a city, stays crisp at any zoom, and costs nothing to run.
- **Icons float above the roofs.** Emoji badges mean you identify an agent in one glance;
  the name sits on the ground plane under the building, painted in the label colour only.
- **The episode is the scheduler.** `CITY_DATA.episode` is an ordered list. The runner
  walks it, spawns an agent from Town Hall for each step, drives it along the road grid,
  pulses the destination, and prints a log line on arrival. Reordering the array reorders
  the week — that's the whole state machine.
- **Pathfinding is grid-thin on purpose.** Agents route to the nearest road, along it, and
  back up. Two buildings on the same side of the vertical road take a straight run; anything
  crossing goes through the central intersection. Cheap, deterministic, and it *looks*
  like traffic because it obeys the same roads the player sees.
- **Log panel as narration.** Max five lines, auto-fading, colour-coded: blue = work,
  green = milestone. It's the run's stdout, translated into English.
- **Camera.** Drag to pan, wheel to zoom, anchored at the cursor so zooming feels physical.
  Hit-testing uses screen-space boxes collected during the same draw pass, so what you see
  is exactly what you can click.
- **Night is the default.** Windows are lit per-building from a stable hash of the id, so
  a building always looks the same on reload — variety without flicker.
- **Live data is a separate script, not a fetch.** `state.js` is a plain `<script>` that
  sets `window.CITY_STATE`, so the page still works when opened by double-clicking
  (`file://`) where `fetch()` is blocked. `app.js` merges it into `CITY_DATA` in one place
  (`applyLive()`), which keeps the engine ignorant of where the numbers came from.
- **A visible source badge.** Grey "Demo data" vs green "Live data" means you can never
  mistake placeholder numbers for real ones — the same reason the shipped/revenue stats
  start at zero.
