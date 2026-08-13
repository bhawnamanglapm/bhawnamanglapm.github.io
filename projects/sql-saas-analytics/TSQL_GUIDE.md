# SQL Practice — SaaS Subscription Analytics (SQL Server / T-SQL edition)

Same dataset and same 12 questions as `SQL_GUIDE.md`, rewritten for **SQL
Server + VS Code** instead of the browser SQLite tool. Everything here is
free — no license cost either way. Use this file, not `SQL_GUIDE.md`, once
SQL Server is installed (`SQL_GUIDE.md` stays as the SQLite backup/reference
in case you ever want the zero-install path again).

## Step 0 — Install (one-time, ~20 min)

1. **SQL Server 2022 Express** (free): https://www.microsoft.com/en-us/sql-server/sql-server-downloads
   → download "Express" → run installer → choose **Basic** install type →
   accept the license → let it finish. Note the instance name it shows at
   the end — it's almost always `SQLEXPRESS`, so your server address will
   be `localhost\SQLEXPRESS`.
2. **SQL Server Management Studio (SSMS)** (free): https://aka.ms/ssmsfullsetup
   → install with defaults. You'll only use this once, for its point-and-click
   CSV import wizard — everything after that happens in VS Code.
3. **VS Code extension**: open VS Code → Extensions icon (`Ctrl+Shift+X`) →
   search **"SQL Server (mssql)"** by Microsoft → Install.

## Step 1 — Create the database (in SSMS)

Open SSMS → Connect → Server name: `localhost\SQLEXPRESS` → Authentication:
**Windows Authentication** → Connect.

Right-click **Databases** → **New Database** → name it `aptura_saas` → OK.

## Step 2 — Import the 3 CSVs (in SSMS, one-time)

Right-click `aptura_saas` → **Tasks** → **Import Flat File...**

Run this three times, once per file (both in this folder):
- `customers.csv` → table name `customers`
- `plans.csv` → table name `plans`
- `subscriptions.csv` → table name `subscriptions`

On the "Modify Columns" screen of the wizard, check that:
- `signup_date`, `start_date`, `end_date` are typed as **date** (the
  wizard sometimes guesses `nvarchar` — click the Data Type dropdown and
  fix it if so)
- `end_date` allows **Nulls** (it must — active customers have no end date)

Click through to Finish for each file. If anything looks wrong afterward,
you can always drop the table (right-click it → Delete) and re-run the
wizard.

## Step 3 — Connect VS Code and run queries

In VS Code: `Ctrl+Shift+P` → **MS SQL: Connect** → Server: `localhost\SQLEXPRESS`
→ Authentication: **Windows Authentication** → Database: `aptura_saas`.

Open a new file, save it as `queries.sql`, paste a query below, then run it
with `Ctrl+Shift+E` (or the ▷ Run button that appears above the query).

---

## Part 1 — BASIC queries

**1. Total customers**
```sql
SELECT COUNT(*) AS total_customers FROM customers;
```

**2. Active vs. cancelled subscriptions**
```sql
SELECT status, COUNT(*) AS count FROM subscriptions GROUP BY status;
```

**3. Current MRR (Monthly Recurring Revenue)**
```sql
SELECT SUM(p.monthly_price) AS current_mrr
FROM subscriptions s
JOIN plans p ON s.plan_id = p.plan_id
WHERE s.status = 'active';
```

**4. MRR by plan**
```sql
SELECT p.plan_name, SUM(p.monthly_price) AS mrr, COUNT(*) AS active_subs
FROM subscriptions s
JOIN plans p ON s.plan_id = p.plan_id
WHERE s.status = 'active'
GROUP BY p.plan_name
ORDER BY mrr DESC;
```

**5. New customers by signup month**
```sql
SELECT FORMAT(signup_date, 'yyyy-MM') AS month, COUNT(*) AS new_customers
FROM customers
GROUP BY FORMAT(signup_date, 'yyyy-MM')
ORDER BY month;
```

**6. Customers by acquisition channel**
```sql
SELECT acquisition_channel, COUNT(*) AS customers
FROM customers
GROUP BY acquisition_channel
ORDER BY customers DESC;
```

**7. Churn rate by plan**
```sql
SELECT p.plan_name,
       COUNT(*) AS total_subs,
       SUM(CASE WHEN s.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
       ROUND(100.0 * SUM(CASE WHEN s.status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_pct
FROM subscriptions s
JOIN plans p ON s.plan_id = p.plan_id
GROUP BY p.plan_name
ORDER BY churn_pct DESC;
```

