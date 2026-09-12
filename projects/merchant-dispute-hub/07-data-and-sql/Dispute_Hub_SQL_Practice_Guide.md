# Dispute Hub SQL Practice Guide

A hands-on SQL workbook built on the Merchant Payment Operations & Dispute Hub project. It has 54 worked queries from basics to advanced analytics, each with the business question, an explanation, the expected result and common mistakes, plus 24 practice exercises with an answer key.

> The data is simulated for practice. It covers January to mid-June 2027, just after the illustrative go-live, and the reporting date used in queries is **2027-06-15**. Merchants, analysts and reason codes are fictional.

## What's in the pack

| File | What it's for |
|---|---|
| `Dispute_Hub_SQL_Lab.html` | Run every lesson and exercise in your browser, check your answers automatically |
| `dispute_hub_practice.db` | Ready-made SQLite database for DB Browser for SQLite, DBeaver or VS Code |
| `dispute_hub_practice.sql` | The same database as a script you can import into an online SQLite editor |
| This guide | Explanations, expected results and the answer key |

## How to practice

**Option 1, easiest:** open `Dispute_Hub_SQL_Lab.html` in a browser. Pick a lesson, edit the query, select Run, and use Check answer on the Practice tab.

**Option 2, desktop tool:** install DB Browser for SQLite (free), choose Open Database, select `dispute_hub_practice.db`, then use the Execute SQL tab.

**Option 3, online:** open an online SQLite editor such as sqliteonline.com, import `dispute_hub_practice.sql`, and run queries there.

For each lesson, read the business question and try writing the query yourself first. Then compare with the worked query, check your result matches the expected result, and read the watch-outs. Queries use SQLite syntax; where other databases differ, the lesson says how.

## How SQL runs a query

You write clauses in one order, but the database processes them in another. Knowing this explains most beginner errors, such as why an alias works in ORDER BY but not in WHERE.

| Written order | Processing order | What happens |
|---|---|---|
| SELECT | 1. FROM and JOIN | Pick tables and combine rows |
| FROM / JOIN | 2. WHERE | Filter individual rows |
| WHERE | 3. GROUP BY | Form groups |
| GROUP BY | 4. HAVING | Filter groups |
| HAVING | 5. SELECT | Calculate columns, aggregates and window functions |
| ORDER BY | 6. ORDER BY | Sort the result |
| LIMIT | 7. LIMIT | Return the first rows |

## Tables

```
merchants ─┬─< disputes ─┬─< status_events
           │             ├─< evidence_files >── portal_users
           │             ├─< ops_work_items >── analysts
           │             └── reason_codes (lookup)
           ├─< portal_users ─< analytics_events
           ├─< settlements ·· ledger (reconciled on merchant_id + payout_date)
           └─< servicing_contacts
```

**merchants**: One row per merchant.

| Column | Meaning |
|---|---|
| `merchant_id` | Merchant identifier (M101 to M130) |
| `merchant_name` | Trading name |
| `segment` | Merchant segment used in the GTM plan |
| `region` | Sales region |
| `rollout_wave` | Pilot, Wave 1, Wave 2, General availability or Later phase |
| `portal_enabled_date` | Date the portal went live for this merchant; NULL if not yet |
| `annual_revenue_usd` | Annual card sales |

**reason_codes**: Reference data for dispute reason codes (illustrative codes).

| Column | Meaning |
|---|---|
| `reason_code` | Code, for example FR-01 |
| `category` | Fraud, Consumer dispute, Processing error or Authorization |
| `description` | Plain-language description |
| `response_window_days` | Days the merchant has to respond |

**disputes**: One row per dispute. Reporting date is 2027-06-15.

| Column | Meaning |
|---|---|
| `dispute_id` | Dispute identifier |
| `merchant_id` | Merchant the dispute belongs to |
| `card_network` | Visa, Mastercard, Amex or Discover |
| `reason_code` | Reason code (may be unmapped) |
| `dispute_amount` | Disputed amount in USD |
| `received_at` | Date received |
| `response_due_at` | Response deadline |
| `responded_at` | Date evidence was submitted or the dispute accepted; NULL if no response |
| `response_channel` | Portal or Email; NULL if no response |
| `internal_status` | New, Awaiting evidence, Evidence submitted, Under review, Won, Partially won, Lost, Accepted or Expired |
| `outcome` | Final outcome; NULL while open |
| `recovered_amount` | Amount returned to the merchant; NULL while open |
| `closed_at` | Date the outcome was recorded |

**status_events**: Status changes received from the processor.

| Column | Meaning |
|---|---|
| `event_id` | Event identifier |
| `dispute_id` | Dispute |
| `processor_status` | Status value sent by the processor |
| `internal_status` | Normalized internal status |
| `processor_event_at` | When the processor recorded the change |
| `hub_updated_at` | When the hub applied it |

**portal_users**: Merchant users invited to the portal.

| Column | Meaning |
|---|---|
| `user_id` | User identifier |
| `merchant_id` | Merchant |
| `role` | Admin, Operations or Finance |
| `invited_at` | Invitation date |
| `first_login_at` | First sign-in date; NULL if never |

**evidence_files**: Files uploaded through the portal.

| Column | Meaning |
|---|---|
| `file_id` | File identifier |
| `dispute_id` | Dispute |
| `user_id` | Uploading user |
| `file_type` | pdf, jpg or png |
| `file_size_kb` | Size in KB |
| `uploaded_at` | Upload time |
| `redaction_status` | Clean, Redacted or Quarantined |

**analytics_events**: Product analytics events (pseudonymous user IDs).

| Column | Meaning |
|---|---|
| `event_id` | Event identifier |
| `user_id` | Portal user |
| `event_name` | sign_in, dispute_viewed, evidence_upload_started, evidence_submitted, export_csv or onboarding_completed |
| `event_at` | Event time |
| `dispute_id` | Related dispute, if any |

**analysts**: Dispute ops analysts.

| Column | Meaning |
|---|---|
| `analyst_id` | Analyst identifier |
| `analyst_name` | Name (fictional) |
| `team` | Team Alpha or Team Beta |

**ops_work_items**: Work handled by dispute ops.

| Column | Meaning |
|---|---|
| `work_item_id` | Work item identifier |
| `dispute_id` | Dispute |
| `analyst_id` | Analyst |
| `queue_reason` | Email evidence intake, Portal submission review or Unmapped reason code |
| `assigned_at` | Picked up |
| `resolved_at` | Resolved; NULL if still open |

**settlements**: Weekly merchant payouts from the settlement pipeline.

| Column | Meaning |
|---|---|
| `settlement_id` | Settlement identifier |
| `merchant_id` | Merchant |
| `payout_date` | Payout date (Fridays) |
| `gross_sales` | Gross card sales |
| `fees` | Processing fees |
| `chargeback_debits` | Disputed amounts debited |
| `reversals` | Amounts returned after won disputes |
| `net_payout` | gross_sales − fees − chargeback_debits + reversals |

**ledger**: Finance ledger payouts used for reconciliation.

| Column | Meaning |
|---|---|
| `ledger_id` | Ledger row identifier |
| `merchant_id` | Merchant |
| `payout_date` | Payout date |
| `ledger_amount` | Amount recorded by finance |

**servicing_contacts**: Merchant contacts with customer servicing.

| Column | Meaning |
|---|---|
| `contact_id` | Contact identifier |
| `merchant_id` | Merchant |
| `contact_at` | Contact time |
| `reason` | Settlement query, Dispute status, Portal access or Other |
| `channel` | Phone, Email or Chat |


The data contains a few deliberate problems for you to find in Level 7. They're listed in the appendix at the end, so try the data quality lessons before looking.

## Syntax differences between databases

| Task | SQLite (this guide) | PostgreSQL | MySQL | SQL Server |
|---|---|---|---|---|
| First N rows | `LIMIT 5` | `LIMIT 5` | `LIMIT 5` | `SELECT TOP 5` |
| Days between dates | `julianday(b) - julianday(a)` | `b::date - a::date` | `DATEDIFF(b, a)` | `DATEDIFF(day, a, b)` |
| Minutes between times | `(julianday(b) - julianday(a)) * 1440` | `EXTRACT(EPOCH FROM b - a) / 60` | `TIMESTAMPDIFF(MINUTE, a, b)` | `DATEDIFF(minute, a, b)` |
| Year-month | `strftime('%Y-%m', d)` | `DATE_TRUNC('month', d)` | `DATE_FORMAT(d, '%Y-%m')` | `FORMAT(d, 'yyyy-MM')` |
| Add a month | `date(d, '+1 month')` | `d + INTERVAL '1 month'` | `DATE_ADD(d, INTERVAL 1 MONTH)` | `DATEADD(month, 1, d)` |
| Join text | `a \|\| b` | `a \|\| b` | `CONCAT(a, b)` | `a + b` or `CONCAT(a, b)` |
| List values in a group | `GROUP_CONCAT(x)` | `STRING_AGG(x, ',')` | `GROUP_CONCAT(x)` | `STRING_AGG(x, ',')` |
| Percentile | ROW_NUMBER method (lesson 33) | `PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY x)` | ROW_NUMBER method | `PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY x) OVER ()` |
| Case-insensitive match | `LIKE` (ASCII) | `ILIKE` | `LIKE` (default collation) | `LIKE` (default collation) |


## Level 1: Basics

### 1. Look at a table

**Business question:** What does the disputes table contain?  
**Concepts:** SELECT *, LIMIT

```sql
SELECT *
FROM disputes
LIMIT 5;
```

**How it works:** SELECT * returns every column, and LIMIT keeps the output to the first five rows. This is the first thing to run on any unfamiliar table: you see column names, data types and what real values look like before writing anything more complex.

**Expected result:**

| dispute_id | merchant_id | card_network | reason_code | dispute_amount | received_at | response_due_at | responded_at | response_channel | internal_status | outcome | recovered_amount | closed_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| D0001 | M105 | Amex | NA-03 | 549.42 | 2027-01-04 | 2027-02-03 | 2027-01-23 | Email | Lost | Lost | 0 | 2027-02-18 |
| D0002 | M122 | Mastercard | CR-04 | 34.2 | 2027-01-05 | 2027-01-25 | 2027-01-21 | Email | Won | Won | 51.3 | 2027-03-16 |
| D0003 | M101 | Visa | FR-01 | 157.17 | 2027-01-08 | 2027-02-07 | 2027-01-26 | Email | Won | Won | 157.17 | 2027-03-07 |
| D0004 | M112 | Visa | NA-03 | 32.17 | 2027-01-08 | 2027-02-07 | 2027-01-25 | Email | Lost | Lost | 0 | 2027-03-05 |
| D0005 | M113 | Discover | NA-03 | 51.48 | 2027-01-08 | 2027-02-07 | 2027-02-06 | Email | Won | Won | 51.48 | 2027-03-05 |

_5 rows._

**Watch out:** Use SELECT * only for exploring. In reports and dashboards, name the columns you need so a new column added to the table doesn't change your output.

**Other databases:** SQL Server: SELECT TOP 5 * FROM disputes. Oracle and newer SQL Server: add OFFSET 0 ROWS FETCH NEXT 5 ROWS ONLY after ORDER BY.

### 2. Choose columns, rename and sort

**Business question:** Show Northwind Outfitters' (M101) disputes with the largest amounts first.  
**Concepts:** Column list, AS aliases, WHERE, ORDER BY

```sql
SELECT dispute_id,
       reason_code,
       dispute_amount  AS amount_usd,
       response_due_at AS due_date
FROM disputes
WHERE merchant_id = 'M101'
ORDER BY dispute_amount DESC;
```

**How it works:** The column list picks only what the question needs, and AS gives columns readable names. WHERE keeps rows for one merchant. ORDER BY ... DESC sorts from largest to smallest. SQL runs clauses in the order FROM, WHERE, GROUP BY, HAVING, SELECT, ORDER BY, LIMIT, which is why you can sort by an alias but can't filter by one in WHERE.

**Expected result:**

| dispute_id | reason_code | amount_usd | due_date |
|---|---|---|---|
| D0106 | DP-05 | 341.07 | 2027-03-06 |
| D0218 | FR-01 | 271.37 | 2027-04-30 |
| D0237 | CR-04 | 221.38 | 2027-04-29 |
| D0273 | NR-02 | 201.9 | 2027-05-22 |
| D0071 | NR-02 | 188.9 | 2027-03-03 |
| D0135 | NA-03 | 183.35 | 2027-04-02 |
| D0158 | DP-05 | 169.06 | 2027-04-01 |
| D0003 | FR-01 | 157.17 | 2027-02-07 |

_Showing 8 of 36 rows._

**Watch out:** Text values go in single quotes ('M101'). Double quotes mean an identifier such as a column name in most databases.

### 3. Combine conditions

**Business question:** Which Visa or Mastercard disputes over $250 were received in March 2027?  
**Concepts:** AND, IN, comparison operators, date ranges

```sql
SELECT dispute_id, merchant_id, card_network, dispute_amount, received_at
FROM disputes
WHERE card_network IN ('Visa', 'Mastercard')
  AND dispute_amount > 250
  AND received_at >= '2027-03-01'
  AND received_at <  '2027-04-01'
ORDER BY received_at;
```

