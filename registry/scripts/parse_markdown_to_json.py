#!/usr/bin/env python3
"""Parse raw_registry.md into registry.json (110) and deep_dive.json (20)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"
WEB_DATA_DIR = SCRIPT_DIR.parent / "web" / "src" / "data"
RAW_MD = DATA_DIR / "raw_registry.md"

REGISTRY_PATH = DATA_DIR / "registry.json"
DEEP_DIVE_PATH = DATA_DIR / "deep_dive.json"
MANIFEST_PATH = DATA_DIR / "manifest.json"
WEB_REGISTRY_PATH = WEB_DATA_DIR / "registry.json"
WEB_DEEP_DIVE_PATH = WEB_DATA_DIR / "deep_dive.json"

EXPECTED_REGISTRY_COUNT = 110
EXPECTED_DEEP_DIVE_COUNT = 20

ALLOWED_CATEGORIES = {
    "AI",
    "Learning & Study Tools",
    "Extensions & API Integrations",
    "Apps & Other Tools",
    "Visualization & Data Analysis",
    "Community, Interaction & Social",
}

ALLOWED_MATURITIES = {
    "Live product",
    "Live but thin",
    "Demo/prototype",
    "Open-source library",
    "Tutorial/content",
    "Unknown",
}

MAIN_HEADER_PREFIX = "| # | Project | Category"
DEEP_HEADER_PREFIX = "| Rank | # | Project"
MAIN_SECTION_HEADING = "## All Projects"
DEEP_SECTION_HEADING = "## Deep Dive"

VARIATION_SPLIT_RE = re.compile(r"(?:\\n|\n)\s*(?=\d+\))")
VARIATION_PREFIX_RE = re.compile(r"^\d+\)\s*")


class ParseError(Exception):
    """Raised when registry markdown does not match the expected schema."""


def split_row(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith("|"):
        return []
    return [col.strip() for col in line.split("|")[1:-1]]


def is_separator(cols: list[str]) -> bool:
    if not cols:
        return False
    return all(re.fullmatch(r":?-{3,}:?", c or "") is not None for c in cols)


def is_heading(line: str) -> bool:
    return line.lstrip().startswith("## ")


def normalize_variation_text(text: str) -> str:
    # Markdown export sometimes embeds literal \n sequences.
    return text.replace("\\n", "\n").strip()


def split_numbered_variations(text: str) -> list[str]:
    text = normalize_variation_text(text)
    if not text:
        return []
    parts = VARIATION_SPLIT_RE.split(text)
    ideas: list[str] = []
    for part in parts:
        cleaned = VARIATION_PREFIX_RE.sub("", part.strip()).strip()
        if cleaned:
            ideas.append(cleaned)
    return ideas


def parse_main_row(cols: list[str], line_no: int) -> dict:
    if len(cols) < 9:
        raise ParseError(f"Main table line {line_no}: expected >= 9 cells, got {len(cols)}")
    if not cols[0].isdigit():
        raise ParseError(f"Main table line {line_no}: id is not numeric: {cols[0]!r}")

    project_id = int(cols[0])
    if project_id < 1 or project_id > EXPECTED_REGISTRY_COUNT:
        raise ParseError(f"Main table line {line_no}: id {project_id} out of range")

    name = cols[1]
    category = cols[2]
    maturity = cols[3]
    link = cols[4]
    description = cols[5]
    core_feature = cols[6]
    differentiator = cols[7]

    if name.isdigit():
        raise ParseError(f"Main table line {line_no}: name looks like a bare number: {name!r}")
    if category not in ALLOWED_CATEGORIES:
        raise ParseError(f"Main table line {line_no}: invalid category {category!r}")
    if maturity not in ALLOWED_MATURITIES:
        raise ParseError(f"Main table line {line_no}: invalid maturity {maturity!r}")

    # cells[8:] are pipe-separated variation ideas (typically 1), 2), 3))
    variation_ideas: list[str] = []
    for cell in cols[8:]:
        cleaned = VARIATION_PREFIX_RE.sub("", cell.strip()).strip()
        if cleaned:
            variation_ideas.append(cleaned)

    if len(variation_ideas) < 1:
        raise ParseError(f"Main table line {line_no}: missing variation ideas")

    return {
        "id": project_id,
        "name": name,
        "category": category,
        "maturity": maturity,
        "link": link,
        "description": description,
        "core_feature": core_feature,
        "differentiator": differentiator,
        "variation_ideas": variation_ideas,
        "source": "sefaria_powered_by",
        "schema_version": 1,
    }


def parse_deep_row(cols: list[str], header: list[str], line_no: int, registry_ids: set[int]) -> dict:
    if len(cols) != len(header):
        raise ParseError(
            f"Deep dive line {line_no}: expected {len(header)} cells, got {len(cols)}"
        )

    row = dict(zip(header, cols))
    try:
        rank = int(row["Rank"])
        project_id = int(row["#"])
    except (KeyError, ValueError) as exc:
        raise ParseError(f"Deep dive line {line_no}: invalid rank/project id") from exc

    if rank < 1 or rank > EXPECTED_DEEP_DIVE_COUNT:
        raise ParseError(f"Deep dive line {line_no}: rank {rank} out of range")
    if project_id not in registry_ids:
        raise ParseError(
            f"Deep dive line {line_no}: project_id {project_id} not in registry"
        )

    name = row["Project"]
    category = row["Category"]
    maturity = row["Maturity"]
    if category not in ALLOWED_CATEGORIES:
        raise ParseError(f"Deep dive line {line_no}: invalid category {category!r}")
    if maturity not in ALLOWED_MATURITIES:
        raise ParseError(f"Deep dive line {line_no}: invalid maturity {maturity!r}")

    variations_cell = row.get("Variations (5)", "") or ""
    variations = split_numbered_variations(variations_cell)
    if len(variations) < 1:
        raise ParseError(f"Deep dive line {line_no}: missing variations")

    return {
        "rank": rank,
        "project_id": project_id,
        "name": name,
        "category": category,
        "maturity": maturity,
        "link": row.get("Link", ""),
        "what_it_actually_is": row.get("What It Actually Is", ""),
        "core_mechanic": row.get("Core Mechanic (reusable primitive)", ""),
        "real_differentiator": row.get("Real Differentiator", ""),
        "strategic_interest": row.get("Why It Is Strategically Interesting", ""),
        "whats_missing": row.get("What's Missing / Unbuilt", ""),
        "variations": variations,
        "schema_version": 1,
    }


def parse_markdown(md_path: Path) -> tuple[list[dict], list[dict]]:
    lines = md_path.read_text(encoding="utf-8").splitlines()

    projects: list[dict] = []
    deep_dives: list[dict] = []
    mode: str | None = None  # None | "main" | "deep"
    deep_header: list[str] | None = None
    seen_main_header = False
    seen_deep_header = False

    for line_no, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith(MAIN_SECTION_HEADING) or stripped.startswith(MAIN_HEADER_PREFIX):
            mode = "main"
            if stripped.startswith(MAIN_HEADER_PREFIX):
                seen_main_header = True
            continue

        if stripped.startswith(DEEP_SECTION_HEADING) or stripped.startswith(DEEP_HEADER_PREFIX):
            mode = "deep"
            deep_header = None
            if stripped.startswith(DEEP_HEADER_PREFIX):
                seen_deep_header = True
                deep_header = split_row(stripped)
            continue

        # Exit table modes on new markdown headings (other sections).
        if is_heading(stripped) and mode is not None:
            mode = None
            deep_header = None
            continue

        # Exit on non-table content once inside a section.
        if mode is not None and stripped and not stripped.startswith("|"):
            mode = None
            deep_header = None
            continue

        if mode is None or not stripped.startswith("|"):
            continue

        cols = split_row(stripped)
        if not cols or is_separator(cols):
            continue

        if mode == "main":
            # Header row inside main section.
            if cols[0] == "#":
                seen_main_header = True
                continue
            projects.append(parse_main_row(cols, line_no))
            continue

        if mode == "deep":
            if cols[0] == "Rank":
                deep_header = cols
                seen_deep_header = True
                continue
            if deep_header is None:
                raise ParseError(f"Deep dive line {line_no}: data row before header")
            registry_ids = {p["id"] for p in projects}
            deep_dives.append(parse_deep_row(cols, deep_header, line_no, registry_ids))

    if not seen_main_header:
        raise ParseError("Main projects table header not found")
    if not seen_deep_header:
        raise ParseError("Deep dive table header not found")

    validate_projects(projects)
    validate_deep_dives(deep_dives, {p["id"] for p in projects})
    return projects, deep_dives


def validate_projects(projects: list[dict]) -> None:
    if len(projects) != EXPECTED_REGISTRY_COUNT:
        raise ParseError(
            f"Expected {EXPECTED_REGISTRY_COUNT} projects, got {len(projects)}"
        )
    ids = [p["id"] for p in projects]
    if len(set(ids)) != len(ids):
        raise ParseError("Duplicate project ids in registry")
    if set(ids) != set(range(1, EXPECTED_REGISTRY_COUNT + 1)):
        raise ParseError("Registry ids must be exactly 1..110")
    for p in projects:
        if re.fullmatch(r"\d+", p["name"] or ""):
            raise ParseError(f"Project {p['id']}: numeric name {p['name']!r}")
        if p["category"] not in ALLOWED_CATEGORIES:
            raise ParseError(f"Project {p['id']}: invalid category {p['category']!r}")
        if p["maturity"] not in ALLOWED_MATURITIES:
            raise ParseError(f"Project {p['id']}: invalid maturity {p['maturity']!r}")
        if not isinstance(p.get("variation_ideas"), list) or len(p["variation_ideas"]) < 1:
            raise ParseError(f"Project {p['id']}: variation_ideas must be a non-empty list")


def validate_deep_dives(deep_dives: list[dict], registry_ids: set[int]) -> None:
    if len(deep_dives) != EXPECTED_DEEP_DIVE_COUNT:
        raise ParseError(
            f"Expected {EXPECTED_DEEP_DIVE_COUNT} deep dive rows, got {len(deep_dives)}"
        )
    ranks = [d["rank"] for d in deep_dives]
    if len(set(ranks)) != len(ranks):
        raise ParseError("Duplicate ranks in deep dive")
    if set(ranks) != set(range(1, EXPECTED_DEEP_DIVE_COUNT + 1)):
        raise ParseError("Deep dive ranks must be exactly 1..20")
    for d in deep_dives:
        if d["project_id"] not in registry_ids:
            raise ParseError(
                f"Deep dive rank {d['rank']}: project_id {d['project_id']} missing from registry"
            )
        if not isinstance(d.get("variations"), list) or len(d["variations"]) < 1:
            raise ParseError(f"Deep dive rank {d['rank']}: variations must be a non-empty list")


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def build_manifest(projects: list[dict], deep_dives: list[dict]) -> dict:
    return {
        "registry_count": len(projects),
        "deep_dive_count": len(deep_dives),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_markdown": str(RAW_MD.relative_to(DATA_DIR.parent)),
    }


def emit_outputs(projects: list[dict], deep_dives: list[dict]) -> None:
    projects_sorted = sorted(projects, key=lambda p: p["id"])
    deep_sorted = sorted(deep_dives, key=lambda d: d["rank"])
    manifest = build_manifest(projects_sorted, deep_sorted)

    write_json(REGISTRY_PATH, projects_sorted)
    write_json(DEEP_DIVE_PATH, deep_sorted)
    write_json(MANIFEST_PATH, manifest)

    write_json(WEB_REGISTRY_PATH, projects_sorted)
    write_json(WEB_DEEP_DIVE_PATH, deep_sorted)


def check_committed(projects: list[dict], deep_dives: list[dict]) -> None:
    """Ensure committed JSON matches a fresh parse (ignores manifest timestamp)."""
    projects_sorted = sorted(projects, key=lambda p: p["id"])
    deep_sorted = sorted(deep_dives, key=lambda d: d["rank"])

    checks = [
        (REGISTRY_PATH, projects_sorted),
        (DEEP_DIVE_PATH, deep_sorted),
        (WEB_REGISTRY_PATH, projects_sorted),
        (WEB_DEEP_DIVE_PATH, deep_sorted),
    ]
    for path, expected in checks:
        if not path.exists():
            raise ParseError(f"--check failed: missing {path}")
        actual = load_json(path)
        if actual != expected:
            raise ParseError(f"--check failed: {path} is out of date; re-run parser")

    if not MANIFEST_PATH.exists():
        raise ParseError(f"--check failed: missing {MANIFEST_PATH}")
    manifest = load_json(MANIFEST_PATH)
    if not isinstance(manifest, dict):
        raise ParseError("--check failed: manifest.json is not an object")
    if manifest.get("registry_count") != EXPECTED_REGISTRY_COUNT:
        raise ParseError("--check failed: manifest registry_count mismatch")
    if manifest.get("deep_dive_count") != EXPECTED_DEEP_DIVE_COUNT:
        raise ParseError("--check failed: manifest deep_dive_count mismatch")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Parse and verify committed JSON matches (do not write)",
    )
    args = parser.parse_args(argv)

    if not RAW_MD.exists():
        print(f"ERROR: missing source markdown: {RAW_MD}", file=sys.stderr)
        return 1

    try:
        projects, deep_dives = parse_markdown(RAW_MD)
        if args.check:
            check_committed(projects, deep_dives)
            print(
                f"OK: check passed "
                f"({len(projects)} projects, {len(deep_dives)} deep dives)"
            )
            return 0

        emit_outputs(projects, deep_dives)
        print(
            f"Successfully parsed {len(projects)} projects and "
            f"{len(deep_dives)} deep-dive entries."
        )
        print(f"  wrote {REGISTRY_PATH}")
        print(f"  wrote {DEEP_DIVE_PATH}")
        print(f"  wrote {MANIFEST_PATH}")
        print(f"  wrote {WEB_REGISTRY_PATH}")
        print(f"  wrote {WEB_DEEP_DIVE_PATH}")
        return 0
    except ParseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
