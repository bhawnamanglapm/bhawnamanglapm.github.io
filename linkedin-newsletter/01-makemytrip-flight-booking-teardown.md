# 90 Days to AI PM — Newsletter Draft #1

**Case study source:** MakeMyTrip — Flight Booking Teardown
**Portfolio link to include:** https://bhawnamanglapm.github.io/#case-makemytrip-flight-booking-teardown
**Status:** Draft — ready to copy into LinkedIn Newsletter editor

---

## Suggested headline

**I tore down MakeMyTrip's flight booking flow using 5 PM frameworks. Here's the one number that changed my whole recommendation.**

---

## Post body

Most product teardowns start with a redesign. Mine starts with a question: *why does the drop-off happen where it happens, and not somewhere else?*

I picked MakeMyTrip's flight search → booking flow — one of India's most-used OTA products — and ran it through five frameworks a real PM would actually reach for: CIRCLES, RICE, MoSCoW, HEART, and OKRs. Not as an exercise in checking boxes. As a way of forcing myself to be honest about trade-offs, not just opportunities.

**Here's what the funnel actually showed.**

The steepest drop in the entire booking journey isn't at payment, where most people assume it is. It's between the results page and fare review — a modeled ~38% conversion at that single stage. That's price shock: the number a searcher sees on the results list isn't the number they see two taps later, once taxes, fees, and pre-selected add-ons show up.

For one persona in particular — I call her "Value Rakesh," a price-sensitive searcher comparing 3+ apps before booking — that gap isn't a UX annoyance. It's the reason he leaves.

**But here's the part I almost missed.**

Those add-ons aren't a design oversight. They're revenue. MakeMyTrip's flight vertical monetizes through airline commissions, a convenience fee on the base fare, and ancillary attach — insurance, seat selection, baggage. Recommending "just remove the late fee reveal" without naming that cost isn't a real recommendation. It's a wish.

So the actual recommendation had to hold two things at once:

1. **Ship all-in fare pricing at the results stage** (RICE 13.5) and **make add-ons opt-in instead of opt-out** (RICE 14.4) — the two highest-scored, lowest-effort fixes, both aimed squarely at where Rakesh actually drops off.
2. **Name the cost out loud, before shipping:** opt-in add-ons will reduce ancillary revenue per booking. That's not a footnote — it needs a revenue-per-booking floor agreed with Finance, not just a UX sign-off.

That second part is the difference between a teardown that sounds smart and one a real company could actually ship. Every recommendation with a real cost got named as a risk, in writing, before launch — not discovered after.

**What I'd actually measure:** not one "engagement" number, but Google's own HEART framework — Happiness (pricing-clarity CSAT), Engagement, Adoption, Retention, and Task success (that Results→Fare Review conversion rate, the real target). Tied to one clear OKR: move that 38% baseline to 50%+ in a quarter, without quietly cratering ancillary revenue to get there.

That last guardrail matters more than the headline metric. A conversion win that kills revenue isn't a win — it's a loss wearing a win's clothes.

---

Full teardown — the personas, the complete RICE table, the interactive journey map, and the OKRs — is on my portfolio: [link]

*This is post 1 of a series pulling real case studies from my portfolio into this newsletter. Next up: what happened when I stood up a real Node.js server to test my own KYC verification logic — and found three mistakes in my own build.*

---

## Notes for next drafts (keep consistent going forward)

- **Voice:** first person, direct, no fluff intro — open with a hook line, not a greeting
- **Structure:** hook → the finding → the twist/nuance → the recommendation with its named cost → the metric → CTA back to portfolio
- **Length:** ~600-700 words in the body — long enough to carry real substance, short enough to read in one sitting on LinkedIn
- **Always name a trade-off, not just a win** — this is the throughline of your whole portfolio's voice, keep it in every post
- **Close every post with a one-line teaser for the next one** — builds newsletter momentum across the series
