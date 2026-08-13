# SQL Practice — SaaS Subscription Analytics (Basic + Advanced)

**Why this exists:** SQL is listed as a "solid" skill on the site, but
there's no real proof of it anywhere — the one place meant to prove it
(the PCMS case study) is real company work and stays as-is, un-edited.
This is a fresh, from-scratch practice project instead: a fictional B2B
SaaS company ("Aptura"), a churn/MRR/cohort-retention scenario — one of
the most commonly asked PM-analytics topics in interviews — and two
tiers of real queries **you run yourself**, not something pre-generated
for you to just display.

This becomes two separate case studies once done:
1. **Basic** — SELECT, WHERE, JOIN, GROUP BY, aggregates
2. **Advanced** — CTEs, window functions, cohort retention analysis

## Prerequisite: a free, zero-install SQL tool

Go to **https://sqliteonline.com/** — it's a real SQLite database running
in your browser, no signup, no install. (If you'd rather use a desktop
app, DB Browser for SQLite — sqlitebrowser.org — is free and works the
same way; the SQL itself is identical either way.)

## Files you need

Both in this folder:
- `customers.csv` (900 rows)
- `plans.csv` (3 rows)
- `subscriptions.csv` (900 rows)

## Step 1 — Create the tables

Paste this into the SQL editor and run it:

```sql
CREATE TABLE customers (
  customer_id INTEGER PRIMARY KEY,
  signup_date TEXT,
  acquisition_channel TEXT,
  region TEXT
);

CREATE TABLE plans (
  plan_id INTEGER PRIMARY KEY,
  plan_name TEXT,
  monthly_price INTEGER
);

CREATE TABLE subscriptions (
  subscription_id INTEGER PRIMARY KEY,
  customer_id INTEGER,
  plan_id INTEGER,
  start_date TEXT,
  end_date TEXT,
  status TEXT
);
```

## Step 2 — Import the data

On sqliteonline.com: right-click the database in the left panel → **Import** →
choose each CSV file → make sure it maps to the matching table you just
created (it usually auto-detects column names from the CSV header) →
Import. Do this three times, once per CSV.

---

## Part 1 — BASIC queries

Run each of these one at a time. For each, take a screenshot of the query
+ its result grid.

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
SELECT strftime('%Y-%m', signup_date) AS month, COUNT(*) AS new_customers
FROM customers
GROUP BY month
ORDER BY month;
```

**6. Customers by acquisition channel**
```sql
SELECT acquisition_channel, COUNT(*) AS customers
FROM customers
GROUP BY acquisition_channel
ORDER BY customers DESC;
```

**7. Churn rate by plan** (this is the first query that tells a real story)
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

**8. Churn rate by acquisition channel** (a 3-table JOIN: subscriptions → customers)
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

**What you should see (so you know if something's wrong):** Starter plan
churns noticeably more than Scale; Paid Search churns more than Referral.
That's not a coincidence — it's how the dataset was deliberately modeled
(documented in `generate_dataset.py`), the same "modeled, not random"
discipline as the Airline Ops / Flight Delay datasets.

---

## Part 2 — ADVANCED queries (CTEs + window functions)

**1. Monthly cohort retention** (the classic SaaS cohort-analysis question:
of everyone who signed up in month X, what % were still active 3 and 6
months later?)
```sql
WITH cohort AS (
  SELECT customer_id, strftime('%Y-%m', signup_date) AS cohort_month
  FROM customers
),
sub_life AS (
  SELECT customer_id,
         CAST((julianday(COALESCE(end_date, '2025-12-31')) - julianday(start_date)) / 30 AS INTEGER) AS months_survived
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
  SELECT strftime('%Y-%m', s.start_date) AS month, SUM(p.monthly_price) AS new_mrr
  FROM subscriptions s
  JOIN plans p ON s.plan_id = p.plan_id
  GROUP BY month
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
  SELECT strftime('%Y-%m', signup_date) AS month, COUNT(*) AS new_customers
  FROM customers
  GROUP BY month
)
SELECT month,
       new_customers,
       SUM(new_customers) OVER (ORDER BY month) AS cumulative_customers
FROM monthly_signups
ORDER BY month;
```

**4. Rank active customers by tenure within each plan** (window function:
`RANK() ... PARTITION BY`)
```sql
SELECT c.customer_id, p.plan_name, s.start_date,
       CAST((julianday('2025-12-31') - julianday(s.start_date)) / 30 AS INTEGER) AS months_tenure,
       RANK() OVER (PARTITION BY p.plan_name ORDER BY s.start_date ASC) AS tenure_rank_in_plan
FROM subscriptions s
JOIN customers c ON s.customer_id = c.customer_id
JOIN plans p ON s.plan_id = p.plan_id
WHERE s.status = 'active'
ORDER BY p.plan_name, tenure_rank_in_plan
LIMIT 30;
```

---

## What to send back

Screenshot each query + its result (12 total: 8 basic + 4 advanced). Also
tell me, in your own words, one thing the churn-by-plan or churn-by-channel
result actually means for the business — that's the part that turns this
from "I can run a query" into "I can read what a query is telling me,"
which is the actual PM skill this is meant to prove.

Once you send these, I'll write up two case studies (Basic and Advanced)
with your real screenshots, add them to the site, and label the SQL
toolkit chip as genuinely proven instead of just claimed.
