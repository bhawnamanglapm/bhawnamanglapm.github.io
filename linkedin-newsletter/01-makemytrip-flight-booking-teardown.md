# 90 Days to AI PM — Newsletter Draft #1

**Case study source:** MakeMyTrip — Flight Booking Teardown
**Portfolio link to include:** https://bhawnamanglapm.github.io/#case-makemytrip-flight-booking-teardown
**Status:** Draft — ready to copy into LinkedIn Newsletter editor

---

## Suggested headline

**I tore down MakeMyTrip's flight booking flow. Here's the story, told the way I'd tell it in an interview — Situation, Task, Action, Result.**

---

## Post body

I want to show you how a Product Manager actually thinks — not with fancy words, but with a real example. I'll walk through it the same way I would if someone asked me about it in an interview: what the situation was, what I set out to do, what I actually did, and what the result was.

**Situation — what was actually going on**

MakeMyTrip's flight booking flow (search for a flight, review the fare, pay, done) has a real problem, and it's not where most people would guess. You'd think most people quit right at payment — card details, OTP, that kind of friction. They don't. The biggest drop happens one step earlier — right after picking a flight, on the page that shows the final price. At that point, roughly **62 out of every 100 people who reach that page leave without booking.**

Why? The price shown on the results list isn't the final price. Taxes, fees, and a few extra charges — already ticked "yes" for you, without asking — only show up now. People feel tricked, even if nobody meant to trick them, and they leave.

To make this real, I imagined a specific person: a 28-year-old IT professional who compares 3-4 apps before booking, because he's careful with money. For someone like him, that price jump at the last step isn't a small annoyance — it's the exact reason he closes the app.

**Task — what I set out to do**

Figure out exactly where and why people were leaving, and come back with a real recommendation — not just "fix the pricing," but something specific enough that an actual team could build it, and honest enough about what it would cost the business.

**Action — what I actually did**

My first instinct was: "easy fix, show the full price upfront, stop auto-ticking those extra charges." But I stopped and asked — *why were they doing it this way in the first place?*

Turns out those extra charges (insurance, seat selection, baggage) are real income for MakeMyTrip, on top of what they earn from the airline. Removing them without saying so out loud isn't good advice — it's wishful thinking.

So I came back with two things, not one:

1. **Show the full, final price right from the results page** — and **stop automatically ticking "yes" on extra charges; let the customer choose to add them.** Out of ten ideas I considered and scored, these two would help the most for the least engineering effort.
2. **Said clearly, in writing, before anyone builds anything:** these two changes will likely reduce the extra income MakeMyTrip makes from add-ons per booking. Not a footnote — Finance needs to agree on how much of a dip is acceptable, not just the design team saying "looks good."

That second part is the real difference between advice that *sounds* smart and advice a company could actually use. Every idea with a real cost got written down as a risk before anyone built anything — not discovered afterward, when it's too late to plan for it.

**Result — what success actually looks like, and how I'd prove it**

I wouldn't just say "it worked" — I'd track five things together: are people happier about pricing being clear (asked directly, after booking); are they using the product more; are they actually noticing and using the new "full price upfront" feature; do they come back and book again within 90 days; and — the main one — did more people actually make it from that price page to a completed booking.

And instead of a vague goal like "make pricing less confusing," I'd write the actual target the SMART way — five plain checks:

- **Specific — what exactly changes?** More people who reach the final price page actually complete their booking, instead of leaving.
- **Measurable — by how much?** From ~38 out of every 100 people completing a booking today, up to 50 or more out of 100.
- **Achievable — is this realistic?** Yes — these are the two changes my scoring showed would help most for the least effort. Not a guess.
- **Relevant — does this matter to the business?** Yes — but only if I also watch the extra-charge income at the same time, so a booking win doesn't quietly become a revenue loss.
- **Time-bound — by when?** Within the next 3 months, so there's a real deadline to check against.

Relevant is the one people skip, and it's the one that matters most here. If more people book but the company makes far less per booking, that's not really a win — it's a loss wearing a win's costume.

---

The full write-up — including all three customer personas, exactly how I scored each of the ten ideas, an interactive map of the whole booking journey, and the specific goals I'd set — is on my portfolio: [link]

*This is post 1 of a series where I'm pulling real case studies from my portfolio into this newsletter, explained simply. Next up: what happened when I built my own test server to check whether a KYC (identity verification) system was actually working correctly — and found three mistakes in my own work along the way.*

---

## Notes for next drafts (keep consistent going forward)

- **Voice:** first person, direct, no fluff intro — open with a hook line, not a greeting
- **Language: plain, layman terms — explain every framework/jargon word in plain English the moment it would otherwise appear, or don't name it at all.** No CIRCLES/RICE/MoSCoW/HEART/OKR/"ancillary revenue"/"conversion rate" as bare terms — say what they mean in one clause instead (e.g. "62 out of 100 people leave" instead of "62% drop-off")
- **Overall structure: STAR** — label and write four clear sections: **Situation** (what was actually going on), **Task** (what I set out to do), **Action** (what I actually did, including the twist/nuance and the named cost), **Result** (what success looks like and how I'd prove it). This is the same structure to use verbally in an interview, so writing it this way doubles as interview prep.
- **Goal format inside Result: SMART, not OKRs** — write the target as five explicit, plainly-worded checks (Specific/Measurable/Achievable/Relevant/Time-bound) rather than an Objective + Key Results list. SMART is the more widely recognized format for a general LinkedIn audience
- **Length:** ~650-800 words in the body — plain language runs a bit longer than jargon, that's fine
- **Always name a trade-off, not just a win** — this is the throughline of your whole portfolio's voice, keep it in every post
- **Close every post with a one-line teaser for the next one** — builds newsletter momentum across the series
