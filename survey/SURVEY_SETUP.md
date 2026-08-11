# Orthodox AI Adoption Survey: Setup & Configuration Guide

## Overview
This guide walks through setting up the three-network survey on Typeform or Qualtrics with zero IP tracking compliance.

## Survey Specification Reference
See `orthodox-ai-adoption-survey_v1.md` for the full question set, branching logic, and methodology.

## Platform Setup: Typeform (Recommended)

### Why Typeform?
- No IP tracking by default
- Built-in privacy compliance
- Free tier sufficient for 500+ responses
- Easy webhook integration for automated data export

### Step 1: Create Typeform Account
1. Go to [typeform.com](https://typeform.com)
2. Sign up (free tier works for this survey)
3. Create a new form

### Step 2: Add Questions
Copy questions from `orthodox-ai-adoption-survey_v1.md` into Typeform. Structure:

**Section 1: Demographics**
- Segment: Institutional / Educator / Layperson
- Role/Organization (if applicable)
- Age range
- Technical proficiency

**Section 2: Current AI Usage**
- Which tools do you use? (Multi-select from Registry)
- Frequency of use
- Primary use cases

**Section 3: Concerns & Barriers**
- Biggest concern about AI in Jewish life
- Halakhic concerns (ranked)
- Privacy concerns
- Technical barriers

**Section 4: Opportunities**
- Which use cases would you find most valuable?
- How would you want to be involved?

### Step 3: Privacy & Compliance
In Typeform settings:
1. Go to **Settings → GDPR**
2. Enable "Do not collect IP addresses"
3. Enable "Show privacy policy"
4. Add link to your privacy policy

**Privacy Policy Template:**
> This survey does not collect IP addresses or personal identifying information beyond what you choose to share. Responses are used for research purposes only and will not be shared with third parties. You can withdraw at any time by closing this form.

### Step 4: Distribution Links
Create 3 separate forms for segment targeting:

```
Institutional: https://yourform.typeform.com/to/xxxxx-institutional
Educator: https://yourform.typeform.com/to/xxxxx-educator
Layperson: https://yourform.typeform.com/to/xxxxx-general
```

(Typeform auto-generates these; copy from Share settings)

### Step 5: Webhook Setup (Automated Data Export)
In Typeform **Connect** → **Webhooks**:
1. Add webhook to your server or to Zapier
2. Event: "New response"
3. Webhook will POST responses to your collection endpoint

---

## Alternative: Qualtrics Setup

If using Qualtrics for more advanced branching:

1. Create study in Qualtrics
2. Add survey questions from spec
3. Set branching logic for segment routing
4. In **Survey → Options → Privacy → Anonymize Responses**: Enable
5. Disable IP logging: **Survey → Tools → IP Address Tracking**: Off
6. Export responses via **Data & Analysis → Export**

---

## Data Collection: Manual Export Process

If you don't set up webhooks:

### Weekly Export Ritual
1. Log into Typeform/Qualtrics
2. Go to **Responses**
3. Download as CSV (include metadata: timestamp, form section)
4. Save to: `survey/responses/raw_YYYYMMDD.csv`
5. Run analysis pipeline (see below)

---

## Data Ingestion Pipeline (Python)

Once responses are collected, the analysis pipeline:

```bash
cd survey
python analyze_responses.py --input responses/raw_YYYYMMDD.csv --output analysis_YYYYMMDD.json
```

The pipeline:
1. Ingests CSV
2. Segments responses (Institutional / Educator / Layperson)
3. Cross-tabs concerns by segment
4. Generates summary statistics
5. Creates JSON output for report writing

See `analyze_responses.py` for implementation.

---

## Expected Timeline & Response Targets

| Week | Action | Target |
|------|--------|--------|
| Week 1-2 | Form setup + QA | Survey live & tested |
| Week 2-3 | Distribute to networks | 500+ responses |
| Week 4 | Data analysis | Cross-tabs by segment |
| Week 5 | Write narrative report | Report ready |
| Week 6 | Distribute to journalists/foundations | Launch coverage |

---

## Sample Invite Email Template

```
Subject: Help Shape the Future of AI in Jewish Life

Dear [Network],

We're conducting the first independent survey on how Jewish communities are adopting and thinking about AI. Your voice matters.

🔗 Take the survey (5-10 min): [LINK]

We collect NO IP addresses or identifying info. Your responses inform a research report we're publishing on AI adoption in Orthodox communities.

Privacy: Your data is anonymous and will not be shared with third parties.

Thanks for your time,
Baseline Research
```

---

## Compliance Checklist
- [ ] IP tracking disabled
- [ ] Privacy policy displayed
- [ ] Consent to use responses confirmed
- [ ] Data stored securely (password-protected)
- [ ] Export encrypted when sharing externally
- [ ] GDPR-compliant data retention (delete after 1 year if no consent to keep)

---

## Questions?
Refer to Typeform docs: https://www.typeform.com/help/ or Qualtrics docs: https://www.qualtrics.com/support/
