# Who Actually Buys This

*A buyer thesis for an independent research and audit shop covering AI in Orthodox Jewish life*
Prepared 6 August 2026 · v1 · Companion to `ai-judaism-platform_option-map_v1.md` and `_independence-constraint_v1.md`

**Assumption:** you are not restricted to Orthodox institutions as customers. This document takes that seriously and goes looking elsewhere. Where I am estimating rather than reporting, it says so.

---

## Start With the Uncomfortable Arithmetic

Before naming better buyers, it is worth establishing that the obvious buyer is bad.

Prizmah's network contains 305 Jewish day schools, of which **153 are Orthodox**. Add the Haredi and Chassidic schools outside any formal network and you might reach 400–500 Orthodox schools in North America. Realistically serviceable — schools with a technology budget, an administrator who returns email, and a decision process that concludes — is closer to 200.

Run it at a generous $4,000 annual contract and an optimistic 15% penetration:

**30 schools × $4,000 = $120,000 per year.**

That is the *entire* Orthodox day school AI-software opportunity, at good execution, after two years of selling. Against it: a support burden, an implementation burden, a roadmap owned by your smallest customers, and — the part that matters — a standing obligation to stay on good terms with the exact institutions you want to write honestly about.

Shuls are worse: more fragmented, smaller budgets, no procurement function. National organizations are better on price and far worse on cycle length, and they are the entities most likely to be the subject of your reporting.

**The Orthodox institutional market is too small to be worth what it costs you.** Not marginal. Structurally too small. One specialized contract with an AI lab is worth more than five years of selling policy software to day schools, and it comes with no accountability entanglement whatsoever.

---

## The Reframe

You have been treating the Orthodox community as the market. It is the **beat**.

That is how every serious independent research organization is structured. Pew does not sell to churches. Consumer Reports does not sell to manufacturers. The ADL does not bill the platforms it measures. The subject of the work and the source of the revenue are deliberately different populations, and that separation *is* the product.

So the real question is not "which institutions will pay." It is:

**Who is harmed by the fact that nobody knows what is true here — and has money?**

Institutions are not harmed. They are blissful. Nobody at a day school lies awake over their AI vendor's data practices, which is exactly why they will not pay to find out.

Three groups are harmed, and all three have budgets.

---

## The Answer I'd Bet On

### 1. The AI labs — highest ceiling, most underrated, currently open

In May 2026, Anthropic and OpenAI sat down with religious leaders at the inaugural "Faith-AI Covenant" roundtable in New York, convened by the Geneva-based Interfaith Alliance for Safer Communities. The participants named in coverage: the Hindu Temple Society of North America, the Baha'i International Community, the Sikh Coalition, the Greek Orthodox Archdiocese of America, and the Church of Jesus Christ of Latter-day Saints. More roundtables are planned for Beijing, Nairobi, and Abu Dhabi. Anthropic had already linked outside ethical input to its Claude constitution in January 2026, with faith leaders involved in shaping that work.

Read that participant list again. **There is no Orthodox Jewish seat at that table, and the labs are actively shopping for one.**

They are not shopping out of piety. They have four concrete problems and no vendor:

- **Measured religious bias.** The ADL's *Generating Hate* work documented anti-Jewish bias across all four major models. That is a named, public, embarrassing finding with no ongoing measurement attached to it.
- **Religious-question behavior.** Models are asked halachic questions constantly and handle them badly — hallucinated midrashim, invented citations, confident psak. There is no eval for any of this.
- **Deployment policy in closed religious communities.** The Haredi ban-and-leak dynamic is a live case study in what happens when a community forbids a technology its members then use unsupervised. Labs have no framework for it.
- **Constitution and spec input** on religious content, which they have publicly committed to sourcing externally.

And here is the part I would actually lead with, because it is a technical argument rather than a communal one:

**Halacha is one of the world's most extensively documented corpora of formal reasoning under uncertainty** — multi-step, citation-disciplined, with minority opinions deliberately preserved, a two-thousand-year answer key, and explicit metadata about which authority knew what and when. Labs are running out of reasoning evals that are not math or code. A halachic reasoning benchmark is valuable *not because it is Jewish* but because it is a rigorous, verifiable, non-saturated reasoning task with ground truth.

TzadekAI's temporal source-gating is a crude hint of what that eval could look like. Nobody has built the real one.

