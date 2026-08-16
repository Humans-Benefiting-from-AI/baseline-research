#!/usr/bin/env python3
"""
HRE Evaluation Results Analyzer

Processes hre_results.jsonl to produce summary statistics for the whitepaper.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path


def load_results(jsonl_path: str) -> list[dict]:
    """Load JSONL evaluation results."""
    results = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    return results


def analyze_results(results: list[dict]) -> dict:
    """Compute summary statistics."""

    # Filter out errors
    valid_results = [r for r in results if 'ERROR' not in r.get('gpt-4o_response', '')]

    print(f"Total evaluations: {len(results)}")
    print(f"Valid (non-error): {len(valid_results)}")
    print(f"Error rate: {(len(results) - len(valid_results)) / len(results) * 100:.1f}%\n")

    # GPT-4o Analysis
    gpt_scores = [r.get('gpt-4o_score', 0) for r in valid_results]
    gpt_accuracy = sum(gpt_scores) / len(gpt_scores) if gpt_scores else 0

    # Archetype breakdown
    archetypes = [r.get('archetype', 'Unknown') for r in valid_results]
    archetype_counts = Counter(archetypes)

    # Accuracy by archetype
    accuracy_by_archetype = defaultdict(list)
    for r in valid_results:
        archetype = r.get('archetype', 'Unknown')
        accuracy_by_archetype[archetype].append(r.get('gpt-4o_score', 0))

    archetype_accuracy = {
        arch: {
            'count': len(scores),
            'accuracy': sum(scores) / len(scores) * 100,
        }
        for arch, scores in accuracy_by_archetype.items()
    }

    return {
        'total_evaluations': len(results),
        'valid_evaluations': len(valid_results),
        'error_rate': (len(results) - len(valid_results)) / len(results),
        'gpt-4o': {
            'overall_accuracy': gpt_accuracy * 100,
            'correct': sum(gpt_scores),
            'total': len(gpt_scores),
        },
        'archetypes': dict(archetype_counts),
        'accuracy_by_archetype': archetype_accuracy,
    }


def format_summary(analysis: dict) -> str:
    """Format analysis as markdown for whitepaper."""

    output = f"""# HRE Evaluation Results Summary

## Overall Performance

- **Total Questions Evaluated:** {analysis['total_evaluations']}
- **Valid Evaluations:** {analysis['valid_evaluations']}
- **GPT-4o Accuracy:** {analysis['gpt-4o']['overall_accuracy']:.1f}%
  - Correct: {analysis['gpt-4o']['correct']}/{analysis['gpt-4o']['total']}

## Failure Modes by Category

"""

    for archetype, stats in sorted(analysis['accuracy_by_archetype'].items(),
                                    key=lambda x: x[1]['accuracy']):
        output += f"### {archetype}\n"
        output += f"- **Count:** {stats['count']} questions\n"
        output += f"- **Accuracy:** {stats['accuracy']:.1f}%\n"
        output += f"- **Failure Rate:** {100 - stats['accuracy']:.1f}%\n\n"

    return output


def main():
    results_path = Path(__file__).parent / 'hre_results.jsonl'

    if not results_path.exists():
        print(f"Error: {results_path} not found")
        return

    results = load_results(str(results_path))
    analysis = analyze_results(results)

    # Print summary
    print("\n" + "=" * 60)
    print("HRE EVALUATION SUMMARY")
    print("=" * 60 + "\n")

    print(f"Overall GPT-4o Accuracy: {analysis['gpt-4o']['overall_accuracy']:.1f}%")
    print(f"  ({analysis['gpt-4o']['correct']}/{analysis['gpt-4o']['total']} correct)\n")

    print("Accuracy by Category:")
    for archetype, stats in sorted(analysis['accuracy_by_archetype'].items(),
                                    key=lambda x: x[1]['accuracy']):
        print(f"  {archetype:.<40} {stats['accuracy']:.1f}% ({stats['count']} q)")

    print("\n" + "=" * 60 + "\n")

    # Export markdown summary
    summary_md = format_summary(analysis)
    output_path = Path(__file__).parent / 'HRE_RESULTS_SUMMARY.md'
    with open(output_path, 'w') as f:
        f.write(summary_md)

    print(f"✓ Exported summary to {output_path}")

    # Export JSON for charts
    json_path = Path(__file__).parent / 'hre_analysis.json'
    with open(json_path, 'w') as f:
        json.dump(analysis, f, indent=2)

    print(f"✓ Exported analysis to {json_path}")


if __name__ == '__main__':
    main()
