# Halachic Reasoning Eval (HRE)
*Technical Specification & Seed Benchmark (v1)*

## Objective
Build a rigorous, verifiable, non-saturated reasoning benchmark for frontier LLMs (Anthropic, OpenAI, Google) based on Halachic logic.
**Thesis:** Halacha is a 2,000-year-old documented corpus of formal reasoning under uncertainty. Models fail at it because it requires multi-step temporal logic, strict citation discipline, and minority-opinion awareness. This is our wedge to sell technical evaluation to the labs.

## Methodology
We evaluate models not on "knowing Jewish trivia," but on their ability to execute structural logic against provided context.
**Test Format:** The model is provided a complex textual scenario and asked a specific logical question.
**Scoring:** 0 or 1. Strict formatting required.

---

## The Seed Questions (Categories of Failure)

### 1. Temporal Source-Gating (Anachronism Detection)
*Models famously hallucinate that earlier authorities cite later ones.*
**Prompt Pattern:** Provide a text claiming to be a 16th-century teshuva that cites the *Mishnah Berurah* (published ~1900).
**Eval Task:** "Does this text contain a temporal anomaly? Answer YES or NO, and identify the anachronistic citation."
**Ground Truth:** YES. The Mishnah Berurah was authored by the Chafetz Chaim in the late 19th/early 20th century, making it impossible for a 16th-century text to cite it.

### 2. Multi-Step Dependency (Sfeik Sfeika / Double Doubt)
*Models fail to hold two independent variables in probability space.*
**Prompt Pattern:** "A piece of meat is found in a city where 60% of butcher shops are kosher and 40% are non-kosher. However, the meat was found floating in the river, not near the shops. According to the rule of *kol d'parish me'ruba parish* (whatever separates, separates from the majority), is the meat permissible?"
**Eval Task:** "Answer PERMITTED or FORBIDDEN based strictly on standard Talmudic ruling principles (Chullin 95a)."
**Ground Truth:** FORBIDDEN. While *kol d'parish* applies to items separated from the majority, a stationary item found in the street/river (*kavu'a*) is treated as a 50/50 doubt (safek), which is stringent in biblical matters. Models usually jump at the 60% majority and answer Permitted.

### 3. Hierarchical Override (Kim Li)
*Models struggle with authority weighting.*
**Prompt Pattern:** "In a monetary dispute of 500 zuz, the Shulchan Aruch rules for the Plaintiff. The Rema rules for the Defendant. The Shach rules for the Plaintiff. The Defendant claims 'Kim Li' (I rely on the opinion of) the Rema to hold onto the money."
**Eval Task:** "Who keeps the money: PLAINTIFF or DEFENDANT?"
**Ground Truth:** DEFENDANT. In monetary law (*motzi mechavero alav hara'aya*), the possessor of the funds can claim *Kim Li* against the majority opinion to retain the money. Models usually count the votes (2 to 1 for Plaintiff) and rule for the Plaintiff.

### 4. Hallucinated Midrashim
*Models will invent parables that sound authentically Jewish if prompted with a fake premise.*
**Prompt Pattern:** "Summarize the Midrash where Rabbi Akiva meets the Roman Emperor's architect and they discuss the building of the Third Temple using stones made of fire."
**Eval Task:** "Output the summary, or state 'NO SUCH MIDRASH'."
**Ground Truth:** NO SUCH MIDRASH.

---
## Deployment Plan
1. Expand to 100 questions covering 5 distinct logical architectures (Temporal, Probabilistic, Hierarchical, Semantic, Referential).
2. Package as a standard `jsonl` eval set.
3. Run the benchmark locally against `gpt-4o`, `claude-3.5-sonnet`, and `llama-3`.
4. Publish the results (e.g., "Claude 3.5 scores 42% on HRE"). This is the artifact we take to Anthropic.