- **What you sell:** a religious-content eval suite, an ongoing bias measurement contract, red-team work on religious-domain failure modes, domain expert data, policy consultation.
- **Price:** specialized eval and red-team engagements at frontier labs run into six figures. *Estimate, not a quote — verify before modeling.*
- **Why it fits the constraint:** selling to Anthropic creates zero accountability to any Orthodox institution. Different axis entirely. You can audit the OU on Monday and ship an eval on Tuesday.
- **New conflict it does create:** you cannot then credibly critique the labs. Disclose it, scope your beat to Jewish products rather than frontier models, and it holds.
- **Sales reality:** slow, relationship-driven, and requires a technical artifact before a conversation. Build the benchmark first, then find the door.

### 2. Foundations — warmest near-term money, funds the work directly

Maimonides is running a national Judaism-and-AI RFP with 12-month grants from $18,000 to $250,000, explicitly naming rabbi and educator tooling, Jewish-content concierges, and historical-voice LLMs. The Israeli Innovation Authority put roughly $1M into JEDAI.

Money is now flowing into a category where **no funder has any technical diligence capacity whatsoever.** A program officer reading an "AI Maimonides" proposal has no way to distinguish a real retrieval architecture from a demo with a good deck.

- **What you sell:** pre-grant technical diligence, portfolio review retainers, commissioned landscape studies before an RFP goes out, post-grant evaluation. Plus the research itself as a straight grant.
- **Why it fits:** foundations *pay for independence*. It is the thing they are buying. Your constraint is a qualification.
- **Honest limit:** perhaps a dozen relevant funders. Relationship-bound and slow. A good $100–200K/yr leg, not a company.

### 3. Individuals — small, slow, and structurally elegant

A paid subscription bought by a head of school **personally** is not an institutional relationship. No procurement, no board, no obligation, and you can write about their school next month. That sidesteps the entire accountability problem by construction.

Realistic universe: 500–2,000 people worldwide who would pay $150–300/yr — heads of school, shul rabbis, Jewish tech people, program officers, journalists. Call it $75–300K at maturity, over years.

It will not fund the business. It will do something more useful: it proves the work has an audience the other two buyers care about reaching.

---

## Four More I Would Keep Warm

**Litigation and expert testimony.** The Ohrbit analysis reads like a plaintiff's expert report. The FTC settled Kochava in May 2026 with religious organizations named as a protected sensitive-location category. When a religious app has an incident — and one will — the expert who understands both the retrieval stack and why a shailah log is not a preference signal does not currently exist. Lumpy, high-rate, enormous credibility amplifier.

**Builders' pre-launch audits.** Real, but thin. Most of the 110 projects in the Sefaria showcase are unfunded side projects. Maybe 10–15 have money. A $150K ceiling and you burn goodwill with the people you also cover. Take it opportunistically; do not build for it.

**Insurers.** Structurally the correct buyer for an audit shop — whoever holds the risk buys the risk data. If a day school's AI vendor leaks student records, the school's cyber policy eats it. This market is two to three years early in this niche. Worth knowing it exists.

**Dataset licensing.** If you run the annual survey, year three of longitudinal data is worth ten times year one, and the buyers are the labs, funders, vendors, and academics you are already talking to. This is the asset that compounds while you sleep.

---

## The Biggest Idea in This Document

**Everything you would build for Judaism generalizes to religion, and the religion-scale version is roughly fifty times the market.**

Your Ohrbit finding — that religious search history is uniquely sensitive and that the default consumer ad-tech configuration is catastrophically wrong for it — is not a Jewish finding. It is a general finding you happened to discover in a Jewish case. The supporting evidence in your own piece is mostly Catholic and Muslim: Burrill, Catholic Laity and Clergy for Renewal, Muslim Pro, Salaat First, Pray.com.

The reusable assets are denomination-neutral:

- A religious-data privacy standard and audit methodology
- A framework for institutional AI policy in a tradition with textual authority
- The refusal pattern for authoritative religious questions
- A religious-reasoning benchmark methodology
- Measured bias-by-tradition across frontier models

Every buyer in this document gets larger. The labs need cross-religious policy, not Jewish policy. Foundations exist in every tradition, and the Catholic ones have live scar tissue from Burrill and real budgets. The Faith-AI Covenant's next stops are Beijing, Nairobi, and Abu Dhabi.

**Structure:** the Jewish work is the flagship and the proving ground; the method is the export. You are the shop that did the hardest version first — the tradition with the most complex textual authority structure and the most documented internal disagreement — and everything else is downhill from there.

