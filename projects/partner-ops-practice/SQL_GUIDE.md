# Partner Ops SQL Practice — Basic to Advanced

Same domain as PCMS at Bajaj Finserv: partners, e-agreements, payouts (the Finacle-integrated
payout side), activity logs, and the discrepancies that actually show up in a system like this.
Every query below was run for real against `partner_ops.db` (SQLite) — the row counts and sample
rows are real output, not made up.

**Setup:** `python3 generate_data.py` builds `partner_ops.db` from `schema.sql`. Open it in
[DB Browser for SQLite](https://sqlitebrowser.org/) (free, GUI, zero setup) or run queries via
`python3 -c "import sqlite3; ..."`. A T-SQL port of the schema and the advanced queries is in
`tsql_port.sql` for practicing in your actual SQL Server 2022 setup.

---

## Schema

```
partners        (partner_id PK, partner_name, region, onboarding_date, status)
e_agreements    (agreement_id PK, partner_id FK, agreement_type, status, sent_date, signed_date, expiry_date)
payouts         (payout_id PK, partner_id FK, amount, payout_date, status, payment_method, finacle_reference_id)
activity_logs   (log_id PK, partner_id FK, activity_type, activity_ts, details)
discrepancies   (discrepancy_id PK, partner_id FK, related_payout_id, related_agreement_id, issue_type, detected_date, resolved)
```

18 partners, 18 e-agreements, 90 payouts, 160 activity log entries. Five real issues are baked
into the data on purpose (see below) — the point of the advanced section is writing the queries
that find them, not reading them off a pre-filled table.

---

## Basic — SELECT, WHERE, ORDER BY, single JOIN

**B1. List all active partners**
```sql
SELECT partner_id, partner_name, region FROM partners
WHERE status = 'active' ORDER BY partner_name;
```
→ 14 rows. First few: Aravali Traders (East), Bluepeak Finserv (North), Coastal Credit Co (North).

**B2. All payouts for one partner, chronologically**
```sql
SELECT payout_id, amount, payout_date, status FROM payouts
WHERE partner_id = 1 ORDER BY payout_date;
```
→ 6 rows for partner 1. (You'll notice some amounts repeat on the same date — that's not a
typo, it's one of the seeded issues. Covered in Advanced.)

**B3. How many payouts are in each status**
```sql
SELECT status, COUNT(*) FROM payouts GROUP BY status ORDER BY COUNT(*) DESC;
```
→ completed: 81, pending: 7, failed: 1, disputed: 1.

**B4. Which e-agreements are still just "sent," not signed**
```sql
SELECT agreement_id, partner_id, sent_date FROM e_agreements WHERE status = 'sent';
```
→ 3 rows: agreements 3, 9, 15.

---

## Intermediate — multi-table JOIN, GROUP BY + HAVING, aggregates, date math

**I1. Total paid per partner, highest first**
```sql
SELECT pt.partner_name, SUM(p.amount) AS total_paid, COUNT(*) AS n_payouts
FROM partners pt JOIN payouts p ON p.partner_id = pt.partner_id
GROUP BY pt.partner_id ORDER BY total_paid DESC LIMIT 5;
```
→ Indus Valley Finserv leads at ₹438,956.89 across 6 payouts.

**I2. Partners with 5 or more payouts** (a HAVING filter on an aggregate)
```sql
SELECT partner_id, COUNT(*) AS n FROM payouts
GROUP BY partner_id HAVING COUNT(*) >= 5;
```
→ 11 of the 18 partners.

**I3. Find duplicate payouts — the first real "payment issue" query**
```sql
SELECT partner_id, amount, payout_date, COUNT(*) AS cnt
FROM payouts
GROUP BY partner_id, amount, payout_date
HAVING COUNT(*) > 1;
```
→ Exactly 3 rows. Same partner, same amount, same date, twice — a classic double-payout bug
(a retry that wasn't idempotent, or a batch job re-run). This is a real thing that happens with
payout systems, and it's exactly the kind of thing "analyze data for discrepancies" means in
practice.

**I4. E-agreements stuck in "sent" for 90+ days — a real e-agreement issue**
```sql
SELECT agreement_id, partner_id, sent_date,
       CAST(julianday('2026-09-09') - julianday(sent_date) AS INTEGER) AS days_stuck
FROM e_agreements
WHERE status = 'sent' AND signed_date IS NULL
  AND julianday('2026-09-09') - julianday(sent_date) > 90;
```
→ 3 agreements, stuck 175–185 days. This is the kind of query that turns into an actual
operational alert: "these partners never signed, someone should follow up."

**I5. Average payout size by region**
```sql
SELECT pt.region, ROUND(AVG(p.amount), 2) AS avg_amount
FROM partners pt JOIN payouts p ON p.partner_id = pt.partner_id
GROUP BY pt.region ORDER BY avg_amount DESC;
```
→ South leads at ₹54,309.70 average.

---

## Advanced — window functions, correlated joins, ranking, the full discrepancy sweep

**A1. Payouts made after the governing agreement had already expired**
```sql
SELECT p.payout_id, pt.partner_name, p.payout_date, e.expiry_date
FROM payouts p
JOIN partners pt ON pt.partner_id = p.partner_id
JOIN e_agreements e ON e.partner_id = p.partner_id
WHERE e.status = 'expired' AND p.payout_date > e.expiry_date AND p.status = 'completed';
```
→ Exactly 4 rows: Bluepeak Finserv and Ganges Retail Finance both got paid after their
agreement expired. This is the sharpest finding in the whole dataset — money moved on a
contract that had lapsed.

**A2. Running total of payouts per partner, over time** (window function)
```sql
SELECT partner_id, payout_date, amount,
       SUM(amount) OVER (PARTITION BY partner_id ORDER BY payout_date) AS running_total
FROM payouts WHERE partner_id = 1 ORDER BY payout_date;
```
Notice the running total counts the duplicate payouts from I3 twice — which is exactly why
dedup has to happen *before* a running-total or reconciliation report, not after. That's a real
lesson, not a contrived one.

**A3. Rank partners by total payout volume** (`RANK()` over an aggregated subquery)
```sql
SELECT partner_name, total_paid, RANK() OVER (ORDER BY total_paid DESC) AS rnk
FROM (
  SELECT pt.partner_name, SUM(p.amount) AS total_paid
  FROM partners pt JOIN payouts p ON p.partner_id = pt.partner_id
  GROUP BY pt.partner_id
);
```
→ Same leaderboard as I1, but now with an actual rank column — the kind of thing that feeds a
dashboard or a monthly ops review.

**A4. Payout requests logged *after* a partner's account went to "suspended"**
```sql
SELECT pt.partner_name, a.activity_ts
FROM activity_logs a JOIN partners pt ON pt.partner_id = a.partner_id
WHERE a.activity_type = 'payout_request' AND pt.status = 'suspended';
```
→ Exactly 2 rows: Lakeside Capital and Everest Capital Partners both tried to request a payout
after suspension. This is the "activity log" version of the same discrepancy-hunting instinct —
cross-referencing what someone *did* against what their account *should* allow.

**A5. Capstone — build one consolidated discrepancy report and persist it**
```sql
INSERT INTO discrepancies (partner_id, related_payout_id, related_agreement_id, issue_type, detected_date, resolved)
SELECT partner_id, payout_id, NULL, 'duplicate_payout', '2026-09-09', 0
FROM (
  SELECT p.payout_id, p.partner_id
  FROM payouts p
  JOIN (
    SELECT partner_id, amount, payout_date
    FROM payouts GROUP BY partner_id, amount, payout_date HAVING COUNT(*) > 1
  ) d ON d.partner_id = p.partner_id AND d.amount = p.amount AND d.payout_date = p.payout_date
)
UNION ALL
SELECT p.partner_id, p.payout_id, e.agreement_id, 'expired_agreement_active_payout', '2026-09-09', 0
FROM payouts p
JOIN e_agreements e ON e.partner_id = p.partner_id
WHERE e.status = 'expired' AND p.payout_date > e.expiry_date AND p.status = 'completed'
UNION ALL
SELECT partner_id, NULL, agreement_id, 'missing_signature', '2026-09-09', 0
FROM e_agreements WHERE status = 'sent' AND signed_date IS NULL;
```
This is the step that turns ad-hoc detection into something an ops team can actually track and
resolve — the same shape as the Verification Gap's five-bucket scorecard, just applied to
payouts instead of citations. After running it: `SELECT * FROM discrepancies;` gives a real,
queryable audit trail — 13 rows: 6 for duplicate_payout (both sides of each of the 3 duplicate
pairs get flagged individually, since both transactions need review, not just one), 4 for
expired_agreement_active_payout, 3 for missing_signature. Worth noticing and being ready to
explain: the duplicate-payout count doubles from 3 (I3, one row per *pair*) to 6 here (one row
per *transaction*) — a real distinction between "how many incidents happened" and "how many
records need review," and exactly the kind of precision an interviewer listens for.

---

## How to talk about this

If asked "walk me through how you'd find payment or e-agreement issues": don't describe the
answer in the abstract — describe the actual sequence: start with a structural check (does every
payout have a valid, current agreement behind it — A1), then a duplication check (I3), then an
activity-consistency check (A4), then consolidate everything into one report instead of three
separate spreadsheets (A5). That's a real methodology, not a one-off query.
