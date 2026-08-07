import json
from collections import defaultdict

def main():
    results_path = '/Users/elieschulman/Projects/AI-plus-Orthodoxy-Platform-Option-Map/benchmark/hre_results.jsonl'
    
    gpt_by_archetype = defaultdict(lambda: {'correct': 0, 'total': 0})
    claude_by_archetype = defaultdict(lambda: {'correct': 0, 'total': 0})
    
    sample_failures = []
    claude_samples = []
    
    with open(results_path, 'r') as f:
        for line in f:
            item = json.loads(line)
            arch = item['archetype']
            
            gpt_score = item.get('gpt-4o_score', 0)
            claude_score = item.get('claude-3.5-sonnet_score', 0)
            
            gpt_by_archetype[arch]['total'] += 1
            gpt_by_archetype[arch]['correct'] += gpt_score
            
            claude_by_archetype[arch]['total'] += 1
            claude_by_archetype[arch]['correct'] += claude_score
            
            if gpt_score == 0 and len(sample_failures) < 2:
                sample_failures.append(item)
            if len(claude_samples) < 2:
                claude_samples.append(item)

    print("=== GPT-4o Breakdown by Archetype ===")
    for arch, stats in gpt_by_archetype.items():
        pct = (stats['correct'] / stats['total']) * 100
        print(f"{arch}: {stats['correct']}/{stats['total']} ({pct:.1f}%)")
        
    print("\n=== Claude 3.5 Sonnet Breakdown by Archetype ===")
    for arch, stats in claude_by_archetype.items():
        pct = (stats['correct'] / stats['total']) * 100
        print(f"{arch}: {stats['correct']}/{stats['total']} ({pct:.1f}%)")

    print("\n=== Why did GPT-4o fail? (Sample) ===")
    for s in sample_failures:
        print(f"Archetype: {s['archetype']}")
        print(f"Ground Truth Expected: {s['ground_truth']}")
        print(f"GPT-4o Output: {s['gpt-4o_response']}\n")

    print("=== Why did Claude 3.5 score 0%? (Sample) ===")
    for s in claude_samples:
        print(f"Archetype: {s['archetype']}")
        print(f"Ground Truth Expected: {s['ground_truth']}")
        print(f"Claude Output: {s['claude-3.5-sonnet_response']}\n")

if __name__ == '__main__':
    main()
