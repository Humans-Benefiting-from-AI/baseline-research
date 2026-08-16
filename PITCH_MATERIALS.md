# Baseline Research: Pitch Materials

## One-Pager 1: AI Diligence Services Pitch (For Foundations)

**File:** `pitch_foundation_diligence.txt`

```
TECHNICAL AI DILIGENCE FOR JEWISH ORGANIZATIONS
Baseline Research

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE PROBLEM

Jewish organizations are rapidly adopting AI tools—from learning platforms to 
administrative systems—without independent technical evaluation. How do you know 
if a tool is:

- Actually reasoning correctly vs. faking understanding?
- Handling sensitive data securely?
- Perpetuating biases in halakhic interpretation or community-specific contexts?
- Compliant with Jewish values and institutional requirements?

Vendor claims and generic AI audits miss these specifics. You need evaluation 
grounded in Jewish institutional reasoning.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE SOLUTION

Baseline Research provides technical diligence specifically for Jewish organizations:

1. MODEL EVALUATION
   We test your chosen AI tools against the Halachic Reasoning Evaluation (HRE)—
   a 100-question benchmark that exposes reasoning failures in frontier models.
   
   Result: A detailed report showing exactly where the model fails and why.

2. INSTITUTIONAL BIAS AUDIT
   We analyze the tool's training data and design for biases specific to:
   - Jewish legal reasoning
   - Community demographics and norms
   - Institutional use cases (education, governance, learning)
   
   Result: A roadmap of risks and mitigation strategies.

3. SECURITY & COMPLIANCE REVIEW
   We evaluate data handling, encryption, vendor credibility, and compliance 
   with institutional requirements (HIPAA, FERPA, or internal standards).
   
   Result: Go/no-go recommendation with specific security requirements.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUR AUTHORITY

- Independent Registry of 110+ Jewish AI tools (rigorous, public evaluation)
- HRE Benchmark: Proves frontier models fail at formal halakhic reasoning
- Team expertise: Talmudic scholars + AI researchers + security engineers
- Zero vendor relationships (no conflicts of interest)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TYPICAL ENGAGEMENT

Scope        | Effort    | Timeline  | Cost
-----------  | --------  | --------  | -----
Tool Audit   | 2-3 weeks | 1 month   | $5k-10k
Deep Audit   | 4-8 weeks | 2-3 mo    | $15k-25k
Institutional | 8-12 wks  | 3-6 mo    | $30k-50k+

(Custom scopes available)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS

1. Schedule a 30-min call to discuss your needs
2. We'll propose a specific audit scope
3. You get a detailed report + recommendations
4. Results inform your procurement/deployment decisions

Interested? Reply to this email or visit: [YOUR SITE]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Baseline Research | Independent • Empirical • Judgment-Based
```

---

## One-Pager 2: HRE Custom Evaluation (For AI Labs)

**File:** `pitch_ai_lab_hre.txt`

