# Amplitude Practice — Strideway (Basic + Advanced)

**Why this exists:** Amplitude/Mixpanel are listed as tools worth having on
a PM's toolkit, but there's no hands-on proof anywhere on the site. This
project fixes that using a real, live Amplitude account (not a simulation)
and a fresh scenario: "Strideway," a fictional fitness/habit-tracking app.

The tracking plan (10 events, 7 event properties, 5 user properties) is
already live in your real Amplitude project — check **Data → Events** in
Amplitude now and you'll see it. What's left is getting real usage data in,
then exploring it.

This becomes two case studies once done:
1. **Basic** — event segmentation: trends, breakdowns, distributions
2. **Advanced** — funnels, retention analysis, cohorts

## Step 1 — Get your API Key

In Amplitude: click the gear icon (bottom left) → **Settings** → **Projects**
→ your project (**"default"**) → copy the **API Key**. (Not the Secret
Key — the API Key is the write-only ingestion key, safe to use in a local
script; it can only send events in, not read or manage your account.)

## Step 2 — Send the data

Both files are in this folder: `events.jsonl` (52,082 events, already
generated — you don't need to run `generate_dataset.py` unless you want to
see how it was built) and `send_to_amplitude.py`.

You'll need the `requests` library: `pip install requests`

**Windows (PowerShell):**
```powershell
$env:AMPLITUDE_API_KEY = "paste-your-api-key-here"
python send_to_amplitude.py
```

**macOS/Linux:**
```bash
export AMPLITUDE_API_KEY="paste-your-api-key-here"
python3 send_to_amplitude.py
```

It'll print progress batch by batch. Takes 1-2 minutes. Once it says
"Done," give Amplitude another minute or two to process, then check
**Data → Events** in Amplitude — you should see real counts appear next to
each event name (Sign Up, Log Workout, etc.).

---

## Part 1 — BASIC: Event Segmentation

In Amplitude, go to **Analytics → New Chart → Segmentation** (sometimes
just called "Event Segmentation" or the default chart type).

**1. Sign Up trend over time**
Event: `Sign Up`. Leave it as a daily/weekly count. You should see signups
ramping upward over the ~90-day window (the dataset was built to show
growth, not a flat rate).

**2. Sign Up, segmented by signup_channel**
Same chart, but click **+ Segment/Group By** → `signup_channel`. You'll get
4 lines instead of 1 — Organic, Referral, Paid Social, Influencer.

**3. Log Workout, broken down by workout_type**
Event: `Log Workout`, grouped by `workout_type`. Shows the relative
popularity of Cardio/Strength/Yoga/HIIT.

**4. Complete Onboarding, segmented by signup_channel**
This is the one that tells a real story: onboarding-completion rate should
differ noticeably by channel. (You won't get a direct "percentage" from a
simple segmentation chart — for that, see the funnel in Part 2 — but the
raw counts here already hint at the pattern.)

**5. Platform split**
Event: `Sign Up`, grouped by `platform` (iOS vs Android) — a simple
distribution check.

Screenshot each of these 5 charts.

---

## Part 2 — ADVANCED: Funnels, Retention, Cohorts

**1. The core monetization funnel**
Go to **Analytics → New Chart → Funnel**. Add these events in order:
1. `Sign Up`
2. `Complete Onboarding`
3. `Log Workout`
4. `View Paywall`
5. `Start Free Trial`
6. `Upgrade to Premium`

Amplitude will show conversion % at each step and the drop-off between
steps. This is the single most useful chart in the whole project — it's
the real shape of Strideway's activation-to-revenue path.

**2. Retention analysis, segmented by signup_channel**
Go to **Analytics → New Chart → Retention**. Starting event: `Sign Up` (or
`Complete Onboarding` for activated-user retention). Returning event:
`Open App`. Then segment/break down by `signup_channel`.

This is where you should be able to **see** the retention difference the
dataset was deliberately built around: Referral and Organic users should
retain visibly better than Paid Social and Influencer users over the
following weeks.

**3. Build a cohort: Premium users**
Go to **Cohorts** (usually in the left nav or under Analytics) → **New
Cohort**. Define it as: users who have performed `Upgrade to Premium` at
least once. Save it as "Premium Users." Cohorts like this get reused across
every other chart type — e.g. you could now go back to the retention chart
and filter to just this cohort.

**4. (Optional but worth trying) Streak milestone breakdown**
Segmentation chart on `Hit Streak Milestone`, grouped by `streak_length`.
Given how the dataset is built, you should see far more people hit a
3-day streak than a 7-day one, and very few or none reach 14/30 — a
realistic finding, not a bug (real habit-app streak data looks like this
too).

Screenshot the funnel, the retention chart, and the cohort definition —
3-4 screenshots covering all of Part 2.

---

## What to send back

Screenshots of all the charts above (roughly 8-9 total across both parts),
plus — in your own words — one real insight from the funnel or retention
data: what would you, as the PM, actually do differently for Influencer-
acquired users versus Referral-acquired ones, given what the retention
chart shows? That's the part that makes this a case study instead of a
list of charts.

Once you send these, I'll write up the Basic and Advanced case studies
with your real screenshots and add them to the site.
