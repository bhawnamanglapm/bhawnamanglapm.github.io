# 24 Fintech API Case Studies — Reference Guide

Companion to the hands-on NSDL KYC Verification project you built and tested in Postman.
Same format throughout: what it does, a realistic endpoint, sample request/response, and the
test scenarios that actually matter — so you can talk through any of these in the interview the
same way you can already talk through KYC, even without having clicked "Send" on it yourself.

**How to use this:** you don't need to memorize the JSON. What matters is the *shape of the
answer* for each one — what it's for, what could go wrong, and what a good test suite checks.
That pattern is identical across all 24; only the specifics change.

---

## 1. Identity & KYC

### 1.1 NSDL PAN Verification
*(You already built and tested this one — included here for completeness.)*
**What it does:** Confirms a PAN number is genuine and matches the name/DOB given.
**Endpoint:** `POST /v1/kyc/verify`
**Test scenarios:** valid → 200 VERIFIED · missing PAN → 400 · invalid PAN format → 400 ·
invalid/missing token → 401 · unknown customer → 404 · duplicate in-progress request → 409 ·
downstream failure → 500 · timeout (NSDL slow/down) → connection error, not a clean response.

### 1.2 Aadhaar eKYC / OKYC
**What it does:** Verifies identity using Aadhaar number + OTP sent to the registered mobile,
pulling name/address/DOB/photo from UIDAI.
**Endpoint:** `POST /v1/kyc/aadhaar/initiate` (sends OTP) → `POST /v1/kyc/aadhaar/verify` (submits OTP)
**Sample request (verify step):**
```json
{ "referenceId": "AAD-REQ-88213", "otp": "482913" }
```
**Sample success response:**
```json
{
  "status": "SUCCESS",
  "verified": true,
  "name": "R. SHARMA",
  "dob": "1990-04-11",
  "addressAvailable": true,
  "photoAvailable": true
}
```
**Test scenarios:** valid OTP → 200 verified · wrong OTP → 400 `INVALID_OTP` · OTP expired
(>3 min old, a real UIDAI rule) → 400 `OTP_EXPIRED` · OTP retry limit exceeded (3 attempts, a
real UIDAI limit) → 429 `MAX_ATTEMPTS_EXCEEDED` · Aadhaar not linked to a mobile number →
422 `MOBILE_NOT_LINKED` · UIDAI service down → 503.
**Compliance note:** Aadhaar data is masked-by-law (only last 4 digits ever stored/shown) —
this is a real, legally mandated data-masking requirement, not just good practice, worth
mentioning if asked about PII handling.

### 1.3 DigiLocker Pull
**What it does:** Fetches a government-issued document (PAN card, driving license, marksheet)
directly from a customer's DigiLocker account with their consent.
**Endpoint:** `GET /v1/digilocker/documents?docType=PANCR`
**Test scenarios:** valid, consented pull → 200 with document URI · consent not granted →
403 `CONSENT_REQUIRED` · document type not found in that account → 404 · consent token expired
→ 401 · rate-limited by DigiLocker → 429.

### 1.4 CKYC Registry Lookup
**What it does:** Checks India's Central KYC Registry to see if a customer already has a
verified KYC record anywhere in the financial system — avoids re-collecting the same documents.
**Endpoint:** `GET /v1/ckyc/search?panNumber=ABCDE1234F`
**Sample success response:**
```json
{ "found": true, "ckycNumber": "10012345678901", "kycStatus": "VERIFIED", "lastUpdated": "2025-11-02" }
```
**Test scenarios:** record found → 200 with CKYC number · no record found (new customer) →
200 `found: false` (not an error — this is a normal outcome) · malformed PAN → 400 · registry
timeout → 504.

---

## 2. E-agreement / E-sign