```
HALACHIC REASONING EVALUATION (HRE)
A Pristine Benchmark for AI Safety Testing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE PROBLEM WITH CURRENT REASONING BENCHMARKS

Standard AI benchmarks (MATH, GSM8K, ARC) test:
- Raw computation
- Memorized algorithms
- Statistical inference

They do NOT test:
- Structured logical reasoning under constraints
- The ability to suppress statistical inference when formal rules require it
- Multi-step dependency reasoning
- Authority hierarchies and rule overrides

Result: Models can score 90%+ on reasoning benchmarks while failing at basic 
structural logic.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE SOLUTION: HALACHIC REASONING EVALUATION (HRE)

HRE is a 100-question benchmark grounded in 2,000 years of formal Jewish law. 
It tests four distinct failure modes:

1. HALLUCINATION DETECTION
   Can the model refuse to cite sources that don't exist?
   
2. TEMPORAL REASONING
   Can the model detect anachronistic citations and time-based impossibilities?

3. HIERARCHICAL LOGIC
   Can the model understand and apply rule priorities when multiple rules conflict?

4. STRUCTURAL CONSTRAINT SUPPRESSION ⭐ (THE KEY FINDING)
   Can the model suppress statistical inference when a formal constraint 
   (like Kavu'a in Halacha) explicitly requires it?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHY HALACHA IS BETTER THAN SYNTHETIC TESTS

✓ Unsaturated ground truth (2,000-year corpus, no model training contamination)
✓ Rigorous formal system (actual logical structure, not made-up puzzles)
✓ Real-world stakes (reasoning failures matter in law, medicine, compliance)
✓ Generalizable (tests logical structure, not Jewish-specific content)
✓ Published dataset (open, reproducible, testable by any lab)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EXISTING RESULTS

Model           | Overall Acc. | Hallucination | Temporal | Hierarchy | Kavu'a
----------------|--------------|--------------|----------|-----------|-------
GPT-4o          | 83%          | 100%         | 100%     | 100%      | 32% ⚠️
Claude-3.5      | [Testing]    | [Testing]    | [Testing]| [Testing] | [Test]

The Kavu'a failure (32%) exposes a critical architectural weakness: models cannot 
suppress statistical reasoning when formal logic requires it.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT WE'RE OFFERING

1. OPEN BENCHMARK (CC-BY-NC-SA)
   - 100-question dataset: hre_eval_100.jsonl
   - Evaluation harness: run_evals.py
   - Full methodology and results

2. CUSTOM TESTING (Optional)
   - We run HRE against your models (as needed)
   - Detailed breakdown by failure mode
   - Competitive comparison (you vs. GPT-4o, Claude, etc.)

3. EXTENSION WORK (Optional)
   - Add questions to probe specific capabilities
   - Test fine-tuned or instruction-following variants
   - Develop Halacha v2 (expert extraction) dataset together

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NEXT STEPS

1. Download & run HRE against your models
   → github.com/humans-benefiting-from-ai/baseline-research

2. Share results with us for competitive benchmarking

3. Discuss collaboration on formal reasoning improvements

Questions? Contact: [YOUR EMAIL]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Baseline Research | Independent • Empirical • Judgment-Based
```

---

## One-Pager 3: Newsletter Sponsorship (For Tool Creators)

**File:** `pitch_newsletter_sponsor.txt`

```
BASELINE: AI + JUDAISM WEEKLY
Sponsor a Deep-Dive Analysis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THE OPPORTUNITY

Baseline publishes a weekly technical deep-dive on Jewish AI tools to an 
engaged audience of:

- Tech-forward educators & institutional decision-makers
- Talmudic scholars interested in AI
- Jewish community leaders evaluating tools
- AI researchers studying religious reasoning

Each week: 1,000-2,000 email subscribers, Twitter share to 5,000+ followers.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

YOUR TOOL, ANALYZED

Is your tool in the Registry? We're analyzing 110 Jewish AI tools over the 
next two years. When we cover yours, you can sponsor the analysis.

What sponsorship includes:

1. YOUR FEATURED ANALYSIS (No editorial compromise)
   - Honest, rigorous evaluation of your tool
   - Highlight strengths and weaknesses
   - Explain use cases and limitations
   
2. YOUR STORY (Guest section)
   - Why you built it
   - What problem it solves
   - Who should use it
   
3. PROMINENT PLACEMENT
   - Featured in weekly email (12,000+ impressions)
   - Pinned social shares (Twitter + LinkedIn)
   - CTA link to your site

4. AUDIENCE ENGAGEMENT
   - Q&A with subscribers
   - Feature on Baseline podcast (coming soon)
   - Invite to Baseline community call

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SPONSORSHIP TIERS

GOLD SPONSOR ($2,500)
- Full-length featured analysis (1,500+ words)
- Guest post from your founder/CEO
- Social promotion + email feature
- Brand mention in footer
- 3-month link from Registry to your site

SILVER SPONSOR ($1,000)
- Sponsored segment within weekly analysis
- Brief guest statement
- Email + social promotion
- Logo in footer

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EDITORIAL INDEPENDENCE

To be clear: Baseline maintains full editorial independence. We won't:
- Hide or minimize weaknesses in your tool
- Fake enthusiasm or results
- Make claims you don't support

Sponsorship is transparent: readers see the full analysis, including 
limitations and competitive alternatives. Sponsorship buys visibility, 
not favorable coverage.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INTERESTED?

1. Email: [YOUR EMAIL] with your tool name
2. We schedule a 20-min call
3. You see the proposed analysis outline
4. You decide if it's worth sponsoring
5. We publish (with your guest contribution if sponsored)

No payment required until after publication if you're not satisfied.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Baseline Research | Independent • Empirical • Judgment-Based
```

