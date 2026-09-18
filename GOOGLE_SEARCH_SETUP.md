# Getting This Site Found on Google — What We Did and Why

A plain-English walkthrough of a real problem this portfolio had, how we found the
cause, and how we fixed it. Written so it makes sense even if you've never touched
Search Console before — future me included.

---

## The problem

Every week, this site's analytics (Google Analytics) get checked to see how many
people are visiting, and where they're coming from. One week, the numbers showed
something odd: **zero visitors from Google Search.** Every single visit was coming
from either typing the link directly or from LinkedIn — nobody was finding this
site by searching Google.

## Step 1 — Prove it, don't assume it

Before fixing anything, we confirmed the problem was real. Searching Google for
`site:bhawnamanglapm.github.io` (a special search that lists every page Google has
indexed for a site) came back with **nothing** — not even the homepage. Searching
for "Bhawna Mangla Product Manager portfolio" didn't surface the actual site either,
only the GitHub code repository behind it.

**Conclusion:** it's not that people are searching and not clicking — the site
simply isn't in Google's index yet, so there's nothing to click on.

## Step 2 — Rule out an actual bug

Before assuming Google just hadn't gotten around to it, we checked whether
something on the site was actively *blocking* Google from crawling it. All of
these were checked and were fine:

| Check | What it does | Result |
|---|---|---|
| `robots.txt` | Tells search engines which pages they're allowed to visit | ✅ Allows everything |
| `sitemap.xml` | A list of the site's pages, handed to Google to make crawling easier | ✅ Present, listing the main pages |
| `<meta name="robots" content="index, follow">` | An explicit "yes, please index this page" signal | ✅ Present |
| Page title, description, canonical link | Standard SEO basics Google looks for | ✅ All present and correct |

So the site itself had nothing wrong with it — it was simply invisible to Google
because nothing had ever told Google to come look.

## Step 3 — Understand why that happens

Google doesn't automatically know a new website exists. It finds new sites one of
two ways:
1. **Someone tells it directly**, via a tool called **Google Search Console**.
2. **It stumbles onto it** by following a link from a page it already knows about
   (a "backlink"). This site had none — nothing on the open web linked to it yet.

Since neither had happened, the site was sitting there, fully working, completely
invisible to search.

## Step 4 — Set up Google Search Console

[Google Search Console](https://search.google.com/search-console) is a free tool
Google provides so a site owner can tell Google "this is my site, please crawl it."

**The one tricky part:** Search Console lets you add a site two different ways —

- **Domain property** (just `bhawnamanglapm.github.io`) — this only lets you prove
  ownership through your domain's DNS settings. That doesn't work here, because
  `github.io` itself belongs to GitHub, not to this site — there's no DNS to add a
  record to.
- **URL-prefix property** (`https://bhawnamanglapm.github.io/`) — this lets you
  prove ownership other ways, like a small code snippet on the page itself.

The first attempt used the wrong one (Domain), which is why it failed with
*"We couldn't find your verification token in your domain's TXT records."* Adding
it again as a **URL-prefix property** instead fixed it immediately.

## Step 5 — Prove ownership of the site

To stop just anyone from claiming your site in Search Console, Google needs proof
you actually control it. We added a small tag to the site's code:

```html
<meta name="google-site-verification" content="i-zsQQKO4mjH6tpYrJLSWciWc8RHjUN6C4RS62DzRoA">
```

This sits in the invisible `<head>` section of the homepage — a visitor never sees
it, but Google can check for it to confirm ownership.

In the end, Google verified ownership automatically through the **Google
Analytics** connection already on the site (since that's also tied to the same
Google account) — so the meta tag ended up being a backup method rather than the
one actually used. Both are now in place, which is good: Search Console
recommends having more than one verification method, in case one ever breaks.

**Important:** don't remove the Google Analytics tracking code *or* the
verification meta tag from the site in the future — either one being removed could
un-verify the site in Search Console.

## Step 6 — Hand Google the map

Once verified, two more things:

1. **Submitted the sitemap** — the same `sitemap.xml` file from Step 2, given
   directly to Google inside Search Console. This is the fastest way to say
   "here are all my pages, please go look at them."
2. **Requested indexing on the homepage** — a manual "please crawl this specific
   page now" button, instead of waiting for Google to get to it on its own
   schedule.

## Step 7 — Wait

This part just takes time — there's no way to speed it up further. Typical
timeline for a brand-new site with no prior history:

- A few hours to a few days: Google processes the sitemap submission
- A few days to a few weeks: the homepage actually gets crawled and shows up in
  search results

We'll check back with a `site:bhawnamanglapm.github.io` search at a future
analytics check-in to confirm it actually worked.

---

## TL;DR

1. Noticed zero Google Search traffic in the analytics.
2. Confirmed via a direct Google search that the site wasn't indexed at all.
3. Checked the site's code — nothing was broken or blocking Google.
4. The real cause: nobody had ever told Google the site existed.
5. Set it up in Google Search Console (using the *URL-prefix* property type, not
   *Domain* — that's the part that trips people up on GitHub Pages sites).
6. Verified ownership, submitted the sitemap, requested indexing.
7. Now waiting for Google to actually crawl and rank it — normal for a new site.