**How it works:** IN is a short way of writing card_network = 'Visa' OR card_network = 'Mastercard'. Every AND condition must be true for a row to be kept. The date range uses 'on or after the first day' and 'before the first day of next month', which works whether the column holds dates or full timestamps.

**Expected result:**

| dispute_id | merchant_id | card_network | dispute_amount | received_at |
|---|---|---|---|---|
| D0175 | M120 | Visa | 276.93 | 2027-03-16 |
| D0193 | M129 | Mastercard | 1,161.96 | 2027-03-21 |
| D0200 | M102 | Visa | 447.78 | 2027-03-25 |
| D0209 | M121 | Visa | 257.13 | 2027-03-28 |
| D0217 | M120 | Mastercard | 252.09 | 2027-03-30 |
| D0218 | M101 | Visa | 271.37 | 2027-03-31 |

_6 rows._

**Watch out:** BETWEEN '2027-03-01' AND '2027-03-31' includes both ends but misses anything later than midnight on 31 March if the column has times. When mixing AND and OR, add parentheses: AND is evaluated before OR.

### 4. Find missing values

**Business question:** Which disputes are still open with no response yet?  
**Concepts:** IS NULL, IS NOT NULL

```sql
SELECT dispute_id, merchant_id, internal_status, response_due_at
FROM disputes
WHERE responded_at IS NULL
  AND closed_at IS NULL
ORDER BY response_due_at;
```

**How it works:** NULL means 'no value'. A dispute with no response date and no closed date is still waiting on the merchant. Sorting by due date puts the most urgent disputes at the top, which is exactly what the ops work queue needs.

**Expected result:**

| dispute_id | merchant_id | internal_status | response_due_at |
|---|---|---|---|
| D0372 | M102 | Awaiting evidence | 2027-06-21 |
| D0374 | M102 | Awaiting evidence | 2027-06-22 |
| D0353 | M104 | Awaiting evidence | 2027-06-23 |
| D0379 | M127 | Awaiting evidence | 2027-06-24 |
| D0359 | M104 | Awaiting evidence | 2027-06-25 |
| D0381 | M102 | Awaiting evidence | 2027-06-25 |
| D0382 | M120 | Awaiting evidence | 2027-06-25 |
| D0388 | M102 | Awaiting evidence | 2027-06-28 |

_Showing 8 of 22 rows._

**Watch out:** responded_at = NULL is never true, not even for missing values, so it returns nothing. Always use IS NULL or IS NOT NULL.

### 5. Search text

**Business question:** Which reason codes relate to fraud or authorization?  
**Concepts:** LIKE, wildcards, OR

```sql
SELECT reason_code, category, description
FROM reason_codes
WHERE category = 'Fraud'
   OR description LIKE '%authoriz%';
```

**How it works:** LIKE matches patterns: % stands for any number of characters, so '%authoriz%' finds the text anywhere in the description. OR keeps a row if either condition is true.

**Expected result:**

| reason_code | category | description |
|---|---|---|
| FR-01 | Fraud | Card-not-present transaction the cardholder says they didn't make |
| AU-07 | Authorization | Transaction processed without valid authorization |
| FR-09 | Fraud | Card-present counterfeit or skimmed card |

_3 rows._

**Watch out:** Case sensitivity differs by database. SQLite and MySQL (with default collation) ignore case for LIKE; PostgreSQL doesn't, so use ILIKE or LOWER(description) LIKE '%authoriz%'.

### 6. Unique values

**Business question:** Which card networks appear in the data?  
**Concepts:** DISTINCT

```sql
SELECT DISTINCT card_network
FROM disputes
ORDER BY card_network;
```

**How it works:** DISTINCT removes duplicate rows from the result, so each network appears once. With several columns, DISTINCT applies to the combination of values.

**Expected result:**

| card_network |
|---|
| Amex |
| Discover |
| Mastercard |
| Visa |

_4 rows._

**Watch out:** DISTINCT is often used to hide an accidental duplicate from a bad join. If you need it after a join, check the join first.

### 7. Calculated columns and dates

**Business question:** How many days did merchants take to respond?  
**Concepts:** Arithmetic, date functions

```sql
SELECT dispute_id,
       received_at,
       responded_at,
       julianday(responded_at) - julianday(received_at) AS days_to_respond
FROM disputes
WHERE responded_at IS NOT NULL
ORDER BY days_to_respond DESC
LIMIT 10;
```

**How it works:** julianday() turns a date into a day number, so subtracting two of them gives the days between. The calculation becomes a new column in the result without changing the table.

**Expected result:**

| dispute_id | received_at | responded_at | days_to_respond |
|---|---|---|---|
| D0057 | 2027-01-27 | 2027-02-26 | 30 |
| D0155 | 2027-03-09 | 2027-04-08 | 30 |
| D0186 | 2027-03-20 | 2027-04-19 | 30 |
| D0307 | 2027-05-03 | 2027-06-02 | 30 |
| D0005 | 2027-01-08 | 2027-02-06 | 29 |
| D0020 | 2027-01-14 | 2027-02-12 | 29 |
| D0047 | 2027-01-25 | 2027-02-22 | 28 |
| D0083 | 2027-02-07 | 2027-03-07 | 28 |

_Showing 8 of 10 rows._

**Watch out:** Any arithmetic with NULL returns NULL, which is why disputes without a response are filtered out first.

**Other databases:** PostgreSQL: responded_at::date - received_at::date. MySQL: DATEDIFF(responded_at, received_at). SQL Server: DATEDIFF(day, received_at, responded_at).

### 8. Categorize with CASE

**Business question:** Put each dispute into an amount band.  
**Concepts:** CASE WHEN

```sql
SELECT dispute_id,
       dispute_amount,
       CASE
         WHEN dispute_amount < 50   THEN 'Under $50'
         WHEN dispute_amount < 250  THEN '$50 to $249'
         WHEN dispute_amount < 1000 THEN '$250 to $999'
         ELSE '$1,000 and over'
       END AS amount_band
FROM disputes
ORDER BY dispute_amount DESC
LIMIT 10;
```

**How it works:** CASE checks conditions from top to bottom and returns the first match, so the order of the WHEN lines matters. ELSE catches everything left. CASE is the building block for bands, flags and pivots later on.

**Expected result:**

| dispute_id | dispute_amount | amount_band |
|---|---|---|
| D0193 | 1,161.96 | $1,000 and over |
| D0342 | 1,121.13 | $1,000 and over |
| D0062 | 1,101.35 | $1,000 and over |
| D0243 | 905.76 | $250 to $999 |
| D0192 | 862.44 | $250 to $999 |
| D0300 | 784.49 | $250 to $999 |
| D0306 | 687.93 | $250 to $999 |
| D0245 | 667.74 | $250 to $999 |

_Showing 8 of 10 rows._

**Watch out:** Without ELSE, rows that match no condition get NULL.


## Level 2: Aggregation

### 9. Summary numbers

**Business question:** How many disputes are there, and what's their total and average value?  
**Concepts:** COUNT, SUM, AVG, MIN, MAX, ROUND

```sql
SELECT COUNT(*)                     AS disputes,
       ROUND(SUM(dispute_amount), 2) AS total_usd,
       ROUND(AVG(dispute_amount), 2) AS average_usd,
       MIN(dispute_amount)           AS smallest_usd,
       MAX(dispute_amount)           AS largest_usd
FROM disputes;
```

**How it works:** Aggregate functions collapse many rows into one. With no GROUP BY, the whole table is one group. ROUND keeps currency readable.

**Expected result:**

| disputes | total_usd | average_usd | smallest_usd | largest_usd |
|---|---|---|---|---|
| 400 | 55,636.33 | 139.09 | 5.85 | 1,161.96 |

_1 row._

**Watch out:** AVG ignores NULLs. If missing values should count as zero, use AVG(COALESCE(column, 0)).

### 10. Group rows

**Business question:** How many disputes are in each status, and how much money is involved?  
**Concepts:** GROUP BY

```sql
SELECT internal_status,
       COUNT(*)                     AS disputes,
       ROUND(SUM(dispute_amount), 2) AS amount_usd
FROM disputes
GROUP BY internal_status
ORDER BY disputes DESC;
```

**How it works:** GROUP BY makes one output row per status, and each aggregate is calculated within its group. Every column in SELECT must either be in GROUP BY or be inside an aggregate function.

**Expected result:**

| internal_status | disputes | amount_usd |
|---|---|---|
| Lost | 115 | 16,406.24 |
| Won | 84 | 9,490.7 |
| Under review | 58 | 9,328.02 |
| Accepted | 37 | 5,771.58 |
| Expired | 32 | 4,940.03 |
| Evidence submitted | 28 | 4,491.17 |
| Partially won | 24 | 3,320.63 |
| Awaiting evidence | 22 | 1,887.96 |

_8 rows._

**Watch out:** SQLite and MySQL may let you select a column that isn't grouped and return an arbitrary value. PostgreSQL and SQL Server raise an error, which is safer.

### 11. Filter groups

**Business question:** Which merchants have more than 15 disputes?  
**Concepts:** HAVING

```sql
SELECT merchant_id,
       COUNT(*) AS disputes
FROM disputes
GROUP BY merchant_id
HAVING COUNT(*) > 15
ORDER BY disputes DESC;
```

**How it works:** WHERE filters rows before grouping; HAVING filters groups after the aggregates are calculated. To filter on a count or sum, you need HAVING.

**Expected result:**

| merchant_id | disputes |
|---|---|
| M105 | 44 |
| M102 | 44 |
| M104 | 42 |
| M101 | 36 |
| M106 | 31 |
| M103 | 21 |
| M125 | 19 |

_7 rows._

**Watch out:** Put ordinary row filters in WHERE, not HAVING. It is clearer and usually faster because fewer rows are grouped.

### 12. Three kinds of COUNT

**Business question:** How many disputes have responses and outcomes, and how many merchants have disputes?  
**Concepts:** COUNT(*), COUNT(column), COUNT(DISTINCT)

```sql
SELECT COUNT(*)                    AS all_disputes,
       COUNT(responded_at)         AS with_response,
       COUNT(outcome)              AS with_outcome,
       COUNT(DISTINCT merchant_id) AS merchants_with_disputes
FROM disputes;
```

**How it works:** COUNT(*) counts rows. COUNT(column) counts rows where that column isn't NULL. COUNT(DISTINCT column) counts unique non-null values. One query shows how much data is filled in.

**Expected result:**

| all_disputes | with_response | with_outcome | merchants_with_disputes |
|---|---|---|---|
| 400 | 346 | 291 | 30 |

_1 row._

**Watch out:** This is a quick data completeness check before building any KPI.

### 13. Group by month

**Business question:** How many disputes arrived each month?  
**Concepts:** Date truncation, GROUP BY expression

```sql
SELECT strftime('%Y-%m', received_at) AS month,
       COUNT(*)                        AS disputes,
       ROUND(SUM(dispute_amount), 2)    AS amount_usd
FROM disputes
GROUP BY month
ORDER BY month;
```

**How it works:** strftime('%Y-%m', ...) turns each date into its year and month, and grouping by that value gives a monthly trend. Year-month text sorts correctly as text.

**Expected result:**

| month | disputes | amount_usd |
|---|---|---|
| 2027-01 | 70 | 10,163.43 |
| 2027-02 | 61 | 8,359.55 |
| 2027-03 | 90 | 10,541.78 |
| 2027-04 | 77 | 12,375.9 |
| 2027-05 | 74 | 11,678.24 |
| 2027-06 | 28 | 2,517.43 |

_6 rows._

**Watch out:** Grouping by the month number alone would merge January 2027 with January 2028.

**Other databases:** PostgreSQL: DATE_TRUNC('month', received_at). MySQL: DATE_FORMAT(received_at, '%Y-%m'). SQL Server: FORMAT(received_at, 'yyyy-MM') or DATETRUNC(month, received_at).

### 14. Pivot with conditional aggregation

**Business question:** How did responses split between portal and email each month?  
**Concepts:** SUM(CASE WHEN ...), percentages

```sql
SELECT strftime('%Y-%m', responded_at) AS month,
       SUM(CASE WHEN response_channel = 'Portal' THEN 1 ELSE 0 END) AS portal,
       SUM(CASE WHEN response_channel = 'Email'  THEN 1 ELSE 0 END) AS email,
       ROUND(100.0 * SUM(CASE WHEN response_channel = 'Portal' THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS portal_share_pct
FROM disputes
WHERE responded_at IS NOT NULL
GROUP BY month
ORDER BY month;
```

**How it works:** Each CASE turns a row into 1 or 0, and SUM adds them up, so one pass over the data produces several columns. This pattern is behind most KPI tables and works in every database.

**Expected result:**

| month | portal | email | portal_share_pct |
|---|---|---|---|
| 2027-01 | 4 | 25 | 13.8 |
| 2027-02 | 9 | 63 | 12.5 |
| 2027-03 | 25 | 41 | 37.9 |
| 2027-04 | 33 | 35 | 48.5 |
| 2027-05 | 43 | 33 | 56.6 |
| 2027-06 | 23 | 12 | 65.7 |

_6 rows._

**Watch out:** Write 100.0, not 100. Some databases divide whole numbers as integers, so 45 / 60 becomes 0.


## Level 3: Joins and set operations

### 15. Inner join

**Business question:** Show the largest travel and hospitality disputes with merchant names.  
**Concepts:** INNER JOIN, table aliases

