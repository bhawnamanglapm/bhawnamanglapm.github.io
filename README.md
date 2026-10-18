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

## Connect
[LinkedIn](https://www.linkedin.com/in/bhawnamangla/) · [Email](mailto:bhawna202019@gmail.com)
