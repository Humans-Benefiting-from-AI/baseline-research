# AI in Judaism: Independent Registry

This repository holds the raw data and site structure for the public Registry of 110 Jewish AI tools.
The registry is the first proof point for our independent research and audit shop.

## Principles
- **No Institutional Accountability:** We do not seek rabbinic approval or institutional backing.
- **Empirical & Technical Authority:** Our standing comes from accurate, verifiable measurements and analysis.
- **Honest Differentiation:** If a tool is just a chat wrapper over Sefaria, we say so.

## Structure
- `/data/raw_registry.md`: Source markdown (main 110-project table + separate Top 20 deep-dive table).
- `/data/registry.json`: Parsed **110** projects only. Never mixed with deep-dive rows.
- `/data/deep_dive.json`: Parsed **Top 20** strategic deep dives, keyed by `project_id` → registry `id`.
- `/data/manifest.json`: Counts and generation metadata for CI checks.
- `/scripts/parse_markdown_to_json.py`: Section-aware parser. Writes data + synced copies under `web/src/data/`.
- `/web`: React/Vite frontend for the public registry.

**Important:** The main projects table and the deep-dive table have different schemas. The parser treats them as separate sections. Do not merge deep-dive rows into `registry.json`.

## Regenerate JSON

```bash
cd registry
python3 scripts/parse_markdown_to_json.py
python3 scripts/parse_markdown_to_json.py --check   # verify committed JSON is current
```

The parser fails non-zero if row counts drift, ids are incomplete, categories/maturities are outside the allowlist, or a deep-dive `project_id` is missing from the registry.
