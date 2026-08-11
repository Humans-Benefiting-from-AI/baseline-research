#!/usr/bin/env python3
"""
Jewish AI Tool Discovery & Registry Update Pipeline

Monitors multiple sources for new Jewish AI tools:
- Product Hunt (new products)
- GitHub (Jewish + AI repos)
- Twitter/X (AI + Judaism discussions)
- HN (AI-related Jewish content)

Output: Staged entries for manual review before adding to Registry.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def discover_tools_github(language: str = "javascript,python", limit: int = 5) -> list[dict]:
    """
    Discover new repos tagged with jewish+ai.
    Requires GitHub API token in env var GITHUB_TOKEN.
    """
    # This is a stub—implement with github3.py or requests to GitHub API
    print(f"[TODO] Implement GitHub discovery for jewish+{language} repos")
    return []


def discover_tools_product_hunt(category: str = "judaica", limit: int = 5) -> list[dict]:
    """
    Discover new products on Product Hunt tagged with Jewish/Religion + AI.
    Requires Product Hunt API key.
    """
    print(f"[TODO] Implement Product Hunt discovery for {category}")
    return []


def discover_tools_twitter(query: str = "jewish AI tool", limit: int = 10) -> list[dict]:
    """
    Search Twitter for mentions of new Jewish AI tools.
    Requires Twitter API v2 bearer token.
    """
    print(f"[TODO] Implement Twitter search for '{query}'")
    return []


def create_staging_entry(
    name: str,
    link: str,
    description: str,
    source: str,
    discovered_date: str,
) -> dict:
    """Create a new staging entry for manual review."""
    return {
        'id': None,  # To be assigned
        'name': name,
        'link': link,
        'description': description,
        'category': 'Pending Review',
        'maturity': 'Unknown',
        'core_feature': '[TODO: Analyze]',
        'differentiator': '[TODO: Analyze]',
        'variation_ideas': '[TODO: Analyze]',
        'source': source,
        'discovered_date': discovered_date,
        'status': 'STAGING',
    }


def load_staging_queue(staging_path: str) -> list[dict]:
    """Load existing staging queue."""
    if Path(staging_path).exists():
        with open(staging_path, 'r') as f:
            return json.load(f)
    return []


def save_staging_queue(tools: list[dict], staging_path: str):
    """Save staging queue to disk."""
    with open(staging_path, 'w') as f:
        json.dump(tools, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved {len(tools)} staged tools to {staging_path}")


def main():
    staging_dir = Path(__file__).parent / 'staging'
    staging_dir.mkdir(exist_ok=True)
    staging_path = staging_dir / 'new_tools_staging.json'

    print("=" * 60)
    print("JEWISH AI TOOL DISCOVERY")
    print("=" * 60 + "\n")

    # Load existing staging queue
    staged = load_staging_queue(str(staging_path))
    print(f"Existing staging queue: {len(staged)} tools\n")

    # Discover new tools (stubs for now)
    print("Discovering new tools...\n")

    new_tools = []

    # GitHub discovery
    github_tools = discover_tools_github()
    new_tools.extend([
        create_staging_entry(
            name=tool['name'],
            link=tool.get('link', ''),
            description=tool.get('description', ''),
            source='GitHub',
            discovered_date=datetime.now().isoformat(),
        )
        for tool in github_tools
    ])

    # Product Hunt discovery
    ph_tools = discover_tools_product_hunt()
    new_tools.extend([
        create_staging_entry(
            name=tool['name'],
            link=tool.get('link', ''),
            description=tool.get('description', ''),
            source='Product Hunt',
            discovered_date=datetime.now().isoformat(),
        )
        for tool in ph_tools
    ])

    # Twitter discovery
    twitter_tools = discover_tools_twitter()
    new_tools.extend([
        create_staging_entry(
            name=tool['name'],
            link=tool.get('link', ''),
            description=tool.get('description', ''),
            source='Twitter',
            discovered_date=datetime.now().isoformat(),
        )
        for tool in twitter_tools
    ])

    print(f"Discovered {len(new_tools)} potentially new tools\n")

    # Filter out duplicates (already in staging or registry)
    registry_path = Path(__file__).parent / 'web/src/data/registry.json'
    existing_names = set()

    if registry_path.exists():
        with open(registry_path, 'r') as f:
            registry = json.load(f)
            existing_names = {tool['name'].lower() for tool in registry}

    staged_names = {tool['name'].lower() for tool in staged}
    all_existing = existing_names | staged_names

    truly_new = [
        tool for tool in new_tools
        if tool['name'].lower() not in all_existing
    ]

    print(f"After dedup: {len(truly_new)} truly new tools\n")

    if truly_new:
        # Add to staging
        staged.extend(truly_new)
        save_staging_queue(staged, str(staging_path))

        print("New tools added to staging queue:")
        for tool in truly_new:
            print(f"  - {tool['name']} ({tool['source']})")

        print(f"\n✓ Staged for manual review: {len(truly_new)} tools")
        print(f"✓ Total staging queue: {len(staged)} tools")
    else:
        print("No new tools discovered.")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print("""
1. Review staged tools: registry/staging/new_tools_staging.json
2. For each tool:
   - Visit the link and verify it exists
   - Fill in: category, maturity, core_feature, differentiator
   - Decide: ACCEPT (move to registry) or REJECT
3. Run: python registry/approve_staged_tools.py
4. Rebuild Registry: npm run build && deploy
5. Announce new tools in next newsletter issue
    """)


if __name__ == '__main__':
    main()
