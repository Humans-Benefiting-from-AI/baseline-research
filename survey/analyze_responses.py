#!/usr/bin/env python3
"""
Survey Response Analysis Pipeline

Ingests raw survey responses (CSV from Typeform/Qualtrics) and produces:
1. Cross-tabulation analysis by segment (Institutional/Educator/Layperson)
2. Summary statistics and concern rankings
3. JSON output for narrative report writing
4. Charts-ready CSV exports
"""

import json
import csv
import sys
from pathlib import Path
from collections import defaultdict, Counter
from argparse import ArgumentParser
from datetime import datetime


def load_survey_data(csv_path: str) -> list[dict]:
    """Load raw survey responses from CSV."""
    responses = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            responses.append(row)
    print(f"✓ Loaded {len(responses)} responses from {csv_path}")
    return responses


def segment_responses(responses: list[dict]) -> dict[str, list[dict]]:
    """Group responses by respondent segment."""
    segments = defaultdict(list)

    for resp in responses:
        # Assume column name is "segment" or "respondent_type"
        segment = resp.get('segment') or resp.get('respondent_type') or 'Unknown'
        segments[segment].append(resp)

    print(f"✓ Segmented responses:")
    for seg, resps in segments.items():
        print(f"  - {seg}: {len(resps)} responses")

    return dict(segments)


def extract_concerns(responses: list[dict]) -> dict[str, int]:
    """Rank concerns by frequency."""
    # Assumes column like "biggest_concern" or "primary_concern"
    concerns = []

    for resp in responses:
        concern = resp.get('biggest_concern') or resp.get('primary_concern')
        if concern and concern.strip():
            concerns.append(concern.strip())

    ranked = Counter(concerns).most_common(10)
    return dict(ranked)


def extract_use_cases(responses: list[dict]) -> dict[str, int]:
    """Extract desired use cases from responses."""
    # Assumes column with comma-separated values or multi-select
    use_cases = []

    for resp in responses:
        # Try multiple column name variations
        cases = resp.get('desired_use_cases') or resp.get('use_cases')
        if cases:
            # Handle comma-separated or semicolon-separated
            items = [x.strip() for x in cases.split(',') if x.strip()]
            use_cases.extend(items)

    ranked = Counter(use_cases).most_common(15)
    return dict(ranked)


def cross_tab_concerns(segments: dict[str, list[dict]]) -> dict:
    """Build cross-tabulation of concerns by segment."""
    crosstab = {}

    for seg, responses in segments.items():
        crosstab[seg] = {
            'count': len(responses),
            'top_concerns': extract_concerns(responses),
            'desired_use_cases': extract_use_cases(responses),
        }

    return crosstab


def generate_summary_stats(responses: list[dict], segments: dict) -> dict:
    """Generate summary statistics for the full dataset."""
    return {
        'total_responses': len(responses),
        'segments': {seg: len(resps) for seg, resps in segments.items()},
        'collection_date': datetime.now().isoformat(),
        'response_rate_by_segment': {
            seg: f"{(len(resps) / len(responses) * 100):.1f}%"
            for seg, resps in segments.items()
        }
    }


def export_json(data: dict, output_path: str):
    """Export analysis results as JSON."""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✓ Exported analysis to {output_path}")


def export_crosstab_csv(crosstab: dict, output_dir: str):
    """Export cross-tabulation as CSV for charts."""
    Path(output_dir).mkdir(exist_ok=True)

    # Concerns by segment
    concerns_path = Path(output_dir) / 'concerns_by_segment.csv'
    with open(concerns_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Segment', 'Concern', 'Count'])
        for seg, data in crosstab.items():
            for concern, count in data['top_concerns'].items():
                writer.writerow([seg, concern, count])

    print(f"✓ Exported crosstab to {concerns_path}")


def main():
    parser = ArgumentParser(description='Analyze survey responses')
    parser.add_argument('--input', required=True, help='Input CSV file')
    parser.add_argument('--output', required=True, help='Output JSON file')
    parser.add_argument('--csv-dir', default='survey/exports', help='Directory for CSV exports')

    args = parser.parse_args()

    # Load and process
    responses = load_survey_data(args.input)
    segments = segment_responses(responses)
    crosstab = cross_tab_concerns(segments)
    stats = generate_summary_stats(responses, segments)

    # Compile final report
    report = {
        'summary': stats,
        'cross_tabulation': crosstab,
        'analysis_timestamp': datetime.now().isoformat(),
    }

    # Export
    export_json(report, args.output)
    export_crosstab_csv(crosstab, args.csv_dir)

    print(f"\n✓ Analysis complete!")
    print(f"  Report: {args.output}")
    print(f"  Charts: {args.csv_dir}")


if __name__ == '__main__':
    main()