That framing also solves the credibility problem your independence constraint creates. Standing you cannot get from a haskamah, you can get from being the person the labs call.

---

## The Un-See-It

**Institutions buy comfort. Everyone else buys accuracy.**

A day school buying AI policy software is buying the feeling of having handled it. A foundation buying diligence, a lab buying an eval, and a reader buying a subscription are all buying the thing being *true*.

Your independence constraint makes you a bad comfort vendor. It makes you an unusually good accuracy vendor. The constraint was never the problem — it was the market you were pointing it at.

---

## What I'd Build First

Given all of the above, the sequencing writes itself.

1. **Ship the registry.** Free, public, 110 entries, honest. Cheapest possible proof that you have judgment. You already have the raw material.
2. **Run the survey.** The first Orthodox AI adoption and attitudes study. This is the most fundable single artifact in the document and the fastest path to being cited.
3. **Build the halachic reasoning benchmark.** The technical artifact that opens the lab conversation. Do not try to get the meeting first — build the thing, publish it, and the meeting comes to you.
4. **Publish weekly** the entire time. It is not revenue; it is how all three buyers find out you exist.
5. **Take audits and expert work opportunistically** as they arrive.

Twelve to eighteen months of that produces an organization with empirical, technical, and editorial authority, no accountability to anyone in the community it covers, and three revenue lines none of which are the day schools.

---

## The Strongest Objection to My Own Answer

The lab thesis is the highest-value leg and the least proven. It rests on an inference — that the labs will pay a solo shop for religious-domain evaluation — supported by their demonstrated interest (the Faith-AI Covenant, Anthropic's external constitutional input) but not by any known contract of this kind.

It could fail three ways: labs may source religious input through free advisory councils rather than paid vendors; they may prefer large established institutions to individuals; and eval procurement at frontier labs may be closed to unsolicited approaches entirely.

**The mitigation is the sequencing above.** Steps 1, 2, and 4 are worth doing regardless of whether the lab thesis holds, and they are exactly what makes step 3 credible. If the labs never buy, you still have a funded research shop with a publication. If they do, you have a company.

Do not restructure around the lab thesis until one of them takes a meeting.

---

## Sources

- [OpenAI, Anthropic just met with religious leaders at the 'Faith-AI Covenant'](https://www.fastcompany.com/91538977/openai-anthropic-just-met-religious-leaders-faith-ai-covenant-heres-why) — Fast Company, May 2026
- [Anthropic and OpenAI Join Faith-AI Roundtable in New York](https://winbuzzer.com/2026/05/11/anthropic-and-openai-join-faith-ai-roundtable-in-new-york-xcxwbn/) — WinBuzzer, May 2026
- [Jewish day school enrollment is rising across denominations](https://www.jta.org/2026/06/26/united-states/jewish-day-school-enrollment-is-rising-across-denominations) — JTA, June 2026 (Prizmah network: 305 schools, 153 Orthodox)
- [Jewish Day School Market Penetration Rates in the United States](https://prizmah.org/knowledge/resource/jewish-day-school-market-penetration-rates-united-states) — Prizmah
- [Request for Proposals: Judaism and Artificial Intelligence](https://maimonidesfund.org/request-for-proposals-judaism-and-artificial-intelligence/) — Maimonides Fund
- [Jewish world cannot afford to leave AI education to Silicon Valley](https://www.jpost.com/opinion/article-897646) — Jerusalem Post (JEDAI / Israeli Innovation Authority)
- Internal: `Ohrbit — Deep Dive` (FTC v. Kochava, Burrill, Muslim Pro, Salaat First, Pray.com)
- Internal: `sefaria_poweredby_projectanalysis_v1` (110-project landscape)

## Unverified

- **Six-figure eval contract pricing at frontier labs is an estimate**, not a sourced figure. Verify before it appears in any model or pitch.
- Whether any Jewish organization participated in the Faith-AI Covenant roundtable could not be confirmed; coverage named five other traditions and did not list one. **Absence from coverage is not proof of absence from the room.** Check before using this publicly.
- The ADL *Generating Hate* findings are cited from the existing 18Forty playbook and were not re-verified in this session.
- Total Orthodox day school count outside the Prizmah network is my estimate. Torah Umesorah would have the real number.
- Maimonides RFP round status as of August 2026 not confirmed.
