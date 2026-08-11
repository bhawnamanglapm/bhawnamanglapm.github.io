# Portfolio chatbot backend (Cloudflare Worker)

This is the free backend that powers the "Ask about Bhawna" chat widget on
the site. It runs on Cloudflare's free tier — Workers AI gives a free daily
allowance of model calls, so there's nothing to pay and no API key to create
or protect.

You only need to do this once. It takes about 10 minutes.

## 1. Create a free Cloudflare account

Go to https://dash.cloudflare.com/sign-up and sign up (no credit card
required for the free tier used here).

## 2. Install Wrangler (Cloudflare's CLI)

You need Node.js installed. Then, from this `cf-worker/` folder, run:

```
npm install -g wrangler
wrangler login
```

`wrangler login` opens a browser tab to authorize the CLI against your new
Cloudflare account.

## 3. Deploy the Worker

From inside this `cf-worker/` folder:

```
wrangler deploy
```

This uploads `worker.js` using the settings in `wrangler.toml`, including
the `AI` binding that gives the Worker free access to Cloudflare's hosted
LLMs — no separate sign-up for that part.

When it finishes, Wrangler prints a URL that looks like:

```
https://bhawna-portfolio-chatbot.<your-subdomain>.workers.dev
```

**Copy that URL.**

## 4. Send me that URL

Paste the URL back in this chat and I'll wire it into the site's chat
widget (`chatbot.js`), commit, and push — the chatbot goes live on the next
step after that.

## Notes

- The Worker only accepts requests from `https://bhawnamanglapm.github.io`
  (CORS-restricted), so it can't be casually reused by other sites even
  though the URL is public.
- Nothing here costs money unless you deliberately upgrade the Cloudflare
  account — the free tier is enough for realistic portfolio-site traffic.
- If you ever want to take the chatbot down, you can disable or delete the
  Worker from the Cloudflare dashboard at any time — the site keeps working
  either way, it just shows a "chat's offline right now" message.
