# Airline Operations Dashboard — Power BI build guide

**Why this exists:** you already have this analysis two ways — a documented
Python/pandas ETL pipeline (`generate_dataset.py` → `analyze.py` →
`dashboard.html`) and a hand-built interactive dashboard. This guide walks
you through building it a *third* way, inside Power BI Desktop itself,
using Power Query (M) for the transform step and DAX for the measures —
the actual tool-native way an ETL/BI Product Owner's team would do this
work, and a different, directly relevant skill from the Python version.

**Good story for Deloitte:** *"I built the same operational analysis three
ways — a Python ETL script, a custom dashboard, and a Power BI report —
specifically to understand what each tool is actually good at."* That's a
stronger, more senior answer than knowing one tool.

**Prerequisite:** Power BI Desktop, free from Microsoft
(https://powerbi.microsoft.com/desktop/). Windows only — if you're on Mac,
use Power BI Service (app.powerbi.com) in a browser instead; the Power
Query and DAX steps below work the same way there.

**Files you need**, both in this folder:
- `../airline_ops_dataset.csv` — the fact table (6,000 flights, same data
  the Python version used)
- `dim_hub.csv` — a small hub lookup table (5 rows), so you build a real
  relationship instead of one flat table

---

## Step 1 — Import both tables

1. Power BI Desktop → **Home** ribbon → **Get Data** → **Text/CSV**.
2. Import `airline_ops_dataset.csv`. When the preview appears, click
   **Transform Data** (not "Load") — this opens Power Query Editor, where
   the cleanup happens.
3. Repeat: **Get Data** → **Text/CSV** → import `dim_hub.csv` → **Transform
   Data** again, so both tables load into the same Power Query session.
4. Rename the two queries (right-click each in the left panel → **Rename**):
   `airline_ops_dataset` → **Fact_Flights**, `dim_hub` → **Dim_Hub**.

## Step 2 — Clean the fact table in Power Query

With **Fact_Flights** selected in the left panel:

1. Select the `date` column → **Transform** ribbon → **Data Type** → **Date**.
2. Select `on_time` and `cancelled` → **Data Type** → **True/False**
   (Power Query usually infers these correctly on import — confirm it did).
3. Select `passengers_expected`, `passengers_boarded`, `capacity`,
   `bags_checked`, `bags_mishandled`, `complaints` → **Data Type** →
   **Whole Number**.
4. Select `load_factor` → **Data Type** → **Decimal Number**.
5. Select `ticket_revenue`, `ancillary_revenue`, `total_revenue` →
   **Data Type** → **Whole Number**.
6. **Remove the `hub_name` column** (right-click the column header →
   **Remove**). This is the actual reason `Dim_Hub` exists: a fact table
   shouldn't carry a denormalized descriptive column when a proper
   dimension table can supply it through a relationship — the same
   normalization judgment call as removing manual Excel lookups in the
   PCMS work at Bajaj, just done here in Power Query's UI instead of a
   REST API integration.
7. **Add a "Reliability Bucket" column** — the Power Query-native version
   of the same logic `analyze.py` uses in Python:
   - **Add Column** ribbon → **Conditional Column**.
   - New column name: `reliability_bucket`.
   - Rule: If `cancelled` **equals** `TRUE` → output `Cancelled`.
   - **Add clause**: Else if `on_time` **equals** `FALSE` → output `Delayed`.
   - Otherwise → output `On-time`.
   - Click OK.
8. **Home** ribbon → **Close & Apply** to load both tables into the model.

## Step 3 — Build a Date table (DAX)

A real Power BI model almost always has a dedicated date table for
time-intelligence, rather than filtering directly on the fact table's date
column. Build one with DAX instead of importing a file — this is a common,
expected technique to be able to talk about.

1. **Modeling** ribbon → **New Table**. Paste this formula:
   ```
   Dim_Date = CALENDAR(DATE(2025,1,1), DATE(2025,12,31))
   ```
2. With `Dim_Date` selected, add calculated columns (**Modeling** →
   **New Column**) for the fields the report needs:
   ```
   MonthName = FORMAT(Dim_Date[Date], "MMM")
   MonthNumber = MONTH(Dim_Date[Date])
   Season = SWITCH(
       TRUE,
       Dim_Date[MonthNumber] IN {12,1,2}, "Winter",
       Dim_Date[MonthNumber] IN {3,4}, "Spring",
       Dim_Date[MonthNumber] IN {5,6}, "Summer",
       Dim_Date[MonthNumber] IN {7,8,9}, "Monsoon",
       "Post-Monsoon"
   )
   ```

## Step 4 — Build the relationships

**Modeling** ribbon → **Manage Relationships** → **New**:

1. `Fact_Flights[hub]` → `Dim_Hub[hub]` — cardinality **Many to one**,
   single direction.
2. `Fact_Flights[date]` → `Dim_Date[Date]` — cardinality **Many to one**,
   single direction.

Switch to **Model view** (left sidebar) afterward and confirm you see a
star: `Fact_Flights` in the middle, `Dim_Hub` and `Dim_Date` each connected
to it by one line, nothing connected to each other. That shape is the
point — it's called a star schema for a reason.

## Step 5 — DAX measures

**Modeling** ribbon → **New Measure**, once per measure below (paste the
formula, press Enter):

```
Flights Operated = COUNTROWS(Fact_Flights)

On-Time % =
DIVIDE(
    CALCULATE(COUNTROWS(Fact_Flights), Fact_Flights[on_time] = TRUE),
    [Flights Operated]
)

Cancellation % =
DIVIDE(
    CALCULATE(COUNTROWS(Fact_Flights), Fact_Flights[cancelled] = TRUE),
    [Flights Operated]
)

Avg Load Factor =
CALCULATE(
    AVERAGE(Fact_Flights[load_factor]),
    Fact_Flights[cancelled] = FALSE
)

Avg Revenue per Flight =
CALCULATE(
    AVERAGE(Fact_Flights[total_revenue]),
    Fact_Flights[cancelled] = FALSE
)

Complaints per 1000 Pax =
DIVIDE(
    SUM(Fact_Flights[complaints]) * 1000,
    SUM(Fact_Flights[passengers_expected])
)
```

Notice that last one uses `passengers_expected`, not `passengers_boarded`
— the exact same denominator fix documented in the Python version's
methodology section (boarded is zero for a cancelled flight by
definition, which would make cancellations look like they generate zero
complaints). Carrying that same judgment call through to the DAX measure,
not just the Python script, is worth saying out loud if it comes up.

```
Baggage Mishandled per 1000 =
DIVIDE(
    SUM(Fact_Flights[bags_mishandled]) * 1000,
    SUM(Fact_Flights[bags_checked])
)
```

## Step 6 — Build the report (3 pages)

**Page 1 — Overview**
- 4 **Card** visuals along the top: `Flights Operated`, `On-Time %`,
  `Avg Load Factor`, `Cancellation %`.
- A **Clustered bar chart**: Axis = `Dim_Hub[hub_name]`, Value =
  `[On-Time %]`.
- A **Line chart**: Axis = `Dim_Date[MonthName]` (sort by `MonthNumber` —
  right-click the field in the Axis well → **Sort by column**), Value =
  `[On-Time %]`.
- A **Slicer** for `Dim_Hub[hub_name]` in a corner, so the whole page
  filters by hub.

**Page 2 — Hub Deep-Dive**
- A **Matrix** visual: Rows = `Dim_Hub[hub_name]`, Values =
  `[On-Time %]`, `[Avg Load Factor]`, `[Avg Revenue per Flight]`,
  `[Cancellation %]`, `[Baggage Mishandled per 1000]`.
- A **Matrix** or **Table** cross-tabbing `Dim_Hub[hub_name]` (rows) by
  `Dim_Date[Season]` (columns) on `[On-Time %]` — this is the Power BI
  version of the route×season heatmap in the HTML dashboard. Add
  **conditional formatting** (right-click the value field in the matrix →
  **Conditional formatting** → **Background color**) so it reads as a
  heatmap, darker = worse.

**Page 3 — Reliability & Complaints (the insight page)**
- A **Clustered column chart**: Axis = `Fact_Flights[reliability_bucket]`,
  Value = `[Complaints per 1000 Pax]`. This should show the same pattern
  as the HTML dashboard: Cancelled far higher than Delayed, far higher
  than On-time.
- A **Text box** underneath stating the finding in one sentence, the same
  way the HTML dashboard's caption does — a Power BI report page is
  supposed to make its own point, not just display a chart and leave the
  reader to find it.

## Step 7 — Save, screenshot, done

1. **File → Save As** → `airline-operations.pbix`, saved into this same
   `power-bi/` folder.
2. Screenshot each of the 3 pages (or **File → Export → PDF**) for the
   portfolio write-up.
3. Send me the `.pbix` file (or just the screenshots/PDF) once it's built
   and I'll add a "Also built as a Power BI report" section to the T4 case
   study on the site, with the screenshots and a short note on what Power
   Query/DAX did differently from the Python version.

## The one-sentence answer if Deloitte asks "do you know Power BI?"

*"Yes — I built a star-schema model with a fact table and two dimension
tables, wrote the DAX measures myself, and used Power Query for the
transform step instead of pre-aggregating in Python, specifically to
practice the tool-native way of doing this rather than just visualizing
numbers I'd already computed elsewhere."*