---

## Customization Notes

Each one-pager should be:
1. **Personalized** with recipient name/organization
2. **Date-stamped** with current metrics (e.g., "110 tools in Registry," "500+ newsletter subscribers")
3. **Linked** to your actual contact info and Registry
4. **Toned** to match recipient (formal for foundations, technical for AI labs, casual for tool creators)

---

## Email Templates

### To Maimonides & Jewish Foundations

```
Subject: Independent AI Diligence for Jewish Organizations

Dear [Name],

We're reaching out because your institution is likely evaluating or deploying 
AI tools. How do you know if those tools are sound?

Baseline Research provides technical diligence specifically for Jewish organizations—
evaluating reasoning quality, institutional bias, and security through the lens of 
Jewish values.

We've built:
- A rigorous Registry of 110 Jewish AI tools
- The Halachic Reasoning Evaluation (HRE) benchmark—proving frontier models fail 
  at structural reasoning
- A team of Talmudic scholars + AI researchers

I'm attaching a one-pager on how we work with foundations. I'd love to discuss 
whether this is useful for [YOUR INSTITUTION].

Are you free for a 20-minute call next week?

Best,
Elie Schulman
Baseline Research

P.S. We're independent, have no vendor relationships, and don't take sides in 
religious debates. We just measure what works and what doesn't.
```

### To OpenAI & Anthropic Safety Teams

```
Subject: HRE Benchmark—A Pristine Dataset for Reasoning Evaluation

Hi [Name],

We've built a new reasoning benchmark grounded in Halacha that exposes a critical 
failure mode in frontier models: they cannot suppress statistical inference when 
formal constraints require it.

The Halachic Reasoning Evaluation (HRE) v1 shows that GPT-4o scores 83% overall, 
but only 32% on a specific class of multi-step probability reasoning (Kavu'a).

- Dataset: hre_eval_100.jsonl (CC-BY-NC-SA, reproducible)
- Whitepaper: [LINK]
- Code: github.com/humans-benefiting-from-ai/baseline-research

We'd like to know how your models perform on HRE and discuss whether this benchmark 
is useful for your internal evaluation suite.

The dataset and code are open. Would your team be interested in testing your models 
against it?

Best,
Elie Schulman
Baseline Research
```

### To Jewish Tool Creators

```
Subject: Baseline Weekly—Your Tool Analysis (Sponsorship Opportunity)

Hi [Name],

Baseline is publishing a weekly technical deep-dive on Jewish AI tools. We cover 
110 tools over two years—roughly one per week.

[YOUR TOOL] is in our rotation. We analyze it rigorously: strengths, weaknesses, 
use cases, limitations.

You can sponsor the analysis (optional). If you do:
- You get a featured write-up to 10,000+ engaged readers
- You contribute a guest section on why you built it
- We remain completely editorially independent

Sponsorship starts at $1,000. No payment if you're not satisfied with the proposed 
outline.

Attached: One-pager on sponsorship tiers.

When would you like to see the draft outline?

Best,
Elie
```

---

## Final Notes for Elie

These one-pagers are templates. Customize them:
1. Add your actual contact email / website
2. Update metrics as you hit them (e.g., "500+ newsletters", "1,000+ tool reviews")
3. Adjust tone per recipient (formal/technical/casual as needed)
4. Reference real results (link to HRE findings, Registry, published analyses)
5. Add personal touches (mentioning their work, explaining why you're reaching out)

Send these proactively to:
- Foundation program officers (quarterly review of budget)
- AI lab safety teams (after HRE whitepaper is published)
- Tool creators (as you schedule their analysis week)

Good luck! 🏺