**8. Churn rate by acquisition channel**
```sql
SELECT c.acquisition_channel,
       COUNT(*) AS total,
       SUM(CASE WHEN s.status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
       ROUND(100.0 * SUM(CASE WHEN s.status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_pct
FROM subscriptions s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.acquisition_channel
ORDER BY churn_pct DESC;
```

**What you should see:** Starter plan churns noticeably more than Scale;
Paid Search churns more than Referral. That's deliberate — documented in
`generate_dataset.py`, not coincidence.

---

## Part 2 — ADVANCED queries (CTEs + window functions)

**1. Monthly cohort retention**
```sql
WITH cohort AS (
  SELECT customer_id, FORMAT(signup_date, 'yyyy-MM') AS cohort_month
  FROM customers
),
sub_life AS (
  SELECT customer_id,
         DATEDIFF(day, start_date, COALESCE(end_date, CAST('2025-12-31' AS DATE))) / 30 AS months_survived
  FROM subscriptions
)
SELECT c.cohort_month,
       COUNT(*) AS cohort_size,
       ROUND(100.0 * SUM(CASE WHEN sl.months_survived >= 3 THEN 1 ELSE 0 END) / COUNT(*), 1) AS retention_3mo_pct,
       ROUND(100.0 * SUM(CASE WHEN sl.months_survived >= 6 THEN 1 ELSE 0 END) / COUNT(*), 1) AS retention_6mo_pct
FROM cohort c
JOIN sub_life sl ON c.customer_id = sl.customer_id
GROUP BY c.cohort_month
ORDER BY c.cohort_month;
```

**2. Month-over-month new-MRR growth** (window function: `LAG()`)
```sql
WITH monthly_new_mrr AS (
  SELECT FORMAT(s.start_date, 'yyyy-MM') AS month, SUM(p.monthly_price) AS new_mrr
  FROM subscriptions s
  JOIN plans p ON s.plan_id = p.plan_id
  GROUP BY FORMAT(s.start_date, 'yyyy-MM')
)
SELECT month,
       new_mrr,
       LAG(new_mrr) OVER (ORDER BY month) AS prev_month_new_mrr,
       ROUND(100.0 * (new_mrr - LAG(new_mrr) OVER (ORDER BY month)) / LAG(new_mrr) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM monthly_new_mrr
ORDER BY month;
```

**3. Running cumulative signups** (window function: `SUM() OVER`)
```sql
WITH monthly_signups AS (
  SELECT FORMAT(signup_date, 'yyyy-MM') AS month, COUNT(*) AS new_customers
  FROM customers
  GROUP BY FORMAT(signup_date, 'yyyy-MM')
)
SELECT month,
       new_customers,
       SUM(new_customers) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS cumulative_customers
FROM monthly_signups
ORDER BY month;
```

> **Note:** `ROWS UNBOUNDED PRECEDING` is required here (not just `ORDER BY
> month` alone). Without it, SQL Server defaults to a RANGE window frame,
> which errors on `FORMAT()`'s output (`Msg 8729`) because RANGE frames cap
> the ORDER BY column's underlying type at 900 bytes and `FORMAT()` returns
> `nvarchar(4000)` regardless of the actual string length. ROWS frames don't
> have that restriction.

**4. Rank active customers by tenure within each plan** (window function:
`RANK() ... PARTITION BY`)
```sql
SELECT TOP 30
       c.customer_id, p.plan_name, s.start_date,
       DATEDIFF(day, s.start_date, CAST('2025-12-31' AS DATE)) / 30 AS months_tenure,
       RANK() OVER (PARTITION BY p.plan_name ORDER BY s.start_date ASC) AS tenure_rank_in_plan
FROM subscriptions s
JOIN customers c ON s.customer_id = c.customer_id
JOIN plans p ON s.plan_id = p.plan_id
WHERE s.status = 'active'
ORDER BY p.plan_name, tenure_rank_in_plan;
```

---

## What changed vs. the SQLite version (for your own notes — this is a
real, common interview talking point: "I know SQL isn't one universal
dialect")

| SQLite | T-SQL (SQL Server) |
|---|---|
| `strftime('%Y-%m', date_col)` | `FORMAT(date_col, 'yyyy-MM')` |
| `julianday(a) - julianday(b)` | `DATEDIFF(day, b, a)` |
| `CAST(x AS INTEGER)` | `CAST(x AS INT)` |
| `... LIMIT 30` (at the end) | `SELECT TOP 30 ...` (at the start) |
| `TEXT` column type | `VARCHAR(n)` / `DATE` |

---

## What to send back

Same as before: screenshot each query + result (12 total), plus one thing
in your own words about what the churn-by-plan or churn-by-channel result
means for the business. Once you send these, I'll write up the Basic and
Advanced case studies with your real screenshots and add them to the site.