```sql
SELECT d.dispute_id,
       m.merchant_name,
       m.segment,
       d.dispute_amount
FROM disputes d
JOIN merchants m ON m.merchant_id = d.merchant_id
WHERE m.segment = 'Travel & hospitality'
ORDER BY d.dispute_amount DESC
LIMIT 10;
```

**How it works:** JOIN (short for INNER JOIN) matches each dispute to its merchant using merchant_id and keeps only rows that match on both sides. Aliases d and m keep the query short and make it clear which table each column comes from.

**Expected result:**

| dispute_id | merchant_name | segment | dispute_amount |
|---|---|---|---|
| D0192 | Coastal Air Tours | Travel & hospitality | 862.44 |
| D0306 | Skyline Stays | Travel & hospitality | 687.93 |
| D0089 | Skyline Stays | Travel & hospitality | 582.51 |
| D0092 | Skyline Stays | Travel & hospitality | 576.84 |
| D0371 | Coastal Air Tours | Travel & hospitality | 506.85 |
| D0113 | TrailPass Travel | Travel & hospitality | 461.79 |
| D0309 | Coastal Air Tours | Travel & hospitality | 439.38 |
| D0072 | Coastal Air Tours | Travel & hospitality | 430.02 |

_Showing 8 of 10 rows._

**Watch out:** If the key isn't unique on one side, rows multiply. Check that merchant_id is unique in merchants before trusting totals.

### 16. Join then aggregate

**Business question:** How do dispute volume and average value differ by merchant segment?  
**Concepts:** JOIN with GROUP BY

```sql
SELECT m.segment,
       COUNT(*)                        AS disputes,
       ROUND(AVG(d.dispute_amount), 2) AS avg_amount_usd
FROM disputes d
JOIN merchants m ON m.merchant_id = d.merchant_id
GROUP BY m.segment
ORDER BY disputes DESC;
```

**How it works:** The join adds segment to every dispute row, then GROUP BY summarizes by segment. This is the most common shape of a business report query.

**Expected result:**

| segment | disputes | avg_amount_usd |
|---|---|---|
| Enterprise e-commerce | 218 | 118.61 |
| Mid-market online retail | 66 | 128.52 |
| Travel & hospitality | 43 | 265.3 |
| Subscription & digital services | 39 | 108.98 |
| Marketplaces & platforms | 24 | 149.31 |
| Small card-present | 10 | 205.52 |

_6 rows._

### 17. Left join to keep everything

**Business question:** How many portal users does each merchant have, including merchants with none?  
**Concepts:** LEFT JOIN, COUNT on the right table

```sql
SELECT m.merchant_name,
       m.rollout_wave,
       COUNT(u.user_id) AS portal_users
FROM merchants m
LEFT JOIN portal_users u ON u.merchant_id = m.merchant_id
GROUP BY m.merchant_id, m.merchant_name, m.rollout_wave
ORDER BY portal_users, m.merchant_name;
```

**How it works:** LEFT JOIN keeps every merchant even when no user matches; the user columns are NULL for those merchants. COUNT(u.user_id) counts only real matches, so merchants without users show 0.

**Expected result:**

| merchant_name | rollout_wave | portal_users |
|---|---|---|
| City Barber | General availability | 0 |
| CloudMeal Plans | Wave 2 | 0 |
| Coastal Air Tours | Wave 2 | 0 |
| Corner Cafe | General availability | 0 |
| CraftBazaar | Later phase | 0 |
| Green Leaf Florist | General availability | 0 |
| Main St Hardware | General availability | 0 |
| MarketHub | Later phase | 0 |

_Showing 8 of 30 rows._

**Watch out:** COUNT(*) would return 1 for merchants with no users, because the unmatched row still exists.

### 18. Find rows with no match

**Business question:** Which disputes have a reason code that isn't in the reference table?  
**Concepts:** Anti-join with LEFT JOIN ... IS NULL

```sql
SELECT d.dispute_id, d.reason_code, d.received_at
FROM disputes d
LEFT JOIN reason_codes r ON r.reason_code = d.reason_code
WHERE r.reason_code IS NULL;
```

**How it works:** The LEFT JOIN tries to find each dispute's reason code. Where none exists, the reference columns are NULL, and the WHERE clause keeps exactly those rows. This is how the unmapped-code issue (I-02) would be found in real data.

**Expected result:**

| dispute_id | reason_code | received_at |
|---|---|---|
| D0058 | ZZ-99 | 2027-01-29 |
| D0213 | ZZ-99 | 2027-03-29 |

_2 rows._

**Watch out:** NOT IN (SELECT reason_code FROM reason_codes) returns nothing at all if the subquery contains a NULL. LEFT JOIN ... IS NULL or NOT EXISTS avoids that trap.

### 19. Filter in ON versus WHERE

**Business question:** How many quarantined evidence files does each portal-enabled merchant have, including zero?  
**Concepts:** Conditions in the ON clause of a LEFT JOIN, chained joins

```sql
SELECT m.merchant_name,
       COUNT(f.file_id) AS quarantined_files
FROM merchants m
LEFT JOIN disputes d
       ON d.merchant_id = m.merchant_id
LEFT JOIN evidence_files f
       ON f.dispute_id = d.dispute_id
      AND f.redaction_status = 'Quarantined'
WHERE m.portal_enabled_date IS NOT NULL
GROUP BY m.merchant_id, m.merchant_name
ORDER BY quarantined_files DESC, m.merchant_name;
```

**How it works:** The quarantine condition sits in the ON clause, so it only decides which files match. Merchants with no quarantined files still appear with 0. The WHERE clause filters merchants, which is safe because it's about the left table.

**Expected result:**

| merchant_name | quarantined_files |
|---|---|
| Northwind Outfitters | 3 |
| Cedar & Pine Home | 2 |
| Atlas Sportswear | 1 |
| Bluefin Electronics | 1 |
| Copperleaf Kitchen | 1 |
| Harbor Lane Apparel | 1 |
| Lumen Lighting | 1 |
| Summit Gear Co | 1 |

_Showing 8 of 19 rows._

**Watch out:** Moving f.redaction_status = 'Quarantined' into WHERE silently turns the LEFT JOIN into an INNER JOIN and drops every merchant with zero.

### 20. Self-join

**Business question:** Are there possible duplicate disputes: same merchant, amount and date?  
**Concepts:** Joining a table to itself

```sql
SELECT a.dispute_id AS first_id,
       b.dispute_id AS second_id,
       a.merchant_id,
       a.dispute_amount,
       a.received_at
FROM disputes a
JOIN disputes b
  ON  a.merchant_id    = b.merchant_id
  AND a.dispute_amount = b.dispute_amount
  AND a.received_at    = b.received_at
  AND a.dispute_id     < b.dispute_id;
```

**How it works:** The same table is used twice under different aliases. Matching on merchant, amount and date finds pairs that look identical. a.dispute_id < b.dispute_id stops a row matching itself and stops each pair appearing twice.

**Expected result:**

| first_id | second_id | merchant_id | dispute_amount | received_at |
|---|---|---|---|---|
| D0121 | D0400 | M105 | 37.38 | 2027-02-21 |

_1 row._

**Watch out:** Using <> instead of < returns every pair twice (A-B and B-A).

### 21. Stack results with UNION ALL

**Business question:** Show a timeline of disputes and servicing contacts for merchant M101.  
**Concepts:** UNION ALL, string concatenation

```sql
SELECT contact_at AS happened_at,
       'Servicing contact: ' || reason AS activity
FROM servicing_contacts
WHERE merchant_id = 'M101'
UNION ALL
SELECT received_at,
       'Dispute received: ' || dispute_id
FROM disputes
WHERE merchant_id = 'M101'
ORDER BY happened_at
LIMIT 12;
```

**How it works:** UNION ALL stacks two result sets with the same number of columns. Column names come from the first SELECT, and ORDER BY at the end sorts the combined list.

**Expected result:**

| happened_at | activity |
|---|---|
| 2027-01-08 | Dispute received: D0003 |
| 2027-01-22 | Dispute received: D0036 |
| 2027-01-27 | Dispute received: D0052 |
| 2027-01-29 | Dispute received: D0058 |
| 2027-02-01 | Dispute received: D0071 |
| 2027-02-05 | Dispute received: D0079 |
| 2027-02-14 | Dispute received: D0105 |
| 2027-02-14 | Dispute received: D0106 |

_Showing 8 of 12 rows._

**Watch out:** UNION (without ALL) also removes duplicate rows, which costs extra work and can hide genuine repeats. Use UNION ALL unless you need duplicates removed.

**Other databases:** String concatenation: || in SQLite, PostgreSQL and Oracle; CONCAT() in MySQL; + or CONCAT() in SQL Server.


## Level 4: Subqueries and CTEs

### 22. Scalar subquery

**Business question:** Which disputes are larger than the average dispute?  
**Concepts:** Subquery that returns one value

```sql
SELECT dispute_id, merchant_id, dispute_amount
FROM disputes
WHERE dispute_amount > (SELECT AVG(dispute_amount) FROM disputes)
ORDER BY dispute_amount DESC
LIMIT 10;
```

**How it works:** The inner query runs once and returns a single number, the average amount. The outer query compares every dispute to it.

**Expected result:**

| dispute_id | merchant_id | dispute_amount |
|---|---|---|
| D0193 | M129 | 1,161.96 |
| D0342 | M103 | 1,121.13 |
| D0062 | M106 | 1,101.35 |
| D0243 | M110 | 905.76 |
| D0192 | M121 | 862.44 |
| D0300 | M105 | 784.49 |
| D0306 | M120 | 687.93 |
| D0245 | M111 | 667.74 |

_Showing 8 of 10 rows._

**Watch out:** You can't write WHERE dispute_amount > AVG(dispute_amount): aggregates aren't allowed in WHERE. A subquery (or a window function) solves it.

### 23. EXISTS

**Business question:** Which merchants have at least one quarantined evidence file?  
**Concepts:** Correlated EXISTS

```sql
SELECT m.merchant_id, m.merchant_name
FROM merchants m
WHERE EXISTS (
  SELECT 1
  FROM disputes d
  JOIN evidence_files f ON f.dispute_id = d.dispute_id
  WHERE d.merchant_id = m.merchant_id
    AND f.redaction_status = 'Quarantined'
)
ORDER BY m.merchant_name;
```

**How it works:** EXISTS asks 'is there at least one matching row?' for each merchant. It stops at the first match and never duplicates merchants, unlike a join followed by DISTINCT. SELECT 1 is a convention; the selected value is ignored.

**Expected result:**

| merchant_id | merchant_name |
|---|---|
| M104 | Atlas Sportswear |
| M102 | Bluefin Electronics |
| M103 | Cedar & Pine Home |
| M109 | Copperleaf Kitchen |
| M105 | Harbor Lane Apparel |
| M113 | Lumen Lighting |
| M101 | Northwind Outfitters |
| M106 | Summit Gear Co |

_8 rows._

### 24. CTEs step by step

**Business question:** What share of evidence responses came through the portal in each rollout wave?  
**Concepts:** WITH, multiple CTEs, NULL-safe filters

```sql
WITH evidence_responses AS (
  SELECT d.dispute_id, d.response_channel, m.rollout_wave
  FROM disputes d
  JOIN merchants m ON m.merchant_id = d.merchant_id
  WHERE d.responded_at IS NOT NULL
    AND (d.outcome IS NULL OR d.outcome <> 'Accepted')
),
by_wave AS (
  SELECT rollout_wave,
         COUNT(*) AS packages,
         SUM(CASE WHEN response_channel = 'Portal' THEN 1 ELSE 0 END) AS via_portal
  FROM evidence_responses
  GROUP BY rollout_wave
)
SELECT rollout_wave,
       packages,
       via_portal,
       ROUND(100.0 * via_portal / packages, 1) AS portal_share_pct
FROM by_wave
ORDER BY portal_share_pct DESC;
```

**How it works:** A CTE (WITH ... AS) names an intermediate result so the logic reads top to bottom: first choose the rows that count as evidence responses, then summarize by wave, then calculate the share. Each step can be checked on its own by selecting from it.

**Expected result:**

| rollout_wave | packages | via_portal | portal_share_pct |
|---|---|---|---|
| Pilot | 79 | 68 | 86.1 |
| Wave 1 | 149 | 52 | 34.9 |
| General availability | 5 | 0 | 0 |
| Later phase | 21 | 0 | 0 |
| Wave 2 | 55 | 0 | 0 |

_5 rows._

**Watch out:** d.outcome <> 'Accepted' alone would drop open disputes, because comparing NULL to anything is unknown, not true. That's why the filter also allows outcome IS NULL.

### 25. Avoid join fan-out

**Business question:** What are total disputes and total settlement debits per merchant?  
**Concepts:** Pre-aggregating before joining

```sql
WITH dispute_totals AS (
  SELECT merchant_id, COUNT(*) AS disputes
  FROM disputes
  GROUP BY merchant_id
),
settlement_totals AS (
  SELECT merchant_id, SUM(chargeback_debits) AS debits_usd
  FROM settlements
  GROUP BY merchant_id
)
SELECT m.merchant_name,
       dt.disputes,
       ROUND(st.debits_usd, 2) AS settlement_debits_usd
FROM merchants m
LEFT JOIN dispute_totals    dt ON dt.merchant_id = m.merchant_id
LEFT JOIN settlement_totals st ON st.merchant_id = m.merchant_id
ORDER BY settlement_debits_usd DESC
LIMIT 10;
```

