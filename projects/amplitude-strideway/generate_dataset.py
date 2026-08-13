"""
Synthetic event-stream generator for "Strideway", a fictional fitness/
habit-tracking app.

WHY SYNTHETIC: this practice project targets product-analytics fluency
(event segmentation, funnels, retention, cohorts) using a real Amplitude
account, one of the most common PM-tool requirements in job postings. No
real app's usage data is available in this environment, so this generates
a clearly-modeled dataset instead of faking a "real" one:

  - "Strideway" is a fictional fitness app. No numbers here are
    attributed to a real, identifiable product.
  - Every behavioral difference is a documented, deliberate rule, not
    independent noise:
      1. Onboarding completion (setting a fitness goal) varies by
         acquisition channel: Referral and Organic users complete it far
         more often than Influencer-driven signups, who tend to be
         curiosity clicks with lower intent — a real, well-documented
         growth pattern.
      2. Users who complete onboarding retain dramatically better than
         those who don't — the classic "activation predicts retention"
         pattern behind most habit-app growth models.
      3. Referral/Organic users retain better than Paid Social/Influencer
         users, mirroring (with a different tool and a different fresh
         scenario) the acquisition-channel-predicts-retention pattern
         already demonstrated in the SQL/Aptura churn analysis.
      4. Hitting a 7-day streak milestone sharply increases the
         probability of viewing the paywall shortly after — a real
         behavioral-commitment pattern ("sunk cost/momentum") used
         deliberately as an upsell trigger in real habit apps.

Output: a single JSON-lines file, events.jsonl, one Amplitude-shaped event
per line, ready for send_to_amplitude.py to batch-post to the real
Amplitude HTTP API.
"""

import json
import random
from datetime import datetime, timedelta, timezone

random.seed(23)

N_USERS = 3000
WINDOW_DAYS = 90  # signups spread across a 90-day window
START = datetime(2026, 5, 1, tzinfo=timezone.utc)
OBS_END = START + timedelta(days=WINDOW_DAYS + 30)  # 30 extra days of runway for activity after signup

PLATFORMS = [("iOS", 0.55), ("Android", 0.45)]
CHANNELS = [
    # (name, signup_weight, onboarding_complete_prob, retention_multiplier)
    ("Organic", 0.35, 0.80, 1.00),
    ("Referral", 0.20, 0.90, 1.15),
    ("Paid Social", 0.25, 0.65, 0.80),
    ("Influencer", 0.20, 0.55, 0.65),
]
GOALS = [
    ("General Fitness", 0.35),
    ("Weight Loss", 0.30),
    ("Muscle Gain", 0.20),
    ("Endurance", 0.15),
]
WORKOUT_TYPES = [
    # (name, weight, mean_duration_min)
    ("Cardio", 0.30, 28),
    ("Strength", 0.30, 42),
    ("Yoga", 0.20, 35),
    ("HIIT", 0.20, 22),
]
COUNTRIES = [("US", 0.45), ("India", 0.25), ("UK", 0.12), ("Canada", 0.10), ("Australia", 0.08)]
STREAK_MILESTONES = [3, 7, 14, 30]


def weighted(items):
    return random.choices([i[0] for i in items], weights=[i[1] for i in items], k=1)[0]


def gen_signup_dt():
    # Ramp: later days in the window get modestly more signups (a growing app).
    day_offset = random.choices(
        range(WINDOW_DAYS),
        weights=[1 + 0.03 * i for i in range(WINDOW_DAYS)],
        k=1,
    )[0]
    seconds_into_day = random.randint(0, 86399)
    return START + timedelta(days=day_offset, seconds=seconds_into_day)


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S") + "Z"


def make_event(user_id, event_type, dt, event_props=None, user_props=None):
    return {
        "user_id": user_id,
        "event_type": event_type,
        "time": iso(dt),
        "event_properties": event_props or {},
        "user_properties": user_props or {},
    }


