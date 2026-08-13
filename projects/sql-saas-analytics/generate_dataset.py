"""
Synthetic B2B SaaS subscription dataset generator.

WHY SYNTHETIC: this practice project targets SQL fluency (joins,
aggregations, window functions, CTEs) on a churn/MRR/cohort-retention
scenario, one of the most common PM-analytics interview topics. No real
company's subscriber data is available in this environment, so this
generates a clearly-modeled dataset instead of faking a "real" one:

  - "Aptura" is a fictional B2B SaaS company. No numbers here are
    attributed to a real, identifiable business.
  - Churn is modeled with a documented, deliberate rule, not independent
    noise: monthly churn probability varies by plan tier (Starter churns
    more than Scale — a real, well-documented SaaS pattern: cheaper plans
    have weaker product lock-in) and by acquisition channel (Paid Search
    churns more than Referral — also a well-documented pattern: referred
    customers arrive with higher intent).

Three tables, written as separate CSVs (mirrors a normalized schema you'd
actually find in a SaaS product database):
  - customers.csv    (customer_id, signup_date, acquisition_channel, region)
  - plans.csv         (plan_id, plan_name, monthly_price)
  - subscriptions.csv (subscription_id, customer_id, plan_id, start_date,
                        end_date, status)
"""

import csv
import random
from datetime import date, timedelta

random.seed(11)

COMPANY = "Aptura"
START_MONTH = date(2024, 1, 1)
N_MONTHS = 24  # Jan 2024 - Dec 2025
N_CUSTOMERS = 900

PLANS = [
    # (plan_id, name, monthly_price, signup weight, base monthly churn prob)
    (1, "Starter", 29, 0.55, 0.055),
    (2, "Growth", 99, 0.34, 0.032),
    (3, "Scale", 299, 0.11, 0.014),
]

CHANNELS = [
    # (name, signup weight, churn multiplier)
    ("Organic", 0.30, 1.00),
    ("Paid Search", 0.28, 1.35),
    ("Referral", 0.22, 0.65),
    ("Outbound Sales", 0.20, 0.85),
]

REGIONS = [("US", 0.45), ("EU", 0.28), ("APAC", 0.19), ("Other", 0.08)]


def weighted_choice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]


def month_add(d, n):
    month = d.month - 1 + n
    year = d.year + month // 12
    month = month % 12 + 1
    return date(year, month, 1)


def gen_signup_month():
    # Signups ramp up over the 24 months (a growing company), not flat.
    weights = [1 + 0.10 * i for i in range(N_MONTHS)]
    idx = random.choices(range(N_MONTHS), weights=weights, k=1)[0]
    m = month_add(START_MONTH, idx)
    day = random.randint(1, 28)
    return date(m.year, m.month, day)


def main():
    customers = []
    subscriptions = []
    sub_id = 1

    for cust_id in range(1, N_CUSTOMERS + 1):
        signup = gen_signup_month()
        channel = weighted_choice(CHANNELS, [c[1] for c in CHANNELS])
        region = weighted_choice(REGIONS, [r[1] for r in REGIONS])[0]
        plan = weighted_choice(PLANS, [p[3] for p in PLANS])
        plan_id, plan_name, price, _, base_churn = plan

        customers.append((cust_id, signup.isoformat(), channel[0], region))

        # Simulate month-by-month survival from signup to churn or "still active".
        monthly_churn_p = base_churn * channel[2]
        cursor = signup
        end_date = None
        status = "active"
        months_elapsed = 0
        # Cap simulation at the dataset's observation window (end of 2025-12).
        while True:
            months_elapsed += 1
            cursor = month_add(signup, months_elapsed)
            if cursor > date(2025, 12, 31):
                break
            if random.random() < monthly_churn_p:
                end_date = cursor.isoformat()
                status = "cancelled"
                break

        subscriptions.append((
            sub_id, cust_id, plan_id, signup.isoformat(), end_date, status
        ))
        sub_id += 1

    with open("customers.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["customer_id", "signup_date", "acquisition_channel", "region"])
        w.writerows(customers)

    with open("plans.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["plan_id", "plan_name", "monthly_price"])
        w.writerows([(p[0], p[1], p[2]) for p in PLANS])

    with open("subscriptions.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["subscription_id", "customer_id", "plan_id", "start_date", "end_date", "status"])
        w.writerows(subscriptions)

    print(f"Wrote {len(customers)} customers, {len(PLANS)} plans, {len(subscriptions)} subscriptions.")


if __name__ == "__main__":
    main()
