"""
Aggregates flight_delay_dataset.csv into the summaries the dashboard needs,
and writes them to dashboard_data.json for the HTML dashboard to embed.
"""

import json
import pandas as pd

df = pd.read_csv("flight_delay_dataset.csv")

TIME_ORDER = [
    "Early Morning (05-08)", "Morning (08-11)", "Afternoon (11-15)",
    "Evening (15-19)", "Night (19-23)",
]
SEASON_ORDER = ["Winter", "Spring", "Summer", "Monsoon", "Post-Monsoon"]
MONTH_ORDER = list(range(1, 13))
MONTH_LABELS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# --- Headline KPIs ---
total = len(df)
cancelled = int(df["cancelled"].sum())
flown = df[~df["cancelled"]]
delayed = int(flown["delayed"].sum())
avg_delay = round(flown["delay_minutes"].mean(), 1)
on_time_pct = round(100 * (1 - delayed / len(flown)), 1)
cancel_pct = round(100 * cancelled / total, 2)

kpis = {
    "total_flights": total,
    "on_time_pct": on_time_pct,
    "avg_delay_minutes": avg_delay,
    "cancellation_pct": cancel_pct,
}

# --- Q1: Which routes delay most? ---
route_stats = (
    flown.groupby("route")
    .agg(avg_delay=("delay_minutes", "mean"), delayed_pct=("delayed", "mean"), flights=("delay_minutes", "count"))
    .reset_index()
)
route_stats["avg_delay"] = route_stats["avg_delay"].round(1)
route_stats["delayed_pct"] = (route_stats["delayed_pct"] * 100).round(1)
route_stats = route_stats.sort_values("avg_delay", ascending=False)
routes = route_stats.to_dict("records")

# --- Q2: Delay patterns by airline ---
airline_stats = (
    flown.groupby(["airline", "airline_type"])
    .agg(avg_delay=("delay_minutes", "mean"), delayed_pct=("delayed", "mean"), flights=("delay_minutes", "count"))
    .reset_index()
)
airline_cancel = df.groupby("airline")["cancelled"].mean().reset_index()
airline_cancel.columns = ["airline", "cancel_rate"]
airline_stats = airline_stats.merge(airline_cancel, on="airline")
airline_stats["avg_delay"] = airline_stats["avg_delay"].round(1)
airline_stats["delayed_pct"] = (airline_stats["delayed_pct"] * 100).round(1)
airline_stats["cancel_rate"] = (airline_stats["cancel_rate"] * 100).round(2)
airline_stats = airline_stats.sort_values("avg_delay", ascending=False)
airlines = airline_stats.to_dict("records")

# --- Q3a: Delay trend by season ---
season_stats = (
    flown.groupby("season")
    .agg(avg_delay=("delay_minutes", "mean"), delayed_pct=("delayed", "mean"))
    .reindex(SEASON_ORDER)
    .reset_index()
)
season_stats["avg_delay"] = season_stats["avg_delay"].round(1)
season_stats["delayed_pct"] = (season_stats["delayed_pct"] * 100).round(1)
seasons = season_stats.to_dict("records")

# --- Q3b: Delay trend by time of day ---
time_stats = (
    flown.groupby("time_bucket")
    .agg(avg_delay=("delay_minutes", "mean"), delayed_pct=("delayed", "mean"))
    .reindex(TIME_ORDER)
    .reset_index()
)
time_stats["avg_delay"] = time_stats["avg_delay"].round(1)
time_stats["delayed_pct"] = (time_stats["delayed_pct"] * 100).round(1)
times = time_stats.to_dict("records")

# --- Q3c: Delay trend by month (for a monthly line chart) ---
month_stats = (
    flown.groupby("month")
    .agg(avg_delay=("delay_minutes", "mean"))
    .reindex(MONTH_ORDER)
    .reset_index()
)
month_stats["avg_delay"] = month_stats["avg_delay"].round(1)
month_stats["label"] = MONTH_LABELS
months = month_stats.to_dict("records")

# --- Route x Season heatmap (top 8 routes) ---
top_routes = route_stats.head(8)["route"].tolist()
heatmap = []
for r in top_routes:
    row = {"route": r}
    for s in SEASON_ORDER:
        sub = flown[(flown["route"] == r) & (flown["season"] == s)]
        row[s] = round(sub["delay_minutes"].mean(), 1) if len(sub) else None
    heatmap.append(row)

output = {
    "kpis": kpis,
    "routes": routes,
    "airlines": airlines,
    "seasons": seasons,
    "times": times,
    "months": months,
    "heatmap": heatmap,
    "season_order": SEASON_ORDER,
}

with open("dashboard_data.json", "w") as f:
    json.dump(output, f, indent=2)

print(json.dumps(kpis, indent=2))
print("\nTop 5 most-delayed routes:")
for r in routes[:5]:
    print(f"  {r['route']}: avg {r['avg_delay']}min, {r['delayed_pct']}% delayed>15min ({r['flights']} flights)")
print("\nAirlines by avg delay:")
for a in airlines:
    print(f"  {a['airline']} ({a['airline_type']}): avg {a['avg_delay']}min, {a['delayed_pct']}% delayed, {a['cancel_rate']}% cancelled")
print("\nBy season:")
for s in seasons:
    print(f"  {s['season']}: avg {s['avg_delay']}min, {s['delayed_pct']}% delayed")
print("\nBy time of day:")
for t in times:
    print(f"  {t['time_bucket']}: avg {t['avg_delay']}min, {t['delayed_pct']}% delayed")
