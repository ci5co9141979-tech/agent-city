# Agent City

Six agents share a task board and town square (SQLite) and ship one product per category, unattended.

| Agent | Job |
|---|---|
| mayor | opens a line per product, re-queues work when QA fails (max 2 retries) |
| scout | niche brief + keywords |
| forge | runs the product builder |
| sentinel | QA: opens files, validates LUT math, form fields, formulas, and drives the HTML apps in a headless browser |
| scribe | store listing (title, description, tags) |
| canvas | listing images from the REAL product: 5 square images + 1280x720 cover (see `out/<line>/images/`) |
| muse | once a week picks the next product (rotates micro app / LUT pack / printable pack / vault) |
| herald | zips the product + listing into `out/<line>/<line>_bundle.zip` |

Weekly autopilot: `python3 run.py --weekly` builds ONE new product. `state/launched.json` remembers what's done.
Backlog (city/backlog.py): 6 calculators, 5 LUT niches, 5 printable packs, 4 vault niches = 20 weeks offline. With `ANTHROPIC_API_KEY` the muse invents new niches (schema-checked; calculator formulas are allow-listed) and adds courses to the rotation.

Run everything: `pip install -r requirements.txt && python3 run.py` then open `out/dashboard.html`.
Set `ANTHROPIC_API_KEY` and scout/scribe use Claude instead of offline templates.
`.github/workflows/city.yml` runs it weekly with no involvement from you.

## Not automated (needs your accounts)
Uploading to Etsy/Gumroad/etc. requires your seller login and, for most, their approval flow. The city stops at an upload-ready kit:
`out/<line>/listing.md` (paste), `<line>_bundle.zip` (upload), `images/` (listing photos + cover).