### 2.1 Aadhaar eSign
**What it does:** Legally binds a customer to a loan/agreement document via an Aadhaar-based
digital signature (OTP-authenticated), same legal weight as a wet-ink signature under the IT Act.
**Endpoint:** `POST /v1/esign/initiate`
**Sample request:**
```json
{ "documentId": "AGMT-2026-4471", "aadhaarLast4": "8821", "signerName": "R. Sharma" }
```
**Test scenarios:** valid signing flow → 200, signed PDF returned · OTP mismatch → 400 ·
document already signed (someone re-submits) → 409 `ALREADY_SIGNED` · document ID doesn't
exist → 404 · signer name doesn't match the Aadhaar name on record → 422 `NAME_MISMATCH`
(a real fraud-prevention check) · signing link expired (typically 24-48 hr window) → 410 `GONE`.

### 2.2 E-stamp & E-sign (Leegality-style)
**What it does:** Applies government e-stamp duty *and* digital signature to a document in one
flow — the e-stamp part is what makes it legally admissible as a stamped agreement, not just signed.
**Endpoint:** `POST /v1/estamp/create`
**Test scenarios:** valid, correct stamp duty for the state/document type → 200 · wrong stamp
duty amount for that document category → 400 `INCORRECT_STAMP_VALUE` (each Indian state has
different stamp duty rules — a real, state-specific compliance check) · document exceeds max
page limit for e-stamping → 400 · e-stamp vendor (SHCIL) service down → 503.

---

## 3. Credit & Risk

### 3.1 CIBIL / Credit Bureau Pull
**What it does:** Pulls a customer's credit score and report from CIBIL (or Experian/CRIF) to
inform a lending decision.
**Endpoint:** `POST /v1/credit/bureau-check`
**Sample success response:**
```json
{ "status": "SUCCESS", "cibilScore": 742, "reportId": "CB-99213", "enquiriesLast6Months": 2 }
```
**Test scenarios:** valid pull, score returned → 200 · customer has no credit history ("NH" —
No History, a real, valid, non-error outcome for a first-time borrower) → 200 `score: null,
reason: "NH"` · PAN doesn't match any bureau record → 404 · consent not captured before pull →
403 (RBI mandates explicit consent before *any* bureau pull — this is a hard compliance rule,
not optional) · bureau service down → 503 · duplicate pull within cooldown window (bureaus rate-
limit how often the same PAN can be queried) → 429.

### 3.2 Internal Risk-Scoring Engine
**What it does:** Combines bureau score + income + existing exposure + behavioral data into a
final approve/reject/refer decision — this is the company's own proprietary model, not a
third-party pull.
**Endpoint:** `POST /v1/risk/score`
**Test scenarios:** valid input, score returned → 200 `decision: APPROVE/REFER/REJECT` ·
missing income data → 400 · model service degraded, falls back to a simpler rule-based score →
200 with a `fallbackUsed: true` flag (a real resilience pattern worth knowing — graceful
degradation instead of hard failure) · customer already has an active loan exceeding exposure
limit → 200 `decision: REJECT, reason: "EXPOSURE_LIMIT"`.

### 3.3 Bank Statement Analysis
**What it does:** Analyzes a customer's bank statement (pulled via Account Aggregator or
uploaded PDF) to verify income and spending patterns — a real alternative to payslips for
gig-economy or self-employed applicants.
**Endpoint:** `POST /v1/risk/statement-analysis`
**Test scenarios:** valid statement, income verified → 200 · statement too short (<3 months,
below the typical minimum a lender requires) → 400 `INSUFFICIENT_HISTORY` · statement shows
bounced cheques/failed EMIs (a real red flag) → 200 `flags: ["BOUNCED_PAYMENT"]` · unreadable
PDF/OCR failure → 422 `PARSE_FAILED`.

---

## 4. Payments & Payouts