**How it works:** Each table is summarized to one row per merchant first, then the summaries are joined. Because both sides are already one row per merchant, nothing is double counted.

**Expected result:**

| merchant_name | disputes | settlement_debits_usd |
|---|---|---|
| Cedar & Pine Home | 21 | 2,985.77 |
| Bluefin Electronics | 44 | 2,582.15 |
| Coastal Air Tours | 14 | 2,528.28 |
| Atlas Sportswear | 42 | 2,472.21 |
| Harbor Lane Apparel | 44 | 2,445.28 |
| CraftBazaar | 19 | 2,411.56 |
| Northwind Outfitters | 36 | 2,226.86 |
| Summit Gear Co | 31 | 1,949.81 |

_Showing 8 of 10 rows._

**Watch out:** Joining disputes directly to settlements and then summing would repeat each settlement row once per dispute, inflating totals many times over. This is one of the most common mistakes in interview exercises and real reports.

### 26. Correlated subquery

**Business question:** What is the latest status event for each dispute?  
**Concepts:** Subquery that refers to the outer row

```sql
SELECT e.dispute_id, e.internal_status, e.processor_event_at
FROM status_events e
WHERE e.processor_event_at = (
  SELECT MAX(e2.processor_event_at)
  FROM status_events e2
  WHERE e2.dispute_id = e.dispute_id
)
ORDER BY e.dispute_id
LIMIT 10;
```

**How it works:** For each event row, the inner query finds the latest timestamp for that same dispute. Only the row with that timestamp is kept.

**Expected result:**

| dispute_id | internal_status | processor_event_at |
|---|---|---|
| D0001 | Lost | 2027-02-18 16:36:42 |
| D0002 | Won | 2027-03-16 09:21:38 |
| D0003 | Won | 2027-03-07 14:20:23 |
| D0004 | Lost | 2027-03-05 14:10:08 |
| D0005 | Won | 2027-03-05 17:08:19 |
| D0006 | Expired | 2027-01-30 14:17:52 |
| D0007 | Won | 2027-03-14 14:50:24 |
| D0008 | Lost | 2027-03-15 08:06:16 |

_Showing 8 of 10 rows._

**Watch out:** Correlated subqueries run once per outer row and can be slow on large tables, and ties return more than one row. The next level shows the window function version.


## Level 5: Window functions

### 27. ROW_NUMBER for latest record

**Business question:** Does each dispute's latest status event agree with the status stored on the dispute?  
**Concepts:** ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)

```sql
WITH ranked AS (
  SELECT dispute_id,
         internal_status,
         processor_event_at,
         ROW_NUMBER() OVER (
           PARTITION BY dispute_id
           ORDER BY processor_event_at DESC, event_id DESC
         ) AS rn
  FROM status_events
)
SELECT r.dispute_id,
       r.internal_status AS latest_event_status,
       d.internal_status AS dispute_status
FROM ranked r
JOIN disputes d ON d.dispute_id = r.dispute_id
WHERE r.rn = 1
  AND r.internal_status <> d.internal_status;
```

**How it works:** PARTITION BY restarts numbering for every dispute, and ORDER BY ... DESC gives the newest event number 1. Keeping rn = 1 returns exactly one latest event per dispute, even when timestamps tie. Comparing it with the disputes table is a consistency test: no rows means the two agree.

**Expected result:**

_No rows returned._

**Watch out:** Window functions can't be used directly in WHERE because they're calculated after WHERE. Wrap them in a CTE or subquery, then filter.

### 28. Rank within groups

**Business question:** Who are the top two merchants by disputed value in each segment?  
**Concepts:** RANK, top N per group

```sql
WITH totals AS (
  SELECT m.segment,
         m.merchant_name,
         SUM(d.dispute_amount) AS disputed_usd
  FROM disputes d
  JOIN merchants m ON m.merchant_id = d.merchant_id
  GROUP BY m.segment, m.merchant_name
),
ranked AS (
  SELECT segment,
         merchant_name,
         ROUND(disputed_usd, 2) AS disputed_usd,
         RANK() OVER (PARTITION BY segment ORDER BY disputed_usd DESC) AS rank_in_segment
  FROM totals
)
SELECT *
FROM ranked
WHERE rank_in_segment <= 2
ORDER BY segment, rank_in_segment;
```

**How it works:** RANK numbers rows within each segment by value. Filtering rank_in_segment <= 2 gives a top-two list per segment, a very common interview question.

**Expected result:**

| segment | merchant_name | disputed_usd | rank_in_segment |
|---|---|---|---|
| Enterprise e-commerce | Harbor Lane Apparel | 5,773.69 | 1 |
| Enterprise e-commerce | Atlas Sportswear | 4,308.81 | 2 |
| Marketplaces & platforms | CraftBazaar | 3,243.55 | 1 |
| Marketplaces & platforms | MarketHub | 339.97 | 2 |
| Mid-market online retail | Juniper Toys | 2,165.94 | 1 |
| Mid-market online retail | Riverstone Pets | 1,431.58 | 2 |
| Small card-present | Sunny Laundry | 1,228.28 | 1 |
| Small card-present | City Barber | 272.37 | 2 |

_Showing 8 of 12 rows._

**Watch out:** RANK leaves gaps after ties (1, 1, 3), DENSE_RANK doesn't (1, 1, 2), and ROW_NUMBER never ties (1, 2, 3). Pick the one that matches how ties should be treated.

### 29. Running total

**Business question:** How did the cumulative number of disputes grow month by month?  
**Concepts:** SUM() OVER with a frame

```sql
WITH monthly AS (
  SELECT strftime('%Y-%m', received_at) AS month,
         COUNT(*) AS disputes
  FROM disputes
  GROUP BY month
)
SELECT month,
       disputes,
       SUM(disputes) OVER (
         ORDER BY month
         ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total
FROM monthly
ORDER BY month;
```

**How it works:** A window SUM keeps every row (unlike GROUP BY) and adds a column. The frame 'from the first row to the current row' turns it into a running total.

**Expected result:**

| month | disputes | running_total |
|---|---|---|
| 2027-01 | 70 | 70 |
| 2027-02 | 61 | 131 |
| 2027-03 | 90 | 221 |
| 2027-04 | 77 | 298 |
| 2027-05 | 74 | 372 |
| 2027-06 | 28 | 400 |

_6 rows._

**Watch out:** Without an explicit frame, many databases use RANGE, which lumps together rows with the same ORDER BY value. ROWS BETWEEN is predictable.

### 30. Compare with the previous period

**Business question:** How did the portal share of evidence responses change month over month?  
**Concepts:** LAG

```sql
WITH monthly AS (
  SELECT strftime('%Y-%m', responded_at) AS month,
         ROUND(100.0 * SUM(CASE WHEN response_channel = 'Portal' THEN 1 ELSE 0 END)
               / COUNT(*), 1) AS portal_pct
  FROM disputes
  WHERE responded_at IS NOT NULL
    AND (outcome IS NULL OR outcome <> 'Accepted')
  GROUP BY month
)
SELECT month,
       portal_pct,
       LAG(portal_pct) OVER (ORDER BY month) AS previous_month_pct,
       ROUND(portal_pct - LAG(portal_pct) OVER (ORDER BY month), 1) AS change_pts
FROM monthly
ORDER BY month;
```

**How it works:** LAG looks back one row in the ORDER BY sequence, so each month can be compared with the one before. LEAD looks forward. The first month has no previous value, so it's NULL.

**Expected result:**

| month | portal_pct | previous_month_pct | change_pts |
|---|---|---|---|
| 2027-01 | 12.5 | NULL | NULL |
| 2027-02 | 11.9 | 12.5 | -0.6 |
| 2027-03 | 38.3 | 11.9 | 26.4 |
| 2027-04 | 48.3 | 38.3 | 10 |
| 2027-05 | 54.4 | 48.3 | 6.1 |
| 2027-06 | 66.7 | 54.4 | 12.3 |

_6 rows._

**Watch out:** Report the change in percentage points, not percent, when comparing two percentages.

### 31. Moving average

**Business question:** What's the four-week moving average of new disputes?  
**Concepts:** AVG() OVER with ROWS BETWEEN n PRECEDING

```sql
WITH weekly AS (
  SELECT strftime('%Y-%W', received_at) AS week,
         COUNT(*) AS disputes
  FROM disputes
  GROUP BY week
)
SELECT week,
       disputes,
       ROUND(AVG(disputes) OVER (
         ORDER BY week
         ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
       ), 1) AS moving_avg_4_weeks
FROM weekly
ORDER BY week;
```

**How it works:** The frame covers the current week and the three before it, smoothing out week-to-week noise so the trend is easier to see.

**Expected result:**

| week | disputes | moving_avg_4_weeks |
|---|---|---|
| 2027-01 | 10 | 10 |
| 2027-02 | 18 | 14 |
| 2027-03 | 18 | 15.3 |
| 2027-04 | 24 | 17.5 |
| 2027-05 | 15 | 18.8 |
| 2027-06 | 21 | 19.5 |
| 2027-07 | 17 | 19.3 |
| 2027-08 | 8 | 15.3 |

_Showing 8 of 23 rows._

**Watch out:** The first three weeks average fewer than four weeks of data. Weeks with no disputes are missing rows, not zeros; for a strict moving average, join to a calendar first.

**Other databases:** PostgreSQL: TO_CHAR(received_at, 'IYYY-IW'). MySQL: YEARWEEK(received_at, 3). SQL Server: DATEPART(iso_week, received_at).

### 32. Percent of total

**Business question:** What share of disputes does each reason code represent?  
**Concepts:** SUM(COUNT(*)) OVER ()

```sql
SELECT reason_code,
       COUNT(*) AS disputes,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_all
FROM disputes
GROUP BY reason_code
ORDER BY disputes DESC;
```

**How it works:** GROUP BY produces one count per reason code. SUM(COUNT(*)) OVER () then adds up all those counts across the whole result (an empty OVER means 'all rows'), giving the denominator without a second query.

**Expected result:**

| reason_code | disputes | pct_of_all |
|---|---|---|
| CR-04 | 80 | 20 |
| FR-01 | 70 | 17.5 |
| NR-02 | 64 | 16 |
| NA-03 | 61 | 15.3 |
| DP-05 | 56 | 14 |
| AU-07 | 42 | 10.5 |
| LP-08 | 15 | 3.8 |
| CX-06 | 8 | 2 |

_Showing 8 of 10 rows._

### 33. 95th percentile without a percentile function

**Business question:** What is the 95th percentile status sync latency in minutes (KPI-12)?  
**Concepts:** ROW_NUMBER and COUNT() OVER, nearest-rank percentile

```sql
WITH latency AS (
  SELECT (julianday(hub_updated_at) - julianday(processor_event_at)) * 24 * 60 AS minutes
  FROM status_events
),
ranked AS (
  SELECT minutes,
         ROW_NUMBER() OVER (ORDER BY minutes) AS rn,
         COUNT(*) OVER ()                    AS n
  FROM latency
)
SELECT ROUND(MIN(minutes), 2) AS p95_minutes
FROM ranked
WHERE rn >= 0.95 * n;
```

**How it works:** Each latency is converted to minutes and numbered from fastest to slowest. The 95th percentile is the first value at or beyond 95% of the rows. This 'nearest rank' method works in any database with window functions.

**Expected result:**

| p95_minutes |
|---|
| 11.45 |

_1 row._

**Watch out:** Averages hide slow outliers, which is why the KPI uses p95. The target in the KPI catalog is 5 minutes.

**Other databases:** PostgreSQL: PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY minutes). SQL Server: PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY minutes) OVER (). BigQuery: APPROX_QUANTILES(minutes, 100)[OFFSET(95)].


## Level 6: KPI queries

### 34. KPI-02 win rate three ways

**Business question:** Why do Finance and Ops report different win rates?  
**Concepts:** Conditional aggregation, NULLIF

```sql
SELECT COUNT(*) AS closed_disputes,
       ROUND(100.0 * SUM(CASE WHEN outcome = 'Won' THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS finance_method_pct,
       ROUND(100.0 * SUM(CASE WHEN outcome IN ('Won', 'Partially won') THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN outcome IN ('Won', 'Partially won', 'Lost') THEN 1 ELSE 0 END), 0), 1) AS ops_method_pct,
       ROUND(100.0 * SUM(CASE WHEN outcome = 'Won' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN outcome IN ('Won', 'Partially won', 'Lost') THEN 1 ELSE 0 END), 0), 1) AS proposed_win_rate_pct,
       ROUND(100.0 * SUM(CASE WHEN outcome = 'Partially won' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN outcome IN ('Won', 'Partially won', 'Lost') THEN 1 ELSE 0 END), 0), 1) AS proposed_partial_rate_pct
FROM disputes
WHERE outcome IS NOT NULL;
```

**How it works:** The same closed disputes are counted three ways. Finance divides wins by every closed dispute, including accepted and expired ones. Ops counts partial wins as wins and only uses contested disputes. The proposed definition (CR-05) uses contested disputes as the denominator and reports partial wins separately.

**Expected result:**

| closed_disputes | finance_method_pct | ops_method_pct | proposed_win_rate_pct | proposed_partial_rate_pct |
|---|---|---|---|---|
| 291 | 28.9 | 48.6 | 37.8 | 10.8 |