def main():
    events = []

    for i in range(1, N_USERS + 1):
        user_id = f"strideway-{i:05d}"
        signup_dt = gen_signup_dt()
        platform = weighted(PLATFORMS)
        channel_name, _, onboard_p, retention_mult = random.choices(
            CHANNELS, weights=[c[1] for c in CHANNELS], k=1
        )[0]
        country = weighted(COUNTRIES)

        base_user_props = {
            "platform": platform,
            "signup_channel": channel_name,
            "country": country,
            "plan_tier": "Free",
        }

        events.append(make_event(
            user_id, "Sign Up", signup_dt,
            event_props={"platform": platform, "signup_channel": channel_name},
            user_props=base_user_props,
        ))

        completed_onboarding = random.random() < onboard_p
        if not completed_onboarding:
            # A handful of these users poke around for a day or two, then vanish —
            # a real "didn't activate" cohort, not just a single Sign Up event.
            for _ in range(random.randint(0, 2)):
                open_dt = signup_dt + timedelta(hours=random.randint(1, 40))
                if open_dt < OBS_END:
                    events.append(make_event(user_id, "Open App", open_dt))
            continue

        goal = weighted(GOALS)
        onboard_dt = signup_dt + timedelta(minutes=random.randint(2, 90))
        user_props_with_goal = dict(base_user_props, goal=goal)
        events.append(make_event(
            user_id, "Complete Onboarding", onboard_dt,
            event_props={"goal": goal},
            user_props=user_props_with_goal,
        ))

        # Per-user engagement propensity: how many of the days they're "in window"
        # they actually open the app. Modulated by channel retention_mult.
        base_propensity = random.betavariate(2.2, 2.8)  # skews toward moderate engagement
        open_prob_per_day = min(0.95, base_propensity * retention_mult)

        # Per-user lifetime: draw an active-lifespan in days (right-skewed —
        # most users taper off within a few weeks, a real minority stay long-term).
        lifespan_days = min(
            int(random.gammavariate(2.0, 18) * retention_mult),
            (OBS_END - onboard_dt).days,
        )

        current_streak = 0
        streaks_hit = set()
        workout_days = 0
        trial_started = False
        premium_since = None
        paywall_boost_days_left = 0  # elevated paywall odds for a few workout-days after a big streak

        for day in range(lifespan_days):
            day_dt = onboard_dt + timedelta(days=day)
            if day_dt >= OBS_END:
                break
            opened = random.random() < open_prob_per_day
            if not opened:
                current_streak = 0
                continue

            open_dt = day_dt + timedelta(hours=random.randint(6, 22))
            events.append(make_event(user_id, "Open App", open_dt))

            logged_workout = random.random() < 0.62
            if logged_workout:
                wt_name, _, wt_mean = random.choices(WORKOUT_TYPES, weights=[w[1] for w in WORKOUT_TYPES], k=1)[0]
                duration = max(8, int(random.gauss(wt_mean, wt_mean * 0.25)))
                events.append(make_event(
                    user_id, "Log Workout", open_dt + timedelta(minutes=random.randint(1, 15)),
                    event_props={"workout_type": wt_name, "duration_min": duration},
                ))
                workout_days += 1
                current_streak += 1
                for m in STREAK_MILESTONES:
                    if current_streak >= m and m not in streaks_hit:
                        streaks_hit.add(m)
                        events.append(make_event(
                            user_id, "Hit Streak Milestone",
                            open_dt + timedelta(minutes=20),
                            event_props={"streak_length": m},
                        ))
                        if m >= 7:
                            paywall_boost_days_left = 4

                # Paywall exposure: a modest baseline chance on any workout day
                # (the app surfaces it periodically), sharply elevated for a few
                # workout-days right after a 7-day+ streak — the deliberate
                # "momentum" upsell trigger this dataset exists to demonstrate.
                paywall_p = 0.32 if paywall_boost_days_left > 0 else 0.025
                if paywall_boost_days_left > 0:
                    paywall_boost_days_left -= 1
                if random.random() < paywall_p:
                    paywall_dt = open_dt + timedelta(hours=random.randint(1, 30))
                    events.append(make_event(user_id, "View Paywall", paywall_dt))
                    if not trial_started and random.random() < 0.40:
                        trial_started = True
                        trial_dt = paywall_dt + timedelta(minutes=random.randint(2, 60))
                        events.append(make_event(user_id, "Start Free Trial", trial_dt))
                        # Conversion odds scale with how engaged this user already is.
                        convert_p = min(0.55, 0.12 + base_propensity * 0.35)
                        if random.random() < convert_p:
                            plan = "Annual" if random.random() < 0.4 else "Monthly"
                            upgrade_dt = trial_dt + timedelta(days=random.randint(3, 7))
                            if upgrade_dt < OBS_END:
                                events.append(make_event(
                                    user_id, "Upgrade to Premium", upgrade_dt,
                                    event_props={"plan": plan},
                                    user_props={"plan_tier": "Premium"},
                                ))
                                premium_since = upgrade_dt
                                # A modest share cancel within the observation window.
                                if random.random() < 0.18:
                                    cancel_dt = upgrade_dt + timedelta(days=random.randint(10, 45))
                                    if cancel_dt < OBS_END:
                                        events.append(make_event(
                                            user_id, "Cancel Subscription", cancel_dt,
                                            user_props={"plan_tier": "Free"},
                                        ))
            else:
                current_streak = 0

            if random.random() < 0.02:
                events.append(make_event(user_id, "Invite Friend", open_dt + timedelta(minutes=5)))

    events.sort(key=lambda e: e["time"])

    with open("events.jsonl", "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    n_users_active = len({e["user_id"] for e in events})
    print(f"Wrote {len(events)} events for {n_users_active} distinct users to events.jsonl")


if __name__ == "__main__":
    main()