### 4.1 UPI Payment
**What it does:** Sends or receives money instantly via a UPI ID (VPA) — this is what your
Partner Ops payout scenarios were modeling conceptually.
**Endpoint:** `POST /v1/payments/upi`
**Sample request:**
```json
{ "payerVpa": "customer@okhdfcbank", "payeeVpa": "bajajfinserv@icici", "amount": 15000.00, "purpose": "EMI_PAYMENT" }
```
**Test scenarios:** valid, completes → 200 `SUCCESS` · invalid VPA format → 400 · insufficient
balance → 200 `status: FAILED, reason: "INSUFFICIENT_FUNDS"` (note: this is a 200, not a 400 —
the *request* was valid, the *transaction* just didn't succeed, a genuinely important distinction)
· payment stuck in `PENDING` beyond expected window (UPI's real-world "money debited, credit
pending" scenario) → needs a reconciliation/status-check call, not a retry · duplicate payment
(same idempotency key sent twice) → returns the *original* result, doesn't charge twice.

### 4.2 NEFT/RTGS/IMPS Payout
**What it does:** Moves money to a bank account via India's interbank transfer rails — exactly
what your `payouts` table modeled.
**Endpoint:** `POST /v1/payouts/bank-transfer`
**Test scenarios:** valid → 200, `utrNumber` returned (the real bank reference number) ·
invalid IFSC code → 400 · beneficiary account doesn't exist (bank returns account-not-found) →
200 `status: FAILED, reason: "INVALID_ACCOUNT"` · RTGS attempted below ₹2 lakh minimum (a real
RBI rule — RTGS has a minimum transfer amount, NEFT/IMPS don't) → 400 `BELOW_RTGS_MINIMUM` ·
duplicate payout, same amount+date+beneficiary → this is literally I3 from your SQL project.

### 4.3 Payment Gateway (Razorpay/Cashfree-style)
**What it does:** Collects payment *from* a customer via card/UPI/netbanking on a checkout page.
**Endpoint:** `POST /v1/payment-gateway/orders`
**Test scenarios:** valid order created → 200 · card declined by issuing bank → 200
`status: FAILED, reason: "CARD_DECLINED"` · webhook for payment confirmation never arrives
(the gateway's own reliability problem — a real reason to always have a manual reconciliation
job, not just trust webhooks) · signature verification fails on an incoming webhook (a real
security check — you must verify a webhook payload wasn't forged before trusting it) → reject,
don't process.

### 4.4 e-NACH / Mandate Setup
**What it does:** Sets up a standing instruction so EMIs auto-debit from a customer's bank
account every month, without needing a fresh authorization each time.
**Endpoint:** `POST /v1/enach/mandate`
**Test scenarios:** valid mandate created → 200, pending customer bank approval · mandate
amount exceeds customer's per-transaction limit set with their bank → rejected by bank, not
your system · customer's bank doesn't support e-NACH (some smaller/co-op banks don't) → 400
`BANK_NOT_SUPPORTED` · mandate execution fails on due date (insufficient balance) → this
triggers a bounced-EMI workflow, a real operational scenario, not just an error code.

---

## 5. Core Banking / Ledger

### 5.1 Finacle Core Banking Integration
**What it does:** The system of record — every payout, EMI collection, and balance update
ultimately has to post to the core banking ledger (Finacle, in Bajaj Finserv's case) to be real.
**Endpoint:** `POST /v1/core-banking/post-transaction`
**Test scenarios:** valid posting → 200, ledger balance updated · account frozen/dormant →
400 `ACCOUNT_FROZEN` · core banking system in end-of-day batch window (a real, common
constraint — core banking systems often have maintenance windows where live posting is
paused) → 503 `EOD_IN_PROGRESS` · two systems both post the same transaction (a
double-entry-bookkeeping integrity issue) → the ledger should reject/reconcile, not silently
double-book. **This is the category you already have genuine hands-on Bajaj Finserv experience
in — lean on that in the interview instead of hypotheticals.**

---

## 6. Fraud & AML Screening

### 6.1 PEP (Politically Exposed Person) List Screening
**What it does:** Checks if a customer (or their close associates) is a politically exposed
person — a legal requirement before onboarding, since PEPs need enhanced due diligence.
**Endpoint:** `POST /v1/screening/pep-check`
**Test scenarios:** clean match, no PEP → 200 `match: false` · exact name match found → 200
`match: true, matchScore: 98` · fuzzy/partial name match (common name, needs human review, not
an auto-reject) → 200 `match: "POSSIBLE", matchScore: 61, requiresManualReview: true` — this
distinction (auto-clear vs. auto-reject vs. needs-a-human) is the real nuance in fraud
screening, worth naming explicitly.

### 6.2 Sanctions List Check
**What it does:** Screens against government/UN sanctions lists (OFAC, UN Security Council,
etc.) — a hard legal block, not a risk score, if there's a confirmed match.
**Endpoint:** `POST /v1/screening/sanctions-check`
**Test scenarios:** clean → 200 `cleared: true` · confirmed match → 200
`cleared: false, action: "BLOCK_ONBOARDING"` (this must hard-block, unlike PEP screening which
allows manual review — worth knowing that distinction exists) · list provider's data is stale
(hasn't synced in >24hr, a real freshness/data-quality concern) → flagged internally even if
the check itself returns clean.

### 6.3 Device Fingerprinting
**What it does:** Identifies the device/browser making a request to detect fraud patterns
(same device used across 20 different "new customer" applications, for example).
**Endpoint:** `POST /v1/fraud/device-check`
**Test scenarios:** new, clean device → 200 low risk score · device seen on multiple recent
applications under different names → 200 high risk score, flagged · device fingerprint spoofed/
missing (common on some browsers with privacy settings) → 200 `fingerprint: "PARTIAL",
confidence: "LOW"` — a partial signal, not a hard failure.

### 6.4 Velocity Check
**What it does:** Flags unusual *speed* of activity — 5 loan applications in 10 minutes from
one number, 3 payout requests in an hour that normally happens once a month.
**Endpoint:** `POST /v1/fraud/velocity-check`
**Test scenarios:** normal activity pattern → 200 `flagged: false` · threshold breached (e.g.
>3 applications/hour) → 200 `flagged: true, rule: "APPLICATION_VELOCITY"` — this is literally
the same shape of query as your A4 (payout request after suspension) — cross-referencing
*behavior* against a *rule*, just a time-based rule instead of a status-based one.

---

## 7. Regulatory Reporting

### 7.1 RBI/SEBI Reporting Feed
**What it does:** Periodically submits required data (loan book summary, NPA figures,
transaction volumes) to the regulator in a prescribed format.
**Endpoint:** `POST /v1/regulatory/rbi-submission`
**Test scenarios:** valid submission, accepted → 200 `acknowledgementNumber` returned ·
data fails the regulator's own schema validation → 400 with a specific field-level error (the
regulator's API tells you *exactly* what's wrong — this is real, not hypothetical) · submission
window closed (these have hard monthly/quarterly deadlines) → 403 `SUBMISSION_WINDOW_CLOSED` —
a missed regulatory deadline is a genuine compliance incident, not just a bug.

### 7.2 CKYC Upload
**What it does:** The reverse of 1.4 — *uploading* a newly completed KYC record to the central
registry so other institutions can find it later.
**Endpoint:** `POST /v1/ckyc/upload`
**Test scenarios:** valid upload → 200, CKYC number assigned · duplicate upload for a PAN
that's already registered → 409, should update not duplicate · mandatory field missing per
CKYC's own schema (father's name, a required field in India's KYC norms) → 400.

### 7.3 Suspicious Transaction Report (STR) Filing
**What it does:** Files a report with India's Financial Intelligence Unit (FIU-IND) when a
transaction pattern looks like potential money laundering — a legal obligation, and the
filing itself is confidential (the customer is never told).
**Endpoint:** `POST /v1/regulatory/str-filing`
**Test scenarios:** valid filing submitted → 200, filed within the legally required window (7
working days from detection in India) · filing submitted late → this is logged as a compliance
breach internally, a real operational risk to track · filing references a transaction ID that
doesn't exist in the system → 400 (data integrity check — you can't file an STR on a
transaction you can't actually prove happened).

---

## 8. Notifications / Webhooks

### 8.1 SMS/Email/WhatsApp Gateway
**What it does:** Sends the OTPs, confirmations, and reminders customers actually see —
"Your KYC is verified," "EMI due tomorrow."
**Endpoint:** `POST /v1/notifications/send`
**Test scenarios:** valid send → 200, `messageId` returned · invalid phone/email format → 400
· delivery fails downstream (number doesn't exist, mailbox full) — note the send *API call*
still returned 200 (it accepted the job), the *delivery* fails separately and asynchronously,
usually reported via a callback — a real and important distinction between "the API accepted
my request" and "the thing I asked for actually happened" · rate limit hit (can't spam the
same number) → 429.

### 8.2 Internal Webhook (Payout Completed / KYC Verified)
**What it does:** Your own system telling *other* internal systems "this thing just happened" —
e.g., core banking tells the customer-notification service a payout completed.
**Endpoint:** `POST {subscriber's URL}/webhooks/payout-completed` (you're the *sender* here, not receiver)
**Test scenarios:** subscriber acknowledges (200) → done · subscriber is down/times out → your
system needs a retry-with-backoff policy, not a one-shot fire-and-forget (a real reliability
pattern worth naming) · subscriber receives the same event twice (a retry after a slow-but-
successful first attempt) → the subscriber must handle it idempotently, same lesson as 4.1's
duplicate payment · payload signature can't be verified by the subscriber → they should reject
it, and you should be able to prove authenticity (HMAC signing is the standard approach).

---

## 9. Account Aggregator (AA)

### 9.1 RBI Account Aggregator Data Pull
**What it does:** With explicit customer consent, pulls financial data (bank statements,
insurance, investments) from *other* institutions via India's AA framework (Setu, Finvu, etc.)
— this is the modern, RBI-sanctioned replacement for asking customers to email PDFs.
**Endpoint:** `POST /v1/aa/consent` (request consent) → `GET /v1/aa/data/{consentId}` (pull once approved)
**Test scenarios:** consent requested, customer approves in their AA app → data pull succeeds,
200 · customer denies consent → 403 `CONSENT_DENIED`, and you must not retry without a fresh
request · consent approved but expires before data pull happens (consents have a validity
window, often single-use or time-boxed) → 410 `CONSENT_EXPIRED` · source institution (the bank
holding the data) is unreachable → the AA framework itself surfaces this as a specific error,
not a generic failure, since the AA is a "consent broker," not the data holder itself — a real
architectural nuance: you're always talking to 3 parties (you, the AA, the actual bank), not 2.

---

## The pattern across all 24

Notice every single one of these reduces to the same handful of question categories you
already rehearsed on the KYC project:

1. **Does it work with valid input?**
2. **Does it correctly reject bad/missing input?**
3. **Does it enforce who's allowed to ask?**
4. **Does it handle "the request was fine but the outcome wasn't" separately from "the request
   itself was broken"** (this is the UPI/payment-gateway 200-with-FAILED-status pattern — one
   of the most commonly missed distinctions, worth having ready)?
5. **Does it handle duplicates/retries without double-processing?**
6. **What happens when a downstream/third-party system is slow, down, or lying?**
7. **Is there a compliance-specific rule layered on top of the generic pattern** (consent,
   masking, a regulatory deadline, a state-specific stamp duty) **that a generic API test
   wouldn't catch unless you know the domain?**

That seventh point is the actual differentiator for a compliance-flavored PM role — anyone can
test "does the API return 200." Knowing *which* extra domain rule applies to *which* API, and
why it matters, is what this whole document is really testing your fluency on.