_1 row._

**Watch out:** NULLIF(denominator, 0) returns NULL instead of a divide-by-zero error when a group has no contested disputes. It matters once you add GROUP BY.

### 35. Win rate by response channel

**Business question:** Do portal responses win more often than email responses?  
**Concepts:** Grouped KPI

```sql
SELECT response_channel,
       SUM(CASE WHEN outcome IN ('Won', 'Partially won', 'Lost') THEN 1 ELSE 0 END) AS contested,
       ROUND(100.0 * SUM(CASE WHEN outcome = 'Won' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN outcome IN ('Won', 'Partially won', 'Lost') THEN 1 ELSE 0 END), 0), 1) AS win_rate_pct
FROM disputes
WHERE outcome IS NOT NULL
  AND response_channel IS NOT NULL
GROUP BY response_channel;
```

**How it works:** Grouping the proposed win-rate calculation by channel compares portal and email outcomes.

**Expected result:**

| response_channel | contested | win_rate_pct |
|---|---|---|
| Email | 151 | 33.8 |
| Portal | 71 | 46.5 |

_2 rows._

**Watch out:** This shows correlation, not proof. Portal merchants in this data are mostly larger enterprise merchants, so compare within a segment before claiming the portal caused better outcomes.

### 36. KPI-01 value recovery rate

**Business question:** What share of contested dispute value was recovered each month?  
**Concepts:** SUM ratio by period

```sql
SELECT strftime('%Y-%m', closed_at) AS month_closed,
       ROUND(SUM(recovered_amount), 2) AS recovered_usd,
       ROUND(SUM(dispute_amount), 2)   AS contested_usd,
       ROUND(100.0 * SUM(recovered_amount) / NULLIF(SUM(dispute_amount), 0), 1) AS recovery_pct
FROM disputes
WHERE outcome IN ('Won', 'Partially won', 'Lost')
GROUP BY month_closed
ORDER BY month_closed;
```

**How it works:** This KPI weights disputes by money, so one large partial win can move it more than several small wins. It sums recovered and contested amounts before dividing.

**Expected result:**

| month_closed | recovered_usd | contested_usd | recovery_pct |
|---|---|---|---|
| 2027-02 | 44.33 | 970.02 | 4.6 |
| 2027-03 | 2,083.4 | 7,834.8 | 26.6 |
| 2027-04 | 4,019.48 | 8,502.69 | 47.3 |
| 2027-05 | 2,033 | 6,436.41 | 31.6 |
| 2027-06 | 2,852 | 5,403 | 52.8 |

_5 rows._

**Watch out:** Averaging per-dispute recovery percentages gives a different (and usually wrong) answer. Divide the sums, not the average of ratios. Also check the data quality level: one record recovers more than was disputed.

### 37. KPI-03 on-time response rate

**Business question:** What share of disputes due each month were answered on time?  
**Concepts:** Deadline logic with NULLs

```sql
SELECT strftime('%Y-%m', response_due_at) AS due_month,
       COUNT(*) AS disputes_due,
       SUM(CASE WHEN responded_at IS NOT NULL
                 AND responded_at <= response_due_at THEN 1 ELSE 0 END) AS on_time,
       ROUND(100.0 * SUM(CASE WHEN responded_at IS NOT NULL
                               AND responded_at <= response_due_at THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS on_time_pct
FROM disputes
WHERE response_due_at <= '2027-06-15'
GROUP BY due_month
ORDER BY due_month;
```

**How it works:** The denominator is every dispute whose deadline has already passed as of the reporting date, grouped by the month it was due. A dispute is on time if a response exists and is on or before the due date.

**Expected result:**

| due_month | disputes_due | on_time | on_time_pct |
|---|---|---|---|
| 2027-01 | 3 | 2 | 66.7 |
| 2027-02 | 74 | 70 | 94.6 |
| 2027-03 | 65 | 60 | 92.3 |
| 2027-04 | 83 | 70 | 84.3 |
| 2027-05 | 90 | 84 | 93.3 |
| 2027-06 | 36 | 33 | 91.7 |

_6 rows._

**Watch out:** Including disputes that aren't due yet would make the rate look worse, because they can't have been answered 'on time' yet.

### 38. KPI-04 missed-deadline loss rate

**Business question:** Which segments lose the most disputes to missed deadlines?  
**Concepts:** KPI by segment

```sql
SELECT m.segment,
       COUNT(*) AS closed_disputes,
       SUM(CASE WHEN d.outcome = 'Expired' THEN 1 ELSE 0 END) AS expired,
       ROUND(100.0 * SUM(CASE WHEN d.outcome = 'Expired' THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS missed_deadline_pct
FROM disputes d
JOIN merchants m ON m.merchant_id = d.merchant_id
WHERE d.outcome IS NOT NULL
GROUP BY m.segment
ORDER BY missed_deadline_pct DESC;
```

**How it works:** Expired disputes are lost without a fight. Splitting the rate by segment shows where reminders and onboarding would help most.

**Expected result:**

| segment | closed_disputes | expired | missed_deadline_pct |
|---|---|---|---|
| Travel & hospitality | 34 | 10 | 29.4 |
| Small card-present | 7 | 2 | 28.6 |
| Mid-market online retail | 47 | 8 | 17 |
| Subscription & digital services | 24 | 2 | 8.3 |
| Marketplaces & platforms | 15 | 1 | 6.7 |
| Enterprise e-commerce | 164 | 9 | 5.5 |

_6 rows._

**Watch out:** Small groups swing wildly. Always show the count next to the percentage.

### 39. KPI-05 ops handling time

**Business question:** How long does ops spend per work item, by team and queue?  
**Concepts:** Timestamp differences, joins, AVG

```sql
SELECT a.team,
       w.queue_reason,
       COUNT(*) AS items,
       ROUND(AVG((julianday(w.resolved_at) - julianday(w.assigned_at)) * 24 * 60), 1) AS avg_minutes
FROM ops_work_items w
JOIN analysts a ON a.analyst_id = w.analyst_id
WHERE w.resolved_at IS NOT NULL
GROUP BY a.team, w.queue_reason
ORDER BY a.team, avg_minutes DESC;
```

**How it works:** Multiplying the day difference by 24 and 60 converts it to minutes. Comparing email intake with portal review shows the handling time saving the business case depends on.

**Expected result:**

| team | queue_reason | items | avg_minutes |
|---|---|---|---|
| Team Alpha | Email evidence intake | 107 | 42.9 |
| Team Alpha | Portal submission review | 14 | 24.9 |
| Team Beta | Email evidence intake | 101 | 42.8 |
| Team Beta | Portal submission review | 23 | 25.8 |

_4 rows._

**Watch out:** Unresolved items have no end time; exclude them, or they'd need a separate 'still open' age measure.

**Other databases:** PostgreSQL: EXTRACT(EPOCH FROM resolved_at - assigned_at) / 60. MySQL: TIMESTAMPDIFF(MINUTE, assigned_at, resolved_at). SQL Server: DATEDIFF(minute, assigned_at, resolved_at).

### 40. KPI-06 portal share with a fair denominator

**Business question:** What share of evidence came through the portal from merchants who actually had the portal?  
**Concepts:** Filtering the eligible population

```sql
WITH eligible AS (
  SELECT d.dispute_id, d.responded_at, d.response_channel
  FROM disputes d
  JOIN merchants m ON m.merchant_id = d.merchant_id
  WHERE d.responded_at IS NOT NULL
    AND (d.outcome IS NULL OR d.outcome <> 'Accepted')
    AND m.portal_enabled_date IS NOT NULL
    AND d.received_at >= m.portal_enabled_date
)
SELECT strftime('%Y-%m', responded_at) AS month,
       COUNT(*) AS evidence_packages,
       SUM(CASE WHEN response_channel = 'Portal' THEN 1 ELSE 0 END) AS via_portal,
       ROUND(100.0 * SUM(CASE WHEN response_channel = 'Portal' THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS portal_share_pct
FROM eligible
GROUP BY month
ORDER BY month;
```

**How it works:** Only disputes received after a merchant's portal went live are counted. That measures adoption among merchants who could use the portal, rather than being dragged down by merchants who haven't been rolled out yet.

**Expected result:**

| month | evidence_packages | via_portal | portal_share_pct |
|---|---|---|---|
| 2027-01 | 5 | 3 | 60 |
| 2027-02 | 13 | 8 | 61.5 |
| 2027-03 | 27 | 23 | 85.2 |
| 2027-04 | 37 | 29 | 78.4 |
| 2027-05 | 45 | 37 | 82.2 |
| 2027-06 | 22 | 20 | 90.9 |

_6 rows._

**Watch out:** Compare this with the overall share in the earlier pivot lesson. Same data, different denominator, very different story. Always state which population a KPI uses.

### 41. KPI-08 activation by rollout wave

**Business question:** What share of portal-enabled merchants viewed a dispute within 28 days of go-live for them?  
**Concepts:** LEFT JOIN to first activity, date windows

```sql
WITH enabled AS (
  SELECT merchant_id, rollout_wave, portal_enabled_date
  FROM merchants
  WHERE portal_enabled_date IS NOT NULL
),
first_view AS (
  SELECT u.merchant_id, MIN(e.event_at) AS first_viewed_at
  FROM analytics_events e
  JOIN portal_users u ON u.user_id = e.user_id
  WHERE e.event_name = 'dispute_viewed'
  GROUP BY u.merchant_id
)
SELECT en.rollout_wave,
       COUNT(*) AS merchants_enabled,
       SUM(CASE WHEN fv.first_viewed_at IS NOT NULL
                 AND julianday(fv.first_viewed_at) - julianday(en.portal_enabled_date) <= 28
                THEN 1 ELSE 0 END) AS activated_within_28_days,
       ROUND(100.0 * SUM(CASE WHEN fv.first_viewed_at IS NOT NULL
                               AND julianday(fv.first_viewed_at) - julianday(en.portal_enabled_date) <= 28
                              THEN 1 ELSE 0 END) / COUNT(*), 1) AS activation_pct
FROM enabled en
LEFT JOIN first_view fv ON fv.merchant_id = en.merchant_id
GROUP BY en.rollout_wave
ORDER BY en.rollout_wave;
```

**How it works:** The first CTE lists merchants who had the portal. The second finds each merchant's first dispute view. The LEFT JOIN keeps merchants who never viewed anything, and CASE counts only those who activated within 28 days.

**Expected result:**

| rollout_wave | merchants_enabled | activated_within_28_days | activation_pct |
|---|---|---|---|
| Pilot | 3 | 3 | 100 |
| Wave 1 | 11 | 11 | 100 |
| Wave 2 | 5 | 2 | 40 |

_3 rows._

**Watch out:** Merchants enabled less than 28 days before the reporting date haven't had a full window yet. In a real report, exclude them or show them separately.

### 42. KPI-10 evidence funnel

**Business question:** Of users who started an evidence upload, how many submitted within 7 days?  
**Concepts:** Funnel with two event CTEs

```sql
WITH starts AS (
  SELECT user_id, dispute_id, MIN(event_at) AS started_at
  FROM analytics_events
  WHERE event_name = 'evidence_upload_started'
  GROUP BY user_id, dispute_id
),
submits AS (
  SELECT user_id, dispute_id, MIN(event_at) AS submitted_at
  FROM analytics_events
  WHERE event_name = 'evidence_submitted'
  GROUP BY user_id, dispute_id
)
SELECT COUNT(*) AS uploads_started,
       SUM(CASE WHEN s.submitted_at IS NOT NULL
                 AND julianday(s.submitted_at) - julianday(st.started_at) <= 7
                THEN 1 ELSE 0 END) AS submitted_within_7_days,
       ROUND(100.0 * SUM(CASE WHEN s.submitted_at IS NOT NULL
                               AND julianday(s.submitted_at) - julianday(st.started_at) <= 7
                              THEN 1 ELSE 0 END) / COUNT(*), 1) AS completion_pct
FROM starts st
LEFT JOIN submits s
       ON s.user_id = st.user_id
      AND s.dispute_id = st.dispute_id;
```

**How it works:** Each funnel step is reduced to the first time it happened for a user and dispute. Joining the steps on both keys, and checking the time gap, counts completions. The drop-off is where the UX team should look.

**Expected result:**

| uploads_started | submitted_within_7_days | completion_pct |
|---|---|---|
| 150 | 120 | 80 |

_1 row._

**Watch out:** Joining events without first taking MIN per user and dispute multiplies rows when someone starts twice.

### 43. KPI-15 settlement reconciliation

**Business question:** Which settlement rows don't match the finance ledger?  
**Concepts:** Two-key LEFT JOIN, tolerance comparison

```sql
SELECT s.merchant_id,
       s.payout_date,
       s.net_payout,
       l.ledger_amount,
       ROUND(s.net_payout - l.ledger_amount, 2) AS difference,
       CASE
         WHEN l.ledger_amount IS NULL THEN 'Missing in ledger'
         ELSE 'Amount mismatch'
       END AS issue
FROM settlements s
LEFT JOIN ledger l
       ON l.merchant_id = s.merchant_id
      AND l.payout_date = s.payout_date
WHERE l.ledger_amount IS NULL
   OR ABS(s.net_payout - l.ledger_amount) > 0.01
ORDER BY s.payout_date, s.merchant_id;
```

