"""
Aggregates airline_ops_dataset.csv into the summaries the dashboard needs,
and writes them to dashboard_data.json for the HTML dashboard to embed.
"""

import json
import pandas as pd

df = pd.read_csv("airline_ops_dataset.csv")
df["on_time"] = df["on_time"].astype(bool)
df["cancelled"] = df["cancelled"].astype(bool)

SEASON_ORDER = ["Winter", "Spring", "Summer", "Monsoon", "Post-Monsoon"]
MONTH_ORDER = list(range(1, 13))
MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

flown = df[~df["cancelled"]]  # load factor / revenue only make sense for operated flights

# --- Headline KPIs ---
total = len(df)
cancelled_n = int(df["cancelled"].sum())
on_time_n = int(df["on_time"].sum())
# Complaints are rated per passengers_expected (the booked/affected
# traveller count), not passengers_boarded — passengers_boarded is 0 for a
# cancelled flight by definition, which would make cancellations look like
# they generate zero complaints. Booked-and-affected is the right
# denominator for a complaints-volume metric; boarded is the right one for
# load factor and revenue, which only exist for flights that actually flew.
total_pax_expected = int(df["passengers_expected"].sum())
total_bags = int(df["bags_checked"].sum())
total_complaints = int(df["complaints"].sum())
total_mishandled = int(df["bags_mishandled"].sum())

kpis = {
    "total_flights": total,
    "on_time_pct": round(100 * on_time_n / total, 1),
    "avg_load_factor_pct": round(100 * flown["load_factor"].mean(), 1),
    "avg_revenue_per_flight": round(flown["total_revenue"].mean()),
    "cancellation_pct": round(100 * cancelled_n / total, 2),
    "complaints_per_1000_pax": round(1000 * total_complaints / total_pax_expected, 2),
    "baggage_mishandled_per_1000": round(1000 * total_mishandled / total_bags, 2),
}

# --- By hub ---
def agg_group(g):
    n = len(g)
    pax_expected = g["passengers_expected"].sum()
    bags = g["bags_checked"].sum()
    flown_g = g[~g["cancelled"]]
    return pd.Series({
        "flights": int(n),
        "on_time_pct": round(100 * g["on_time"].sum() / n, 1),
        "load_factor_pct": round(100 * flown_g["load_factor"].mean(), 1) if len(flown_g) else None,
        "avg_revenue": int(round(flown_g["total_revenue"].mean())) if len(flown_g) else 0,
        "cancellation_pct": round(100 * g["cancelled"].sum() / n, 2),
        "complaints_per_1000_pax": round(1000 * g["complaints"].sum() / pax_expected, 2) if pax_expected else 0,
        "mishandled_per_1000": round(1000 * g["bags_mishandled"].sum() / bags, 2) if bags else 0,
    })

def fix_int_cols(stats):
    # groupby().apply() upcasts every column in the returned Series to a
    # common dtype (float64) when combining groups, even the ones that were
    # cast to int per-group above — a well-known pandas gotcha. Cast back
    # explicitly so the JSON doesn't show "1206.0" for a flight count.
    for col in ("flights", "avg_revenue"):
        if col in stats.columns:
            stats[col] = stats[col].astype(int)
    return stats

hub_stats = df.groupby(["hub", "hub_name"]).apply(agg_group, include_groups=False).reset_index()
hub_stats = fix_int_cols(hub_stats).sort_values("on_time_pct", ascending=False)
hubs = hub_stats.to_dict("records")

# --- By month (trend) ---
month_stats = df.groupby("month").apply(agg_group, include_groups=False).reindex(MONTH_ORDER).reset_index()
month_stats = fix_int_cols(month_stats)
month_stats["label"] = MONTH_LABELS
months = month_stats.to_dict("records")

# --- Hub x season heatmap (on-time %) ---
heatmap = []
for hub_code, hub_name in df[["hub", "hub_name"]].drop_duplicates().itertuples(index=False):
    row = {"hub": hub_code}
    for s in SEASON_ORDER:
        sub = df[(df["hub"] == hub_code) & (df["season"] == s)]
        row[s] = round(100 * sub["on_time"].mean(), 1) if len(sub) else None
    heatmap.append(row)
# Keep heatmap rows in the same order as the hub table (most-reliable first)
hub_order = [h["hub"] for h in hubs]
heatmap = sorted(heatmap, key=lambda r: hub_order.index(r["hub"]))

# --- The correlation callout: complaints vs. operational reliability ---
def complaint_rate(mask):
    sub = df[mask]
    pax_expected = sub["passengers_expected"].sum()
    return round(1000 * sub["complaints"].sum() / pax_expected, 2) if pax_expected else 0

reliability_complaints = [
    {"bucket": "On-time", "complaints_per_1000_pax": complaint_rate((df["on_time"]) & (~df["cancelled"]))},
    {"bucket": "Delayed", "complaints_per_1000_pax": complaint_rate((~df["on_time"]) & (~df["cancelled"]))},
    {"bucket": "Cancelled", "complaints_per_1000_pax": complaint_rate(df["cancelled"])},
]

output = {
    "kpis": kpis,
    "hubs": hubs,
    "months": months,
    "heatmap": heatmap,
    "season_order": SEASON_ORDER,
    "reliability_complaints": reliability_complaints,
}

with open("dashboard_data.json", "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(kpis, indent=2))
print("\nBy hub (most to least reliable):")
for h in hubs:
    print(f"  {h['hub_name']}: {h['on_time_pct']}% on-time, {h['load_factor_pct']}% load factor, "
          f"₹{h['avg_revenue']:,} avg revenue/flight, {h['mishandled_per_1000']} bags mishandled/1000")
print("\nComplaints per 1,000 passengers, by reliability bucket:")
for r in reliability_complaints:
    print(f"  {r['bucket']}: {r['complaints_per_1000_pax']}")
