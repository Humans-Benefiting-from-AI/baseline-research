# Whitepaper: Frontier Models Fail at 2,000-Year-Old Formal Logic
*Why Halachic Reasoning is the Missing AI Safety Evaluation*

**By Baseline Research**

## 1. The Executive Summary
- **The Problem:** Current reasoning benchmarks (like MATH or GSM8K) test raw computation or coding ability. They do not test a model's ability to hold conflicting multi-step rules, weight hierarchical authorities, or suppress statistical probability in favor of structural law.
- **The Solution:** Halacha (Jewish Law) is a 2,000-year-old, heavily documented corpus of formal reasoning under uncertainty. It serves as a pristine, un-saturated ground-truth dataset for complex logical operations.
- **The Finding:** In our Halachic Reasoning Evaluation (HRE), GPT-4o scored 83% overall, but failed catastrophically (32%) on specific multi-step dependency rules, defaulting to raw statistics instead of structural constraints.

## 2. The Kavu'a Failure (The Core Evidence)
- Explain the test: 80% of shops are kosher, 20% are not. Meat is found stationary in the street. 
- GPT-4o's response: "PERMITTED. Because 80% is the majority."
- The structural reality: Stationary objects (*Kavu'a*) are legally treated as exactly 50/50, overriding the 80% statistic.
- **The AI Safety Takeaway:** When models encounter statistical majorities, their probability training overrides explicit structural constraints. In legal or medical compliance contexts, this failure mode is dangerous.

## 3. Why This Matters to AI Labs
- AI Labs are currently convening "Faith-AI Roundtables" to solve religious bias and handle religious queries. 
- Currently, they evaluate religious queries for "offensiveness" or "safety." They do not evaluate them for **structural logical integrity.**
- Baseline Research provides the evaluation harness to measure this.

## 4. The Call to Action (The Pitch)
- Baseline Research offers dedicated red-teaming, dataset licensing, and continuous evaluation for religious-domain reasoning.