**How it works:** Rows are matched on merchant and payout date. The WHERE clause keeps only problems: settlements with no ledger row and amounts that differ by more than a cent.

**Expected result:**

| merchant_id | payout_date | net_payout | ledger_amount | difference | issue |
|---|---|---|---|---|---|
| M101 | 2027-03-05 | 905,757.56 | 898,491.25 | 7,266.31 | Amount mismatch |
| M117 | 2027-03-05 | 258,632.36 | 259,643.06 | -1,010.7 | Amount mismatch |
| M121 | 2027-03-05 | 166,019.69 | 168,126.35 | -2,106.66 | Amount mismatch |
| M129 | 2027-03-05 | 14,051.18 | 14,107.85 | -56.67 | Amount mismatch |
| M102 | 2027-03-19 | 797,269.19 | 781,246.91 | 16,022.28 | Amount mismatch |
| M118 | 2027-03-19 | 390,797.28 | 402,048.09 | -11,250.81 | Amount mismatch |
| M119 | 2027-03-19 | 383,982.58 | 378,206.5 | 5,776.08 | Amount mismatch |
| M126 | 2027-03-19 | 11,627.34 | 11,594.59 | 32.75 | Amount mismatch |

_Showing 8 of 21 rows._

**Watch out:** Comparing money with = can fail on tiny rounding differences; use a tolerance. An INNER JOIN would hide the missing ledger rows entirely.

### 44. KPI-15 variance percentage

**Business question:** What's the monthly reconciliation variance between reports and the ledger?  
**Concepts:** COALESCE with SUM

```sql
SELECT strftime('%Y-%m', s.payout_date) AS month,
       ROUND(SUM(s.net_payout), 2)                   AS report_total_usd,
       ROUND(SUM(COALESCE(l.ledger_amount, 0)), 2)    AS ledger_total_usd,
       ROUND(100.0 * ABS(SUM(s.net_payout) - SUM(COALESCE(l.ledger_amount, 0)))
             / NULLIF(SUM(COALESCE(l.ledger_amount, 0)), 0), 3) AS variance_pct
FROM settlements s
LEFT JOIN ledger l
       ON l.merchant_id = s.merchant_id
      AND l.payout_date = s.payout_date
GROUP BY month
ORDER BY month;
```

**How it works:** COALESCE treats a missing ledger amount as 0 so the gap shows up in the variance instead of disappearing. The KPI target is 0.5% or less.

**Expected result:**

| month | report_total_usd | ledger_total_usd | variance_pct |
|---|---|---|---|
| 2027-03 | 68,016,328.67 | 67,996,230.79 | 0.03 |
| 2027-04 | 84,392,326.52 | 83,807,615.86 | 0.7 |
| 2027-05 | 51,902,619.95 | 51,887,727.64 | 0.03 |

_3 rows._

**Watch out:** Positive and negative differences cancel out in a monthly total. Pair this with the row-level check in the previous lesson.

### 45. KPI-07 contacts per 100 merchants

**Business question:** How many settlement queries per 100 merchants each month, split by portal status?  
**Concepts:** Calendar CTE, CROSS JOIN, rate per population

```sql
WITH months AS (
  SELECT '2027-01' AS month UNION ALL SELECT '2027-02' UNION ALL SELECT '2027-03'
  UNION ALL SELECT '2027-04' UNION ALL SELECT '2027-05' UNION ALL SELECT '2027-06'
),
merchant_months AS (
  SELECT mo.month,
         m.merchant_id,
         CASE WHEN m.portal_enabled_date IS NOT NULL
               AND m.portal_enabled_date <= mo.month || '-01'
              THEN 'Portal enabled' ELSE 'Not enabled' END AS portal_status
  FROM months mo
  CROSS JOIN merchants m
),
settlement_contacts AS (
  SELECT strftime('%Y-%m', contact_at) AS month, merchant_id, COUNT(*) AS contacts
  FROM servicing_contacts
  WHERE reason = 'Settlement query'
  GROUP BY month, merchant_id
)
SELECT mm.month,
       mm.portal_status,
       COUNT(*) AS merchants,
       COALESCE(SUM(sc.contacts), 0) AS settlement_contacts,
       ROUND(100.0 * COALESCE(SUM(sc.contacts), 0) / COUNT(*), 1) AS per_100_merchants
FROM merchant_months mm
LEFT JOIN settlement_contacts sc
       ON sc.month = mm.month
      AND sc.merchant_id = mm.merchant_id
GROUP BY mm.month, mm.portal_status
ORDER BY mm.month, mm.portal_status;
```

**How it works:** CROSS JOIN builds every merchant-month combination, so merchants with no contacts still count in the denominator. Each merchant-month gets a portal status, then contacts are joined on and turned into a rate per 100 merchants.

**Expected result:**

| month | portal_status | merchants | settlement_contacts | per_100_merchants |
|---|---|---|---|---|
| 2027-01 | Not enabled | 30 | 23 | 76.7 |
| 2027-02 | Not enabled | 27 | 20 | 74.1 |
| 2027-02 | Portal enabled | 3 | 1 | 33.3 |
| 2027-03 | Not enabled | 27 | 23 | 85.2 |
| 2027-03 | Portal enabled | 3 | 0 | 0 |
| 2027-04 | Not enabled | 20 | 14 | 70 |
| 2027-04 | Portal enabled | 10 | 3 | 30 |
| 2027-05 | Not enabled | 16 | 9 | 56.3 |

_Showing 8 of 11 rows._

**Watch out:** Dividing contacts by only the merchants who called would overstate the rate. Rates need the full population.

**Other databases:** Generate months with generate_series in PostgreSQL, or a recursive CTE in SQL Server and MySQL, instead of typing them.


## Level 7: Data quality and testing

### 46. Duplicates with GROUP BY

**Business question:** Which merchant, amount and date combinations appear more than once?  
**Concepts:** GROUP BY ... HAVING COUNT(*) > 1, GROUP_CONCAT

```sql
SELECT merchant_id,
       dispute_amount,
       received_at,
       COUNT(*)                 AS copies,
       GROUP_CONCAT(dispute_id) AS dispute_ids
FROM disputes
GROUP BY merchant_id, dispute_amount, received_at
HAVING COUNT(*) > 1;
```

**How it works:** Grouping by the columns that should be unique together and keeping groups with more than one row is the standard duplicate check. GROUP_CONCAT lists the IDs involved so someone can investigate.

**Expected result:**

| merchant_id | dispute_amount | received_at | copies | dispute_ids |
|---|---|---|---|---|
| M105 | 37.38 | 2027-02-21 | 2 | D0121,D0400 |

_1 row._

**Other databases:** PostgreSQL and SQL Server: STRING_AGG(dispute_id, ','). Oracle and Snowflake: LISTAGG(dispute_id, ',').

### 47. Rule checks in one report

**Business question:** Which disputes break basic data rules?  
**Concepts:** UNION ALL of validation queries

```sql
SELECT 'Recovered more than disputed' AS rule_broken, dispute_id
FROM disputes
WHERE recovered_amount > dispute_amount
UNION ALL
SELECT 'Closed without an outcome', dispute_id
FROM disputes
WHERE closed_at IS NOT NULL AND outcome IS NULL
UNION ALL
SELECT 'Outcome without a closed date', dispute_id
FROM disputes
WHERE outcome IS NOT NULL AND closed_at IS NULL
UNION ALL
SELECT 'Responded after the deadline', dispute_id
FROM disputes
WHERE responded_at > response_due_at
UNION ALL
SELECT 'Unmapped reason code', d.dispute_id
FROM disputes d
LEFT JOIN reason_codes r ON r.reason_code = d.reason_code
WHERE r.reason_code IS NULL
ORDER BY rule_broken, dispute_id;
```

**How it works:** Each SELECT tests one rule from the data dictionary and labels its failures. Stacking them gives one exception report that can run every day. An empty result means every rule passes.

**Expected result:**

| rule_broken | dispute_id |
|---|---|
| Closed without an outcome | D0321 |
| Recovered more than disputed | D0002 |
| Unmapped reason code | D0058 |
| Unmapped reason code | D0213 |

_4 rows._

**Watch out:** Rules written this way become automated data tests in the pipeline, not just one-off checks.

### 48. Orphan records

**Business question:** Are there settlements for merchants that don't exist in the merchant master (R-05)?  
**Concepts:** Anti-join for referential integrity

```sql
SELECT s.settlement_id, s.merchant_id, s.payout_date, s.net_payout
FROM settlements s
LEFT JOIN merchants m ON m.merchant_id = s.merchant_id
WHERE m.merchant_id IS NULL;
```

**How it works:** A child row whose parent doesn't exist is an orphan. These rows would silently disappear from any report that joins settlements to merchants.

**Expected result:**

| settlement_id | merchant_id | payout_date | net_payout |
|---|---|---|---|
| 361 | M999 | 2027-03-26 | 5,080.14 |

_1 row._

**Watch out:** Foreign key constraints prevent orphans at write time, but analytics warehouses often don't enforce them, so these checks matter.

### 49. Status mapping test (DEF-03)

**Business question:** Is any processor status mapped to more than one internal status?  
**Concepts:** COUNT(DISTINCT) in HAVING

```sql
SELECT processor_status,
       COUNT(DISTINCT internal_status)          AS internal_statuses,
       GROUP_CONCAT(DISTINCT internal_status)    AS mapped_to,
       COUNT(*)                                 AS events
FROM status_events
GROUP BY processor_status
HAVING COUNT(DISTINCT internal_status) > 1;
```

**How it works:** Every processor status should map to exactly one internal status. Any processor status that maps to two is a mapping defect, like IN_REVIEW showing as Closed.

**Expected result:**

| processor_status | internal_statuses | mapped_to | events |
|---|---|---|---|
| IN_REVIEW | 2 | Under review,Closed | 141 |

_1 row._

**Watch out:** To see the bad rows themselves, filter status_events for that processor status and the unexpected internal status.

### 50. Test case TC-043

**Business question:** Does every closed dispute have exactly one valid outcome?  
**Concepts:** Reconciling counts as a test

```sql
SELECT COUNT(*) AS closed_disputes,
       SUM(CASE WHEN outcome IN ('Won', 'Partially won', 'Lost', 'Accepted', 'Expired')
                THEN 1 ELSE 0 END) AS with_valid_outcome,
       COUNT(*) - SUM(CASE WHEN outcome IN ('Won', 'Partially won', 'Lost', 'Accepted', 'Expired')
                           THEN 1 ELSE 0 END) AS failures
FROM disputes
WHERE closed_at IS NOT NULL;
```

**How it works:** The test passes when failures is 0. Writing the expected result as a number makes the test easy to automate and to record in the traceability matrix.

**Expected result:**

| closed_disputes | with_valid_outcome | failures |
|---|---|---|
| 292 | 291 | 1 |

_1 row._


## Level 8: Advanced analytics

### 51. Time spent in each status

**Business question:** On average, how many days do disputes spend in each status?  
**Concepts:** LEAD over events

```sql
WITH sequenced AS (
  SELECT dispute_id,
         internal_status,
         processor_event_at,
         LEAD(processor_event_at) OVER (
           PARTITION BY dispute_id
           ORDER BY processor_event_at, event_id
         ) AS next_event_at
  FROM status_events
)
SELECT internal_status,
       COUNT(*) AS transitions,
       ROUND(AVG(julianday(next_event_at) - julianday(processor_event_at)), 1) AS avg_days_in_status
FROM sequenced
WHERE next_event_at IS NOT NULL
GROUP BY internal_status
ORDER BY avg_days_in_status DESC;
```

**How it works:** LEAD finds when the next status began for the same dispute, so the gap is the time spent in the current status. Averaging by status shows where disputes wait longest.

**Expected result:**

| internal_status | transitions | avg_days_in_status |
|---|---|---|
| Under review | 219 | 38.2 |
| Closed | 3 | 29.1 |
| Awaiting evidence | 377 | 13.9 |
| Evidence submitted | 280 | 2 |
| New | 399 | 0 |

_5 rows._

**Watch out:** The final status of each dispute has no next event and is excluded; it's still in that status.

### 52. Monthly cohort retention

**Business question:** Of users who first signed in each month, how many signed in again one and two months later?  
**Concepts:** Cohorts, date arithmetic, COUNT(DISTINCT CASE ...)

```sql
WITH first_month AS (
  SELECT user_id, MIN(strftime('%Y-%m', event_at)) AS cohort_month
  FROM analytics_events
  WHERE event_name = 'sign_in'
  GROUP BY user_id
),
active_months AS (
  SELECT DISTINCT user_id, strftime('%Y-%m', event_at) AS active_month
  FROM analytics_events
  WHERE event_name = 'sign_in'
)
SELECT f.cohort_month,
       COUNT(DISTINCT f.user_id) AS users,
       COUNT(DISTINCT CASE WHEN a.active_month = strftime('%Y-%m', date(f.cohort_month || '-01', '+1 month'))
                           THEN a.user_id END) AS active_month_1,
       COUNT(DISTINCT CASE WHEN a.active_month = strftime('%Y-%m', date(f.cohort_month || '-01', '+2 months'))
                           THEN a.user_id END) AS active_month_2
FROM first_month f
LEFT JOIN active_months a ON a.user_id = f.user_id
GROUP BY f.cohort_month
ORDER BY f.cohort_month;
```

