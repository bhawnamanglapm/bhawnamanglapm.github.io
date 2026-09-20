# 90 Days to AI PM — Newsletter Draft #1

**Case study source:** MakeMyTrip — Flight Booking Teardown
**Portfolio link to include:** https://bhawnamanglapm.github.io/#case-makemytrip-flight-booking-teardown
**Status:** Draft — ready to copy into LinkedIn Newsletter editor

---

## Suggested headline

**I tore down MakeMyTrip's flight booking flow and set a SMART goal to fix it. Here's the one number that changed my whole recommendation.**

---

## Post body

I want to show you how a Product Manager actually thinks — not with fancy words, but with a real example. So I picked one thing: the flow on MakeMyTrip where you search for a flight and end up booking it. And I studied it closely, the way I would if this were my actual job at the company.

**First, where do people actually give up and leave?**

You'd think most people quit right at the payment step — typing in card details, waiting for OTP, that kind of friction. That's not where the biggest drop happens.

The biggest drop happens one step earlier — right after you pick a flight from the results list, and it takes you to the page where you review the final fare. At that point, roughly **62 out of every 100 people who reach that page leave without booking.** Why? Because the price they see on the results page is not the final price. Taxes, fees, and a few extra charges (that were already ticked "yes" for you, without asking) show up only now. People feel tricked, even if nobody meant to trick them, and they leave.

I imagined a specific person to make this real: a 28-year-old IT professional who compares 3-4 apps before booking anything, because he's careful with money. For someone like him, that price jump isn't a small annoyance — it's the exact reason he closes the app.

**Here's the part that made me stop and think twice.**

My first instinct was: "easy fix, just show the full price upfront, and don't tick those extra charges automatically." But then I asked myself — *why were they doing it this way in the first place?*

Turns out, those extra charges (insurance, seat selection, baggage) are a real source of income for MakeMyTrip, on top of what they earn from the airline itself. So if I just remove that late price-reveal and those pre-ticked extras, the company loses real money. Telling them "just fix it" without saying that out loud isn't good advice — it's wishful thinking.

So my actual recommendation had two parts, not one:

1. **Show the full, final price right from the results page** — no surprises later — and **stop automatically ticking "yes" on extra charges; let the customer choose to add them instead.** These were the two changes that would help the most, for the least effort, out of ten ideas I considered and scored.
2. **Say clearly, in writing, before anyone builds anything:** these two changes will likely reduce the extra income MakeMyTrip makes from add-ons per booking. That's not a small footnote — it means Finance needs to agree on how much of a dip is acceptable, not just the design team saying "looks good."

That second part is the actual difference between advice that *sounds* smart and advice a real company could actually use. Every idea that would cost the company something got written down as a real risk, before anyone built anything — not discovered afterward, when it's too late to plan for it.

**How would I know if it actually worked?**

Not with one single number like "engagement went up." I'd track five different things together: are people happier about pricing being clear (asked directly, after booking); are they using the product more; are they actually noticing and using the new "full price upfront" feature; do they come back and book again within 90 days; and — the main one — did more people actually make it from the results page to a completed booking.

And instead of a vague goal like "make pricing less confusing," I'd write it out the SMART way — a simple habit of checking a goal against five questions before calling it a real goal at all:

- **Specific — what exactly changes?** More people who reach the final price page actually go on to complete their booking, instead of leaving.
- **Measurable — by how much, in numbers?** From roughly 38 out of every 100 people completing a booking today, up to 50 or more out of 100.
- **Achievable — is this realistic?** Yes — because the two fixes I'm shipping (full price upfront, optional add-ons instead of pre-ticked) are the two changes my scoring showed would help the most for the least engineering effort. This isn't a guess; it's the highest-leverage move available.
- **Relevant — does this actually matter to the business?** Yes, directly — but only if I also watch the extra-charge income at the same time, so a "win" on bookings doesn't quietly become a loss in revenue.
- **Time-bound — by when?** Within the next 3 months, so there's a real deadline to check the result against, not an open-ended hope.

That last part — Relevant — is the one people skip, and it's the one that matters most here. If more people book, but the company makes far less money per booking, that's not really a win — it's a loss wearing a win's costume.

---

The full write-up — including all three customer personas, exactly how I scored each of the ten ideas, an interactive map of the whole booking journey, and the specific goals I'd set — is on my portfolio: [link]

*This is post 1 of a series where I'm pulling real case studies from my portfolio into this newsletter, explained simply. Next up: what happened when I built my own test server to check whether a KYC (identity verification) system was actually working correctly — and found three mistakes in my own work along the way.*

---

## Notes for next drafts (keep consistent going forward)

- **Voice:** first person, direct, no fluff intro — open with a hook line, not a greeting
- **Language: plain, layman terms — explain every framework/jargon word in plain English the moment it would otherwise appear, or don't name it at all.** No CIRCLES/RICE/MoSCoW/HEART/OKR/"ancillary revenue"/"conversion rate" as bare terms — say what they mean in one clause instead (e.g. "62 out of 100 people leave" instead of "62% drop-off")
- **Structure:** hook → the finding, explained plainly → the twist/nuance → the recommendation with its named cost, explained plainly → a SMART goal (Specific, Measurable, Achievable, Relevant, Time-bound), each letter spelled out in plain words → CTA back to portfolio
- **Goal format: SMART, not OKRs** — write the goal as five explicit, plainly-worded checks (Specific/Measurable/Achievable/Relevant/Time-bound) rather than an Objective + Key Results list. SMART is the more widely recognized format for a general LinkedIn audience
- **Length:** ~650-800 words in the body — plain language runs a bit longer than jargon, that's fine
- **Always name a trade-off, not just a win** — this is the throughline of your whole portfolio's voice, keep it in every post
- **Close every post with a one-line teaser for the next one** — builds newsletter momentum across the series
