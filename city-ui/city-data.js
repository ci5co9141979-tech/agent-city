/* ============================================================
   AGENT CITY — DATA
   This is the only file you need to edit to change the city.
   Every building = one agent in your pipeline.
   tile: [gx, gy] grid position (gridSize below, default 14x14)
   Roads are fixed at rows/cols 6 and 7 — keep buildings off those.
   ============================================================ */
window.CITY_DATA = {
  cityName: "Agent City",
  tagline: "One product forged every Monday while you sleep.",

  gridSize: 14,
  roads: { rows: [6, 7], cols: [6, 7] },

  // Headline numbers (edit away — or drive these from real data)
  stats: { shipped: 0, revenue: 0, avgPrice: 24 },

  // Where the schedule comes from (shown in the countdown tooltip)
  schedule: { weekday: 1, hourUTC: 13, labelUTC: "13:00 UTC", labelLocal: "8:00 AM Central" },

  buildings: [
    {
      id: "town-hall", name: "Town Hall", role: "Orchestrator", icon: "🏛️",
      tile: [2, 2], height: 70, color: "#d4af37",
      desc: "Runs the whole city. Wakes up every Monday, calls the right agent for each job, and makes sure a finished product gets shipped before it goes back to sleep.",
      last: "Ships each week's launch kit",
      stat: "GitHub Actions + city.yml"
    },
    {
      id: "market-scout", name: "Market Scout", role: "Research", icon: "🔭",
      tile: [11, 2], height: 48, color: "#4cc9f0",
      desc: "Studies what people are actually buying this week and picks one product idea for the Forge to build. Keeps the city from repeating itself.",
      last: "Picks this week's product concept",
      stat: "Trend + niche research"
    },
    {
      id: "product-forge", name: "Product Forge", role: "Builder", icon: "🔨",
      tile: [4, 4], height: 56, color: "#ef8354",
      desc: "Takes the idea and writes the actual product — the file a customer downloads. This is where the value is created.",
      last: "Builds the product file",
      stat: "Python build step"
    },
    {
      id: "image-studio", name: "Image Studio", role: "Design", icon: "🎨",
      tile: [2, 11], height: 52, color: "#f72585",
      desc: "Renders the listing images and cover art so the product doesn't look homemade. Produces the pictures you upload to the store.",
      last: "Renders cover + listing images",
      stat: "Pillow / Playwright"
    },
    {
      id: "listing-writer", name: "Listing Writer", role: "Copy", icon: "✍️",
      tile: [9, 4], height: 44, color: "#c77dff",
      desc: "Writes the store listing — title, description and tags — tuned so the product is actually findable by buyers.",
      last: "Drafts title, description, tags",
      stat: "Claude model call"
    },
    {
      id: "bundle-depot", name: "Bundle Depot", role: "Packaging", icon: "📦",
      tile: [9, 9], height: 42, color: "#ffb703",
      desc: "Packs everything — product, images and listing text — into one launch kit zip so you can grab it in a single download.",
      last: "Packs the launch-kit zip",
      stat: "Artifacts upload"
    },
    {
      id: "archive", name: "The Archive", role: "Memory", icon: "🗄️",
      tile: [11, 11], height: 46, color: "#8d99ae",
      desc: "Remembers every product the city has ever shipped, so it never repeats itself. This is the record committed back to your repo each week.",
      last: "Commits the 'already launched' record",
      stat: "Git commit"
    },
    {
      id: "bank", name: "Credit Bank", role: "Budget", icon: "🏦",
      tile: [4, 9], height: 60, color: "#06d6a0",
      desc: "The API budget. Every build spends a little credit here — keep an eye on your Anthropic billing page so the city never runs dry.",
      last: "Tracks weekly API spend",
      stat: "console.anthropic.com"
    }
  ],

  // The order of a weekly episode. ids must match buildings above.
  episode: [
    { id: "market-scout",  say: "scans the market and picks this week's product idea", icon: "🔭", ok: "Picked a concept" },
    { id: "product-forge", say: "forges the product file",                            icon: "🔨", ok: "Product built" },
    { id: "image-studio",  say: "renders the cover and listing images",               icon: "🎨", ok: "Images rendered" },
    { id: "listing-writer",say: "writes the store listing copy",                      icon: "✍️", ok: "Copy drafted" },
    { id: "bundle-depot",  say: "packs it all into a launch kit",                     icon: "📦", ok: "Kit packed" },
    { id: "archive",       say: "records this week so it's never repeated",           icon: "🗄️", ok: "Recorded" },
    { id: "town-hall",     say: "publishes the product 🎉",                           icon: "🏛️", ok: "Shipped!" }
  ]
};