**How it works:** Users are grouped by the month they first signed in. For each later month offset, COUNT(DISTINCT CASE ...) counts users from that cohort who were active. Reading across a row shows how well that cohort stuck with the portal.

**Expected result:**

| cohort_month | users | active_month_1 | active_month_2 |
|---|---|---|---|
| 2027-01 | 9 | 9 | 9 |
| 2027-03 | 9 | 9 | 9 |
| 2027-04 | 17 | 17 | 14 |
| 2027-05 | 2 | 2 | 0 |
| 2027-06 | 7 | 0 | 0 |

_5 rows._

**Watch out:** Recent cohorts haven't reached later months yet, so their zeros are 'not yet', not 'churned'.

**Other databases:** PostgreSQL: DATE_TRUNC('month', event_at) + INTERVAL '1 month'. SQL Server: DATEADD(month, 1, ...). MySQL: DATE_ADD(..., INTERVAL 1 MONTH).

### 53. Reusable view

**Business question:** Create a view of closed disputes with merchant details, then use it.  
**Concepts:** CREATE VIEW

```sql
CREATE VIEW IF NOT EXISTS v_closed_disputes AS
SELECT d.dispute_id, d.outcome, d.dispute_amount, d.recovered_amount,
       d.closed_at, d.response_channel, m.segment, m.rollout_wave
FROM disputes d
JOIN merchants m ON m.merchant_id = d.merchant_id
WHERE d.outcome IS NOT NULL;

SELECT rollout_wave, outcome, COUNT(*) AS disputes
FROM v_closed_disputes
GROUP BY rollout_wave, outcome
ORDER BY rollout_wave, disputes DESC;
```

**How it works:** A view saves a query under a name so the same definition of 'closed dispute' is reused by every report. It stores the query, not a copy of the data, so results stay current.

**Expected result:**

| rollout_wave | outcome | disputes |
|---|---|---|
| General availability | Lost | 4 |
| General availability | Expired | 2 |
| General availability | Accepted | 1 |
| Later phase | Lost | 7 |
| Later phase | Won | 5 |
| Later phase | Partially won | 1 |
| Later phase | Expired | 1 |
| Later phase | Accepted | 1 |

_Showing 8 of 23 rows._

**Watch out:** If KPI logic lives in many copy-pasted queries, definitions drift. Views (or dbt models) keep one agreed definition, which is exactly what CR-05 is about.

**Other databases:** Most databases use CREATE OR REPLACE VIEW. SQL Server uses CREATE OR ALTER VIEW.

### 54. Indexes and query plans

**Business question:** How can a slow filter on merchant and received date be sped up?  
**Concepts:** CREATE INDEX, EXPLAIN QUERY PLAN

```sql
CREATE INDEX IF NOT EXISTS idx_disputes_merchant_received
  ON disputes (merchant_id, received_at);

EXPLAIN QUERY PLAN
SELECT dispute_id, dispute_amount
FROM disputes
WHERE merchant_id = 'M101'
  AND received_at >= '2027-03-01';
```

**How it works:** An index is a sorted lookup structure. With merchant_id first and received_at second, the database can jump straight to one merchant's rows in date order instead of scanning the table. EXPLAIN shows whether the index is used.

**Expected result:**

| id | parent | notused | detail |
|---|---|---|---|
| 3 | 0 | 0 | SEARCH disputes USING INDEX idx_disputes_merchant_received (merchant_id=? AND received_at>?) |

_1 row._

**Watch out:** Indexes speed up reads but slow down writes and take space. Index columns you filter and join on most, with the most selective equality column first.

**Other databases:** PostgreSQL: EXPLAIN ANALYZE. MySQL: EXPLAIN. SQL Server: the actual execution plan. Cloud warehouses such as Snowflake and BigQuery use clustering and partitions instead of traditional indexes.


## Practice exercises

Write each query yourself before checking the answer key. Your column names and row order can differ; what matters is that the values match. In the HTML lab, Check answer compares your result with the answer automatically.


**Level 1: Basics**

- **E01.** List every Travel & hospitality merchant with its rollout wave, in alphabetical order by name.  
  _Hint: Filter merchants on segment and sort by merchant_name._

- **E02.** Find disputes over $1,000 that are still open (no closed date). Show ID, merchant, amount and status.  
  _Hint: Two conditions: an amount comparison and IS NULL._

- **E03.** Show Amex disputes received in April 2027, newest first.  
  _Hint: Use >= '2027-04-01' and < '2027-05-01'._


**Level 2: Aggregation**

- **E04.** Count disputes by card network, most disputes first.  
  _Hint: GROUP BY card_network with COUNT(*)._

- **E05.** Show the average dispute amount per reason code (2 decimals), only for codes with at least 20 disputes.  
  _Hint: The 'at least 20' condition is on a count, so it goes in HAVING._

- **E06.** For each redaction status, show the number of evidence files and total size in MB (1 decimal).  
  _Hint: Divide the KB sum by 1024.0._


**Level 3: Joins and set operations**

- **E07.** List each analyst's name and number of resolved work items, including analysts with none.  
  _Hint: LEFT JOIN ops_work_items and put the resolved condition in the ON clause._

- **E08.** For disputes currently 'Under review', show dispute ID, merchant name and reason category.  
  _Hint: Join three tables: disputes, merchants and reason_codes._

- **E09.** Which portal-enabled merchants have no user who has logged in yet?  
  _Hint: Use NOT EXISTS (or a LEFT JOIN) against portal_users where first_login_at IS NOT NULL._


**Level 4: Subqueries and CTEs**

- **E10.** Which merchants have a total disputed amount above the average merchant total? Show merchant ID and total (2 decimals).  
  _Hint: Build merchant totals in a CTE, then compare each to (SELECT AVG(total) FROM totals)._

- **E11.** Calculate the proposed win rate (Won ÷ Won, Partially won and Lost) by merchant segment.  
  _Hint: Join merchants, then use conditional aggregation with NULLIF._

- **E12.** Find disputes that have no status events at all.  
  _Hint: NOT EXISTS against status_events._


**Level 5: Window functions**

- **E13.** Show each merchant's single largest dispute (merchant ID, dispute ID, amount).  
  _Hint: ROW_NUMBER() partitioned by merchant, ordered by amount descending; keep rn = 1._

- **E14.** Rank reason codes by number of expired disputes using DENSE_RANK. Show code, expired count and rank.  
  _Hint: Filter outcome = 'Expired', group by reason code, then DENSE_RANK over the count._

- **E15.** Show the cumulative recovered amount by month closed (2 decimals).  
  _Hint: Sum recovered_amount per month in a CTE, then a running SUM() OVER (ORDER BY month)._

- **E16.** For merchant M101, show each dispute's received date and the number of days since that merchant's previous dispute.  
  _Hint: LAG(received_at) OVER (ORDER BY received_at, dispute_id), then julianday difference._


**Level 6: KPI queries**

- **E17.** Calculate the on-time response rate by response channel for disputes due on or before 2027-06-15. Treat disputes with no response as their own group.  
  _Hint: COALESCE(response_channel, 'No response') for the grouping column._

- **E18.** Calculate the missed-deadline loss rate by rollout wave.  
  _Hint: Expired ÷ all closed disputes, joined to merchants for rollout_wave._

- **E19.** Show the average number of days from received to closed for each outcome (1 decimal).  
  _Hint: Filter closed_at IS NOT NULL and outcome IS NOT NULL; average the julianday difference._

- **E20.** Calculate the 95th percentile status sync latency in minutes for each month of processor_event_at (2 decimals).  
  _Hint: Same nearest-rank method as the lesson, but partition ROW_NUMBER and COUNT by month, then take MIN per month._


**Level 7: Data quality and testing**

- **E21.** Count status events with sync latency over 10 minutes, by processor status.  
  _Hint: Latency in minutes > 10, then GROUP BY processor_status._

- **E22.** Find ledger rows that have no matching settlement row.  
  _Hint: Anti-join from ledger to settlements on merchant and payout date. An empty result means the check passes._


**Level 8: Advanced analytics**

- **E23.** For each portal-enabled merchant, show the first sign-in time and the first evidence submission time, and the days between them.  
  _Hint: Two CTEs with MIN(event_at) per merchant (join analytics_events to portal_users), then LEFT JOIN them._

- **E24.** For portal-enabled merchants, compare the share of servicing contacts that are settlement queries before and after their portal enablement date.  
  _Hint: CASE on contact_at >= portal_enabled_date to label 'Before' or 'After', then conditional aggregation._


## Answer key

### E01
List every Travel & hospitality merchant with its rollout wave, in alphabetical order by name.

```sql
SELECT merchant_name, rollout_wave
FROM merchants
WHERE segment = 'Travel & hospitality'
ORDER BY merchant_name;
```

**Expected result:**

| merchant_name | rollout_wave |
|---|---|
| Coastal Air Tours | Wave 2 |
| Skyline Stays | Wave 2 |
| TrailPass Travel | Wave 2 |
| Wander Hotels | Wave 2 |

_4 rows._

### E02
Find disputes over $1,000 that are still open (no closed date). Show ID, merchant, amount and status.

```sql
SELECT dispute_id, merchant_id, dispute_amount, internal_status
FROM disputes
WHERE dispute_amount > 1000
  AND closed_at IS NULL;
```

**Expected result:**

| dispute_id | merchant_id | dispute_amount | internal_status |
|---|---|---|---|
| D0342 | M103 | 1,121.13 | Under review |

_1 row._

### E03
Show Amex disputes received in April 2027, newest first.

```sql
SELECT dispute_id, merchant_id, dispute_amount, received_at
FROM disputes
WHERE card_network = 'Amex'
  AND received_at >= '2027-04-01'
  AND received_at <  '2027-05-01'
ORDER BY received_at DESC;
```

**Expected result:**

| dispute_id | merchant_id | dispute_amount | received_at |
|---|---|---|---|
| D0294 | M106 | 151.94 | 2027-04-30 |
| D0279 | M105 | 79.71 | 2027-04-26 |
| D0282 | M119 | 79.27 | 2027-04-26 |
| D0276 | M105 | 44.83 | 2027-04-24 |
| D0265 | M111 | 105.54 | 2027-04-18 |
| D0249 | M105 | 34.54 | 2027-04-15 |

_Showing 6 of 11 rows._

### E04
Count disputes by card network, most disputes first.

```sql
SELECT card_network, COUNT(*) AS disputes
FROM disputes
GROUP BY card_network
ORDER BY disputes DESC;
```

**Expected result:**

| card_network | disputes |
|---|---|
| Visa | 163 |
| Mastercard | 143 |
| Amex | 66 |
| Discover | 28 |

_4 rows._

### E05
Show the average dispute amount per reason code (2 decimals), only for codes with at least 20 disputes.

```sql
SELECT reason_code, COUNT(*) AS disputes, ROUND(AVG(dispute_amount), 2) AS avg_amount
FROM disputes
GROUP BY reason_code
HAVING COUNT(*) >= 20;
```

**Expected result:**

| reason_code | disputes | avg_amount |
|---|---|---|
| AU-07 | 42 | 130.78 |
| CR-04 | 80 | 151.54 |
| DP-05 | 56 | 133.85 |
| FR-01 | 70 | 124.04 |
| NA-03 | 61 | 138.15 |
| NR-02 | 64 | 133.63 |

_6 rows._

### E06
For each redaction status, show the number of evidence files and total size in MB (1 decimal).

```sql
SELECT redaction_status, COUNT(*) AS files, ROUND(SUM(file_size_kb) / 1024.0, 1) AS total_mb
FROM evidence_files
GROUP BY redaction_status;
```

**Expected result:**

| redaction_status | files | total_mb |
|---|---|---|
| Clean | 195 | 944 |
| Quarantined | 11 | 57 |
| Redacted | 34 | 149.2 |

_3 rows._

### E07
List each analyst's name and number of resolved work items, including analysts with none.

```sql
SELECT a.analyst_name, COUNT(w.work_item_id) AS resolved_items
FROM analysts a
LEFT JOIN ops_work_items w
       ON w.analyst_id = a.analyst_id
      AND w.resolved_at IS NOT NULL
GROUP BY a.analyst_id, a.analyst_name;
```

**Expected result:**

| analyst_name | resolved_items |
|---|---|
| Priya Nair | 41 |
| Marcus Lee | 40 |
| Sofia Gomez | 40 |
| Daniel Kim | 37 |
| Aisha Khan | 36 |
| Tom Walsh | 51 |

_6 rows._

### E08
For disputes currently 'Under review', show dispute ID, merchant name and reason category.

```sql
SELECT d.dispute_id, m.merchant_name, r.category
FROM disputes d
JOIN merchants m ON m.merchant_id = d.merchant_id
JOIN reason_codes r ON r.reason_code = d.reason_code
WHERE d.internal_status = 'Under review';
```

**Expected result:**

| dispute_id | merchant_name | category |
|---|---|---|
| D0231 | MarketHub | Fraud |
| D0239 | CraftBazaar | Consumer dispute |
| D0241 | Atlas Sportswear | Consumer dispute |
| D0244 | Pebble Footwear | Consumer dispute |
| D0245 | Riverstone Pets | Consumer dispute |
| D0253 | CraftBazaar | Consumer dispute |

_Showing 6 of 58 rows._

