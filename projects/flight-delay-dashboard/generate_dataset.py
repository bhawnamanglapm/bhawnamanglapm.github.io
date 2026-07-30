"""
Synthetic India-domestic flight-delay dataset generator.

WHY SYNTHETIC: this practice project targets a Power BI/Tableau-style delay
dashboard, but the environment this was built in cannot reach live sources
(DGCA, US BTS, Kaggle) to pull a real historical dataset. Rather than fake a
"real" data source, this script generates a clearly-modeled dataset instead:

  - Airlines are FICTIONAL labels (IndiFly, BlueSky Air, Metro Express,
    Skyline National, Coastal Wings) so no delay/reliability numbers are
    attributed to a real, identifiable airline.
  - Routes use REAL Indian city/airport codes, since route congestion at
    real hubs (Delhi, Mumbai, Bengaluru) and real seasonal effects (North
    Indian winter fog, western-coast monsoon) are well-documented public
    aviation-industry knowledge, not a proprietary claim about any company.
  - Delay minutes are drawn from a right-skewed distribution (most flights
    on time or slightly late, a long tail of bad delays) with additive
    effects for: airline reliability tier, route congestion tier, season,
    and time-of-day (delays cascade later in the day - a standard airline
    operations pattern).

Every number this dashboard reports is a property of this generator's
parameters, not of any real airline's actual on-time performance.
"""

import csv
import random
from collections import namedtuple

random.seed(42)

AIRLINES = [
    # (name, type, reliability_index, weight in flight volume)
    ("IndiFly",         "LCC",             1.00, 0.30),
    ("Metro Express",   "LCC",             1.25, 0.24),
    ("BlueSky Air",     "Full-service",    0.75, 0.22),
    ("Skyline National","Full-service",    1.15, 0.16),
    ("Coastal Wings",   "Regional/turboprop", 1.35, 0.08),
]

# route: (origin, destination, base_congestion_delay_min, monsoon_sensitive, fog_sensitive, weight)
ROUTES = [
    ("DEL", "BOM", 9, False, True,  0.14),
    ("DEL", "BLR", 7, False, True,  0.11),
    ("BOM", "BLR", 6, False, False, 0.10),
    ("DEL", "HYD", 7, False, True,  0.08),
    ("BOM", "GOI", 5, True,  False, 0.07),
    ("DEL", "CCU", 6, False, True,  0.07),
    ("BOM", "COK", 5, True,  False, 0.06),
    ("DEL", "AMD", 6, False, True,  0.06),
    ("BLR", "HYD", 4, False, False, 0.06),
    ("DEL", "PNQ", 6, False, True,  0.05),
    ("MAA", "CCU", 4, False, False, 0.04),
    ("COK", "BOM", 5, True,  False, 0.04),
    ("DEL", "GOI", 7, True,  True,  0.03),
    ("BLR", "COK", 4, True,  False, 0.03),
    ("HYD", "MAA", 4, False, False, 0.02),
]

MONTHS = list(range(1, 13))
MONSOON_MONTHS = {6, 7, 8, 9}
FOG_MONTHS = {12, 1}

TIME_BUCKETS = [
    ("Early Morning (05-08)", 0.90),
    ("Morning (08-11)",       1.00),
    ("Afternoon (11-15)",     1.15),
    ("Evening (15-19)",       1.35),
    ("Night (19-23)",         1.55),
]

N_FLIGHTS = 8000
Record = namedtuple("Record", "date airline airline_type route origin destination "
                               "day_of_week month season time_bucket "
                               "delay_minutes delayed cancelled")

SEASON_BY_MONTH = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Spring", 4: "Spring",
    5: "Summer", 6: "Summer",
    7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon",
}
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def weighted_choice(items, weights):
    return random.choices(items, weights=weights, k=1)[0]


def gen_record(i):
    airline = weighted_choice(AIRLINES, [a[3] for a in AIRLINES])
    name, atype, reliability, _ = airline

    route = weighted_choice(ROUTES, [r[5] for r in ROUTES])
    origin, dest, congestion, monsoon_sens, fog_sens, _ = route

    month = random.choice(MONTHS)
    day = random.randint(1, 28)
    dow = DAY_NAMES[random.randint(0, 6)]
    season = SEASON_BY_MONTH[month]

    time_label, time_mult = weighted_choice(TIME_BUCKETS, [1, 1, 1, 1, 1])

    # Base delay: right-skewed (gamma) around a small mean, in minutes.
    # Tuned so the fleet-wide on-time rate lands around 78-82% (a plausible
    # domestic OTP range) while still leaving real spread between the best
    # and worst routes/airlines/seasons/times-of-day.
    base = random.gammavariate(1.3, 3.2)

    delay = base * reliability * time_mult + congestion * 0.35

    if monsoon_sens and month in MONSOON_MONTHS:
        delay += random.gammavariate(1.6, 5.0)
    if fog_sens and month in FOG_MONTHS:
        delay += random.gammavariate(1.8, 6.0) * (1.3 if "Early" in time_label else 1.0)

    delay = max(0.0, delay)

    # Cancellation probability rises with weather exposure.
    cancel_p = 0.006
    if monsoon_sens and month in MONSOON_MONTHS:
        cancel_p += 0.018
    if fog_sens and month in FOG_MONTHS:
        cancel_p += 0.024
    cancelled = random.random() < cancel_p

    if cancelled:
        delay = 0.0  # cancelled flights tracked separately, not as a "delay"

    delayed_flag = (not cancelled) and delay > 15

    date = f"2025-{month:02d}-{day:02d}"

    return Record(date, name, atype, f"{origin}-{dest}", origin, dest, dow,
                  month, season, time_label, round(delay, 1), delayed_flag, cancelled)


def main():
    rows = [gen_record(i) for i in range(N_FLIGHTS)]
    out_path = "flight_delay_dataset.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(Record._fields)
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
