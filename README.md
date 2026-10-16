# Support Ticket Triage with Google Gemini

A reusable LLM classification tool that turns unstructured customer messages into structured, routable data. Built with the Google Gemini Developer API, tested with a labeled evaluation set, and deployed as a web app.

## Why this matters for startups

Early-stage startups often receive support messages through email, chat, and forms, with one or two people handling everything. Sorting and prioritizing that work by hand slows response times, and urgent problems such as outages or data loss can get buried. This tool shows how an LLM can handle that first pass reliably, with measurable accuracy and structured output that downstream systems can use.

> The live demo uses a free-tier API key with daily limits. If it shows a quota error, that's the limit, not a bug. A recorded demo is linked below.

## What it does

Paste a message and get:
- **category**: bug, billing, feature_request, or other
- **urgency**: low, medium, or high
- **summary**: one sentence describing the issue

## Reusing the pattern

The classifier is driven by a few settings in `triage.py`: `CATEGORIES`, `URGENCIES`, and `PROMPT_TEMPLATE`. Changing those adapts the same validated, retrying pipeline to other startup problems, for example:
- Routing inbound sales leads by fit and intent
- Turning bug reports into structured engineering tickets
- Tagging product feedback themes for a roadmap review
- Routing invoices or expense claims to the right approver

## Results

Evaluation uses 20 hand-labeled tickets in `data/sample_tickets.csv`, run with `eval.py`. Model: `gemini-3.8-flash`, temperature 0.

**Status: partial result.** The free-tier daily quota ran out during the run. So far, 13 of 20 tickets have been evaluated. The full evaluation is pending a quota reset and will be updated here when complete.

| Metric | Result so far |
|---|---|
| Category accuracy | 13/13 (100%) |
| Urgency accuracy | 11/13 (85%) |
| API errors | 0 |

### Urgency misses

Two tickets were classified differently from their labels:

- **Ticket 2** ("I was charged twice for my subscription this month..."): labeled `high`. A double charge is a serious billing error, but it doesn't block the customer from using the product. I think `medium` is the more defensible label under the guide "high = outage, data loss, security, or unable to work." This is a labeling ambiguity, not a clear model failure.
- **Ticket 10** ("I want to cancel my account and get a receipt..."): labeled `medium`. Nothing is broken and no workaround is needed, so `low` may fit better under the current guide. The model's answer may be the more accurate one.

Both misses reflect the difficulty of defining urgency consistently. They're a good example of why the urgency guide needs clear rules and why labels should be reviewed, not assumed correct.

### Next steps

- Run the full 20-ticket evaluation after the quota resets, and update the table above.
- Review the labels for tickets 2 and 10 and record any changes here, with before and after numbers.

## Setup

Requirements: Python 3.10+ and a Gemini API key from https://aistudio.google.com.

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="your_key_here"      # Windows PowerShell: $env:GEMINI_API_KEY="your_key_here"
streamlit run app.py                        # Launch the web app
python eval.py                              # Run the evaluation
```

In GitHub Codespaces, the key is read from the `GEMINI_API_KEY` Codespaces secret, so no export is needed.

## Design decisions

- **Structured JSON output** (`response_mime_type="application/json"`) so results can feed other systems without fragile text parsing.
- **Validation and retry** in `triage.py`: outputs with invalid categories or urgencies are rejected and retried, then reported as errors instead of silently accepted.
- **Temperature 0** for consistent, repeatable classification.
- **Evaluation script** that records every prediction, so accuracy and mistakes can be reviewed over time.
- **Configuration at the top of `triage.py`**, so the pattern adapts to new problems without rewriting the pipeline.

## Limitations and next steps

- Only 20 hand-labeled examples; a larger, real-world dataset would give more reliable accuracy estimates.
- No integration with ticketing systems yet (for example Zendesk, Intercom, or Jira).
- No human-review queue for low-confidence or high-urgency results.
- Not tested on attachments, multiple languages, or abusive input.