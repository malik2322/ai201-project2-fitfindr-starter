# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tool Inventory

| Tool | Signature | Inputs | Returns |
|------|-----------|--------|---------|
| `search_listings` | `search_listings(description: str, size: str \| None = None, max_price: float \| None = None) -> list[dict]` | `description` — keywords describing the item (e.g. `"vintage graphic tee"`); `size` — size string to filter by, or `None` to skip (`"M"` matches `"S/M"`); `max_price` — maximum price inclusive, or `None` to skip | A list of matching listing dicts sorted by keyword-overlap relevance (best first). Returns `[]` if nothing matches — never raises an exception. |
| `suggest_outfit` | `suggest_outfit(new_item: dict, wardrobe: dict) -> str` | `new_item` — a listing dict (the item the user is considering); `wardrobe` — a dict with an `"items"` key containing wardrobe item dicts (may be empty) | A string with 1–2 outfit suggestions. If the wardrobe is empty, returns general styling advice instead. Uses Groq `llama-3.3-70b-versatile`. |
| `create_fit_card` | `create_fit_card(outfit: str, new_item: dict) -> str` | `outfit` — the outfit suggestion string from `suggest_outfit()`; `new_item` — the listing dict for the thrifted item | A 2–4 sentence Instagram/TikTok-style caption mentioning the item name, price, and platform. Returns `"Error: missing outfit data"` if outfit is empty/None/whitespace. Uses Groq with `temperature=0.9` for varied output. |

---

## Interaction Walkthrough

**User query:** `"vintage graphic tee under $30"`

**Step 1 — Tool called:**
- Tool: `search_listings`
- Input: `description="vintage graphic tee"`, `size=None`, `max_price=30.0`
- Why this tool: The agent needs to find matching listings from the mock dataset before it can suggest outfits. The query parser extracted the keywords and price ceiling from the natural language input.
- Output: 20 matching listings sorted by relevance. Top result: **Y2K Baby Tee — Butterfly Print** ($18.00, size S/M, depop, condition: excellent).

**Step 2 — Tool called:**
- Tool: `suggest_outfit`
- Input: `new_item=` the Y2K Baby Tee listing dict (from Step 1's top result), `wardrobe=` the user's example wardrobe (10 items including baggy jeans, combat boots, khaki trousers, etc.)
- Why this tool: Now that the agent has a specific item, it needs to show the user how it fits with what they already own. The selected item and wardrobe are passed directly from session state — no re-fetching.
- Output: *"Here are two outfit combinations: (1) Pair the Y2K Baby Tee with the baggy straight-leg jeans and chunky white sneakers for a casual, retro-inspired look. (2) Combine the Y2K Baby Tee with the wide-leg khaki trousers and black combat boots for a vintage, cottagecore-inspired outfit."*

**Step 3 — Tool called:**
- Tool: `create_fit_card`
- Input: `outfit=` the outfit suggestion string from Step 2, `new_item=` the same Y2K Baby Tee listing dict
- Why this tool: The user needs a shareable social media caption that captures the outfit vibe. The fit card is generated from the outfit suggestion and item details — not re-derived from scratch.
- Output: *"I'm obsessed with this Y2K Baby Tee I scored on Depop for $18.0 — it's giving me major retro vibes. I paired it with my fave baggy straight-leg jeans and chunky white sneakers for a casual, laid-back look that's totally channeling the early 2000s."*

**Final output to user:** The Gradio UI displays three panels: (1) the top listing details (title, price, size, condition, platform, colors, style tags, description), (2) the outfit suggestion with specific wardrobe pieces named, and (3) the fit card caption ready to copy-paste to social media.

---

## Error Handling and Fail Points

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| `search_listings` | Returns `[]` — no listings match the query (e.g. `"designer ballgown XXS under $5"`) | Agent sets `session["error"] = "No listings found"`, sets `fit_card` to `None`, and returns the session immediately. `suggest_outfit` and `create_fit_card` are **never called** — the branching logic in `run_agent()` exits early to avoid passing empty data downstream. |
| `suggest_outfit` | Wardrobe is empty or missing the `"items"` key | The function safely checks `wardrobe.get("items", [])`. If empty, it sends the LLM a general styling prompt (what kinds of pieces pair well, what vibe it suits) instead of referencing specific wardrobe items. It never crashes on missing keys — all dict access uses `.get()` with defaults. |
| `create_fit_card` | Outfit string is empty, `None`, or whitespace-only | The function checks `if not outfit or not outfit.strip()` before calling the LLM. If the guard triggers, it returns `"Error: missing outfit data"` immediately — no LLM call is made, no exception is raised, and the return type is always a string. |

---

## Spec Reflection

**One way planning.md helped during implementation:**
The Planning Loop section forced me to define the exact session dict fields and the conditional branching logic (stop after `search_listings` if results are empty) *before* writing any code. This meant when I implemented `run_agent()`, the if/else structure was already decided — I just translated the written steps into code. Without that, I would likely have written the happy path first and bolted on error handling as an afterthought, which is how tools end up calling each other with `None` inputs and crashing.

**One divergence from your spec, and why:**
The spec described query parsing as simple string splitting, but the implementation uses regex patterns (`r"(?:under|below|max|less than|<)\s*\$?([\d.]+)"` for price, `r"(?:size|sz)\s+([a-z0-9/]+)"` for size) instead. Pure string splitting couldn't reliably handle variations like `"under $30"` vs `"$30 or less"` vs `"max $30"` — the regex approach handles all of these with one pattern per field and strips the matched phrases from the description cleanly, so the remaining keywords are what gets passed to `search_listings`.

---

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
