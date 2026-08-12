"""
Synthetic single-airline operations dataset generator.

WHY SYNTHETIC: this practice project targets an internal airline-ops
dashboard (the kind a PM at an airline, not an OTA, would own) — on-time
performance, load factor, revenue per flight, cancellation rate, customer
complaints, and baggage handling, tracked by hub and by month. The
environment this was built in cannot reach a real airline's internal
operations data (it isn't public), so this generates a clearly-modeled
dataset instead of faking a "real" one:

  - The airline (Aravali Air) and its route network are entirely fictional.
  - Hubs use REAL Indian city/airport codes, since hub congestion at real
    metros (Delhi, Mumbai, Bengaluru) and real seasonal effects (North
    Indian winter fog, western-coast monsoon) are well-documented public
    aviation-industry knowledge, reused here the same way as the sibling
    Flight Delay Prediction Dashboard project — not a proprietary claim
    about any real company's operations.
  - Complaints and baggage mishandling are modeled as CORRELATED with
    on-time performance and cancellations, not independent random noise —
    that correlation (operational reliability drives complaint volume) is
    a well-documented real pattern in airline ops, and it's the one
    deliberate modeling choice this generator is built to surface.

Every number this dashboard reports is a property of this generator's
parameters, not of any real airline's actual operating performance.
"""

import csv
import random
from collections import namedtuple

random.seed(7)

AIRLINE = "Aravali Air"
CAPACITY = 180  # seats — single fleet type (A320-class), keeps load-factor math simple

# hub: (code, name, congestion index, fog-sensitive, monsoon-sensitive, weight in flight volume)
HUBS = [
    ("DEL", "Delhi",      8, True,  False, 0.28),
    ("BOM", "Mumbai",     7, False, True,  0.24),
    ("BLR", "Bengaluru",  5, False, False, 0.20),
    ("HYD", "Hyderabad",  4, False, False, 0.16),
    ("CCU", "Kolkata",    6, True,  True,  0.12),
]

MONTHS = list(range(1, 13))
MONSOON_MONTHS = {6, 7, 8, 9}
FOG_MONTHS = {12, 1}
FESTIVE_MONTHS = {10, 11}   # higher demand -> higher load factor + fares
LOW_SEASON_MONTHS = {1, 2}  # lower demand -> lower load factor + fares

SEASON_BY_MONTH = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring",
    5: "Summer", 6: "Summer",
    7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon",
}
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

N_FLIGHTS = 6000
Record = namedtuple("Record", "date hub hub_name month season day_of_week capacity "
                               "passengers_expected passengers_boarded load_factor "
                               "on_time cancelled ticket_revenue ancillary_revenue "
                               "total_revenue complaints bags_checked bags_mishandled")


def weighted_choice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]


def sample_complaints(on_time, cancelled):
    """Complaint count per flight, deliberately correlated with reliability —
    the modeling choice this dataset exists to demonstrate."""
    if cancelled:
        weights = [0.50, 0.27, 0.15, 0.08]  # 0, 1, 2, 3 complaints
    elif not on_time:
        weights = [0.80, 0.13, 0.05, 0.02]
    else:
        weights = [0.965, 0.030, 0.004, 0.001]
    return weighted_choice([0, 1, 2, 3], weights)


def sample_mishandled(bags_checked, congestion, irregular_ops):
    """Binomial-style: one independent draw per bag, rate rising with hub
    congestion and on days operations went irregular (delay/cancellation)."""
    rate = 0.0025 + congestion * 0.00035
    if irregular_ops:
        rate += 0.0035
    return sum(1 for _ in range(bags_checked) if random.random() < rate)


def gen_record():
    hub = weighted_choice(HUBS, [h[5] for h in HUBS])
    code, name, congestion, fog_sens, monsoon_sens, _ = hub

    month = random.choice(MONTHS)
    day = random.randint(1, 28)
    dow = DAY_NAMES[random.randint(0, 6)]
    season = SEASON_BY_MONTH[month]

    # --- On-time performance ---
    # Base OTP tuned high (airlines report OTP in the 75-88% range); reduced
    # by hub congestion and by weather exposure at fog/monsoon-sensitive hubs.
    on_time_p = 0.90 - congestion * 0.012
    if fog_sens and month in FOG_MONTHS:
        on_time_p -= 0.22
    if monsoon_sens and month in MONSOON_MONTHS:
        on_time_p -= 0.14
    on_time_p = max(0.35, on_time_p)
    on_time = random.random() < on_time_p

    # --- Cancellation ---
    cancel_p = 0.006 + congestion * 0.0006
    if fog_sens and month in FOG_MONTHS:
        cancel_p += 0.022
    if monsoon_sens and month in MONSOON_MONTHS:
        cancel_p += 0.016
    cancelled = random.random() < cancel_p
    if cancelled:
        on_time = False  # a cancelled flight is never counted as on-time

    # --- Load factor & passengers ---
    base_load = 0.79
    if month in FESTIVE_MONTHS:
        base_load += 0.07
    if month in LOW_SEASON_MONTHS:
        base_load -= 0.06
    if monsoon_sens and month in MONSOON_MONTHS:
        base_load -= 0.03
    load_factor = min(0.98, max(0.45, random.gauss(base_load, 0.06)))
    # passengers_expected = demand estimate, computed the same way whether or
    # not the flight went on to fly. A cancelled flight still had a booked
    # set of travellers affected by it — using passengers_boarded (which is
    # 0 for a cancellation) as the denominator for a complaints-per-1,000
    # metric would make cancellations look like they generate zero
    # complaints, which is backwards. passengers_expected fixes that.
    passengers_expected = round(CAPACITY * load_factor)
    passengers = 0 if cancelled else passengers_expected

    # --- Revenue ---
    base_fare = {"DEL": 4400, "BOM": 4300, "BLR": 3900, "HYD": 3700, "CCU": 3800}[code]
    fare_mult = 1.0
    if month in FESTIVE_MONTHS:
        fare_mult += 0.15
    if month in LOW_SEASON_MONTHS:
        fare_mult -= 0.10
    ticket_revenue = 0 if cancelled else round(passengers * base_fare * fare_mult * random.uniform(0.94, 1.06))
    ancillary_revenue = 0 if cancelled else round(passengers * random.uniform(280, 420))
    total_revenue = ticket_revenue + ancillary_revenue

    # --- Complaints ---
    complaints = sample_complaints(on_time, cancelled)

    # --- Baggage ---
    bags_checked = 0 if cancelled else round(passengers * random.uniform(1.02, 1.18))
    irregular_ops = cancelled or (not on_time)
    bags_mishandled = sample_mishandled(bags_checked, congestion, irregular_ops) if bags_checked else 0

    date = f"2025-{month:02d}-{day:02d}"

    return Record(
        date, code, name, month, season, dow, CAPACITY,
        passengers_expected, passengers, round(load_factor, 3), on_time, cancelled,
        ticket_revenue, ancillary_revenue, total_revenue,
        complaints, bags_checked, bags_mishandled,
    )


def main():
    rows = [gen_record() for _ in range(N_FLIGHTS)]
    out_path = "airline_ops_dataset.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(Record._fields)
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
