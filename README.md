# Bhawna Mangla — Product Portfolio

Senior Product Manager · Fintech & B2B Platforms · Gurugram, India

🔗 **Live site:** [bhawnamanglapm.github.io](https://bhawnamanglapm.github.io)

## What's inside (as described by the owner)
- **PCMS** — 0→1 partner commission management system at Bajaj Finance (₹50,000 Cr+ deposit book)
- **Partner Portal revamp** — onboarding TAT cut from 7 days to 1 day
- **Partner Distribution OS** — flagship case study with full PRD & artifact suite
- **Weft** — Chrome MV3 extension for AI workflow intelligence (personal build)
- **90 Days to AI PM** — newsletter documenting the platform PM → AI PM transition

All figures above are the owner's own account of past work. This repository holds no employer records, so
they are not independently verified. See [docs/METRICS_EVIDENCE.md](docs/METRICS_EVIDENCE.md) for which
numbers are owner-reported, which come from modeled datasets, and where the site and the chatbot disagree.

## How the site works

- **Static site:** hand-written `index.html`, `styles.css`, `script.js`, served by GitHub Pages. No build step.
- **Case-study pages and demos:** under `projects/` (dashboards, wireframes, datasets, generators).
- **"Ask about Bhawna" chatbot:** `chatbot.js` calls a Cloudflare Worker (`cf-worker/`) that answers from a fixed
  fact sheet using Cloudflare's free Workers AI. It can be wrong; it is limited to the facts in `worker.js`.
- **Worker limits:** it accepts requests only from this site's origin and refuses oversized bodies. That is not
  authentication and there is no rate limit. Changes to `cf-worker/worker.js` take effect only after the owner
  runs `wrangler deploy`.

## Checks

```bash
node scripts/check.mjs            # local files and links exist, alt text, page basics, Worker origin policy
node cf-worker/worker.test.mjs    # Worker behavior with the AI stubbed (no account needed)
```

Both run on every push and pull request. Not checked: accessibility audit, performance, analytics and Search
Console data, and the deployed Worker's live behavior beyond a CORS preflight.

## Case-study repositories

Case studies that have files behind them (documents, datasets, prototypes) each have their own public repo, linked from their card on [travel-tech-more.html](https://bhawnamanglapm.github.io/travel-tech-more.html). The other 26 cards are written analyses with no files, so they have no repo. The `projects/` folders here are unchanged.

| Repo | Case study |
|---|---|
| [mmt-flight-booking-teardown](https://github.com/bhawnamanglapm/mmt-flight-booking-teardown) | MakeMyTrip pricing transparency teardown |
| [wayfare-ai-trip-planner-prd](https://github.com/bhawnamanglapm/wayfare-ai-trip-planner-prd) | Wayfare AI trip planner PRD |
| [travel-support-ai-copilot](https://github.com/bhawnamanglapm/travel-support-ai-copilot) | Travel Support AI Copilot |
| [opspilot-ai-ops-copilot](https://github.com/bhawnamanglapm/opspilot-ai-ops-copilot) | OpsPilot AI operations copilot |
| [verification-gap-engine](https://github.com/bhawnamanglapm/verification-gap-engine) | The Verification Gap (3 cards, shared artifacts) |
| [merchant-dispute-hub](https://github.com/bhawnamanglapm/merchant-dispute-hub) | Merchant Dispute Hub (simulation) |
| [flight-delay-prediction-dashboard](https://github.com/bhawnamanglapm/flight-delay-prediction-dashboard) | Flight Delay Prediction Dashboard (modeled data) |
| [airline-operations-dashboard](https://github.com/bhawnamanglapm/airline-operations-dashboard) | Airline Operations Dashboard (modeled data) |
| [sql-saas-analytics](https://github.com/bhawnamanglapm/sql-saas-analytics) | SQL Analytics, Basic and Advanced (2 cards) |
| [amplitude-strideway](https://github.com/bhawnamanglapm/amplitude-strideway) | Amplitude Analytics, Basic and Advanced (2 cards) |
| [partner-ops-sql-api-practice](https://github.com/bhawnamanglapm/partner-ops-sql-api-practice) | Partner Ops SQL and API practice |
| [fintech-api-landscape](https://github.com/bhawnamanglapm/fintech-api-landscape) | Fintech API landscape reference |

Weft and Career Copilot already had their own repos ([Weft](https://github.com/bhawnamanglapm/Weft), [Career_Copilot](https://github.com/bhawnamanglapm/Career_Copilot)).

## Connect
[LinkedIn](https://www.linkedin.com/in/bhawnamangla/) · [Email](mailto:bhawna202019@gmail.com)