### E09
Which portal-enabled merchants have no user who has logged in yet?

```sql
SELECT m.merchant_id, m.merchant_name
FROM merchants m
WHERE m.portal_enabled_date IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM portal_users u
    WHERE u.merchant_id = m.merchant_id
      AND u.first_login_at IS NOT NULL
  );
```

**Expected result:**

| merchant_id | merchant_name |
|---|---|
| M119 | SoundSphere |

_1 row._

### E10
Which merchants have a total disputed amount above the average merchant total? Show merchant ID and total (2 decimals).

```sql
WITH totals AS (
  SELECT merchant_id, SUM(dispute_amount) AS total
  FROM disputes
  GROUP BY merchant_id
)
SELECT merchant_id, ROUND(total, 2) AS total_usd
FROM totals
WHERE total > (SELECT AVG(total) FROM totals);
```

**Expected result:**

| merchant_id | total_usd |
|---|---|
| M101 | 3,780.82 |
| M102 | 4,080.88 |
| M103 | 3,700.27 |
| M104 | 4,308.81 |
| M105 | 5,773.69 |
| M106 | 4,213.08 |

_Showing 6 of 11 rows._

### E11
Calculate the proposed win rate (Won ÷ Won, Partially won and Lost) by merchant segment.

```sql
SELECT m.segment,
       ROUND(100.0 * SUM(CASE WHEN d.outcome = 'Won' THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN d.outcome IN ('Won', 'Partially won', 'Lost') THEN 1 ELSE 0 END), 0), 1) AS win_rate_pct
FROM disputes d
JOIN merchants m ON m.merchant_id = d.merchant_id
GROUP BY m.segment;
```

**Expected result:**

| segment | win_rate_pct |
|---|---|
| Enterprise e-commerce | 36.7 |
| Marketplaces & platforms | 38.5 |
| Mid-market online retail | 40.6 |
| Small card-present | 0 |
| Subscription & digital services | 63.2 |
| Travel & hospitality | 20 |

_6 rows._

### E12
Find disputes that have no status events at all.

```sql
SELECT d.dispute_id, d.merchant_id, d.received_at
FROM disputes d
WHERE NOT EXISTS (
  SELECT 1 FROM status_events e WHERE e.dispute_id = d.dispute_id
);
```

**Expected result:**

| dispute_id | merchant_id | received_at |
|---|---|---|
| D0400 | M105 | 2027-02-21 |

_1 row._

### E13
Show each merchant's single largest dispute (merchant ID, dispute ID, amount).

```sql
WITH ranked AS (
  SELECT merchant_id, dispute_id, dispute_amount,
         ROW_NUMBER() OVER (PARTITION BY merchant_id ORDER BY dispute_amount DESC) AS rn
  FROM disputes
)
SELECT merchant_id, dispute_id, dispute_amount
FROM ranked
WHERE rn = 1;
```

**Expected result:**

| merchant_id | dispute_id | dispute_amount |
|---|---|---|
| M101 | D0106 | 341.07 |
| M102 | D0200 | 447.78 |
| M103 | D0342 | 1,121.13 |
| M104 | D0222 | 467.2 |
| M105 | D0300 | 784.49 |
| M106 | D0062 | 1,101.35 |

_Showing 6 of 30 rows._

### E14
Rank reason codes by number of expired disputes using DENSE_RANK. Show code, expired count and rank.

```sql
SELECT reason_code,
       COUNT(*) AS expired,
       DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS expired_rank
FROM disputes
WHERE outcome = 'Expired'
GROUP BY reason_code;
```

**Expected result:**

| reason_code | expired | expired_rank |
|---|---|---|
| FR-01 | 6 | 1 |
| NR-02 | 5 | 2 |
| DP-05 | 5 | 2 |
| CR-04 | 5 | 2 |
| NA-03 | 4 | 3 |
| LP-08 | 3 | 4 |

_Showing 6 of 8 rows._

### E15
Show the cumulative recovered amount by month closed (2 decimals).

```sql
WITH monthly AS (
  SELECT strftime('%Y-%m', closed_at) AS month, SUM(recovered_amount) AS recovered
  FROM disputes
  WHERE closed_at IS NOT NULL
  GROUP BY month
)
SELECT month,
       ROUND(recovered, 2) AS recovered_usd,
       ROUND(SUM(recovered) OVER (ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_usd
FROM monthly;
```

**Expected result:**

| month | recovered_usd | cumulative_usd |
|---|---|---|
| 2027-01 | 0 | 0 |
| 2027-02 | 44.33 | 44.33 |
| 2027-03 | 2,083.4 | 2,127.73 |
| 2027-04 | 4,019.48 | 6,147.21 |
| 2027-05 | 2,033 | 8,180.21 |
| 2027-06 | 2,852 | 11,032.21 |

_6 rows._

### E16
For merchant M101, show each dispute's received date and the number of days since that merchant's previous dispute.

```sql
SELECT dispute_id,
       received_at,
       julianday(received_at) - julianday(LAG(received_at) OVER (ORDER BY received_at, dispute_id)) AS days_since_previous
FROM disputes
WHERE merchant_id = 'M101';
```

**Expected result:**

| dispute_id | received_at | days_since_previous |
|---|---|---|
| D0003 | 2027-01-08 | NULL |
| D0036 | 2027-01-22 | 14 |
| D0052 | 2027-01-27 | 5 |
| D0058 | 2027-01-29 | 2 |
| D0071 | 2027-02-01 | 3 |
| D0079 | 2027-02-05 | 4 |

_Showing 6 of 36 rows._

### E17
Calculate the on-time response rate by response channel for disputes due on or before 2027-06-15. Treat disputes with no response as their own group.

```sql
SELECT COALESCE(response_channel, 'No response') AS channel,
       COUNT(*) AS disputes_due,
       ROUND(100.0 * SUM(CASE WHEN responded_at IS NOT NULL AND responded_at <= response_due_at THEN 1 ELSE 0 END)
             / COUNT(*), 1) AS on_time_pct
FROM disputes
WHERE response_due_at <= '2027-06-15'
GROUP BY COALESCE(response_channel, 'No response');
```

**Expected result:**

| channel | disputes_due | on_time_pct |
|---|---|---|
| Email | 201 | 100 |
| No response | 32 | 0 |
| Portal | 118 | 100 |

_3 rows._

### E18
Calculate the missed-deadline loss rate by rollout wave.

```sql
SELECT m.rollout_wave,
       COUNT(*) AS closed_disputes,
       ROUND(100.0 * SUM(CASE WHEN d.outcome = 'Expired' THEN 1 ELSE 0 END) / COUNT(*), 1) AS missed_deadline_pct
FROM disputes d
JOIN merchants m ON m.merchant_id = d.merchant_id
WHERE d.outcome IS NOT NULL
GROUP BY m.rollout_wave;
```

**Expected result:**

| rollout_wave | closed_disputes | missed_deadline_pct |
|---|---|---|
| General availability | 7 | 28.6 |
| Later phase | 15 | 6.7 |
| Pilot | 77 | 3.9 |
| Wave 1 | 134 | 10.4 |
| Wave 2 | 58 | 20.7 |

_5 rows._

### E19
Show the average number of days from received to closed for each outcome (1 decimal).

```sql
SELECT outcome,
       COUNT(*) AS disputes,
       ROUND(AVG(julianday(closed_at) - julianday(received_at)), 1) AS avg_days_to_close
FROM disputes
WHERE closed_at IS NOT NULL AND outcome IS NOT NULL
GROUP BY outcome;
```

**Expected result:**

| outcome | disputes | avg_days_to_close |
|---|---|---|
| Accepted | 37 | 3.7 |
| Expired | 32 | 26 |
| Lost | 114 | 54.2 |
| Partially won | 24 | 50.1 |
| Won | 84 | 54.1 |

_5 rows._

### E20
Calculate the 95th percentile status sync latency in minutes for each month of processor_event_at (2 decimals).

```sql
WITH latency AS (
  SELECT strftime('%Y-%m', processor_event_at) AS month,
         (julianday(hub_updated_at) - julianday(processor_event_at)) * 24 * 60 AS minutes
  FROM status_events
),
ranked AS (
  SELECT month, minutes,
         ROW_NUMBER() OVER (PARTITION BY month ORDER BY minutes) AS rn,
         COUNT(*) OVER (PARTITION BY month) AS n
  FROM latency
)
SELECT month, ROUND(MIN(minutes), 2) AS p95_minutes
FROM ranked
WHERE rn >= 0.95 * n
GROUP BY month;
```

**Expected result:**

| month | p95_minutes |
|---|---|
| 2027-01 | 10.95 |
| 2027-02 | 4 |
| 2027-03 | 14.1 |
| 2027-04 | 11.55 |
| 2027-05 | 4 |
| 2027-06 | 13.8 |

_6 rows._

### E21
Count status events with sync latency over 10 minutes, by processor status.

```sql
SELECT processor_status, COUNT(*) AS slow_events
FROM status_events
WHERE (julianday(hub_updated_at) - julianday(processor_event_at)) * 24 * 60 > 10
GROUP BY processor_status;
```

**Expected result:**

| processor_status | slow_events |
|---|---|
| ACCEPTED | 7 |
| EVIDENCE_REQUIRED | 20 |
| EXPIRED | 2 |
| IN_REVIEW | 11 |
| LOST | 8 |
| NEW | 15 |

_Showing 6 of 10 rows._

### E22
Find ledger rows that have no matching settlement row.

```sql
SELECT l.ledger_id, l.merchant_id, l.payout_date, l.ledger_amount
FROM ledger l
LEFT JOIN settlements s
       ON s.merchant_id = l.merchant_id
      AND s.payout_date = l.payout_date
WHERE s.settlement_id IS NULL;
```

**Expected result:**

_No rows returned._

### E23
For each portal-enabled merchant, show the first sign-in time and the first evidence submission time, and the days between them.

```sql
WITH first_sign_in AS (
  SELECT u.merchant_id, MIN(e.event_at) AS first_sign_in
  FROM analytics_events e
  JOIN portal_users u ON u.user_id = e.user_id
  WHERE e.event_name = 'sign_in'
  GROUP BY u.merchant_id
),
first_submit AS (
  SELECT u.merchant_id, MIN(e.event_at) AS first_submission
  FROM analytics_events e
  JOIN portal_users u ON u.user_id = e.user_id
  WHERE e.event_name = 'evidence_submitted'
  GROUP BY u.merchant_id
)
SELECT si.merchant_id,
       si.first_sign_in,
       fs.first_submission,
       ROUND(julianday(fs.first_submission) - julianday(si.first_sign_in), 1) AS days_between
FROM first_sign_in si
LEFT JOIN first_submit fs ON fs.merchant_id = si.merchant_id;
```

**Expected result:**

| merchant_id | first_sign_in | first_submission | days_between |
|---|---|---|---|
| M101 | 2027-01-11 09:00:46 | 2027-02-08 17:16:42 | 28.3 |
| M102 | 2027-01-17 17:38:07 | 2027-01-28 16:49:52 | 11 |
| M103 | 2027-01-17 13:42:57 | 2027-01-19 18:32:12 | 2.2 |
| M104 | 2027-03-24 14:35:34 | 2027-04-11 09:21:02 | 17.8 |
| M105 | 2027-03-29 15:02:18 | 2027-03-30 18:22:24 | 1.1 |
| M106 | 2027-03-29 10:57:27 | 2027-04-08 10:06:27 | 10 |

_Showing 6 of 18 rows._

### E24
For portal-enabled merchants, compare the share of servicing contacts that are settlement queries before and after their portal enablement date.

```sql
SELECT CASE WHEN c.contact_at >= m.portal_enabled_date THEN 'After enablement' ELSE 'Before enablement' END AS period,
       COUNT(*) AS contacts,
       ROUND(100.0 * SUM(CASE WHEN c.reason = 'Settlement query' THEN 1 ELSE 0 END) / COUNT(*), 1) AS settlement_query_pct
FROM servicing_contacts c
JOIN merchants m ON m.merchant_id = c.merchant_id
WHERE m.portal_enabled_date IS NOT NULL
GROUP BY period;
```

**Expected result:**

| period | contacts | settlement_query_pct |
|---|---|---|
| After enablement | 61 | 27.9 |
| Before enablement | 87 | 57.5 |

_2 rows._


## Appendix: deliberate data problems

These are planted so the Level 7 queries have something to find. Each one mirrors an item in the project workbooks.

| Problem | How many | Related project item |
|---|---|---|

| Recovered amount higher than disputed amount | one dispute | Data dictionary quality rule |

| Closed dispute with no outcome | one dispute | TC-043 |

| Duplicate dispute (same merchant, amount and date) | one pair | Duplicate check |

| Unmapped reason code ZZ-99 | two disputes | I-02 |

| Processor status IN_REVIEW mapped to Closed | three events | DEF-03 |

| Settlement row for merchant M999 not in the merchant master | one row | R-05 |

| Settlement rows missing from the ledger or with amount mismatches | a few rows | KPI-15 |


## Interview tips

Say the business question back before writing SQL, and name the denominator out loud; most KPI mistakes are denominator mistakes. Build complex queries in CTE steps and check each step's row count. Mention NULL handling, join fan-out and ties in rankings before the interviewer asks. When the result looks surprising, check the data before trusting the number, as Level 7 shows.
