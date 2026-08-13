# Power Automate + AI Builder Practice — Policy Ops Triage (Basic + Advanced)

**Why this exists:** you listed real experience with Power Automate + AI-driven
document/email automation on your resume ("automate email triaging and
document extraction, reducing manual effort by 40%"). This project exists to
put a real, hands-on, screenshot-able build behind that claim — a fresh
scenario, not a repeat of PCMS or OpsPilot, but the same domain instinct
(BFSI operations) applied to a different real tool: **Microsoft Power
Automate**, using its built-in AI Builder for the "DocLM"-style
classification and extraction step.

This becomes two case studies once done:
1. **Basic** — an email-triage flow: classify an inbound email into a
   category and log it automatically.
2. **Advanced** — a document-extraction flow: pull structured fields out of
   an attached policy document and route it based on whether extraction
   succeeded.

The scenario: **"Bharat Assure General Insurance"** (fictional — no real
company). Its policy-ops inbox gets renewal requests, claim inquiries, and
document submissions. Today a person reads every email and decides what to
do; this project automates the triage step.

---

## Step 0 — Setup (~15 min)

1. Go to **https://make.powerautomate.com** and sign in (or sign up free)
   with a Microsoft account. The free plan is enough for everything here.
2. You'll trigger flows using your own email inbox (Outlook.com or
   Microsoft 365) — no shared mailbox needed. To avoid the flow firing on
   your real mail, every test email you send yourself in this guide uses
   the subject prefix **`[PolicyOps]`** — you'll filter the trigger to only
   fire on that prefix.
3. Both Excel files below need to live in **your own OneDrive** (Power
   Automate's Excel connector reads from OneDrive/SharePoint, not a local
   file) — upload them there before you start building.

**Files in this folder:**
- `PolicyOpsLog-Basic.xlsx` — pre-built Excel table for Part 1 (upload to OneDrive)
- `PolicyRenewals-Advanced.xlsx` — pre-built Excel table for Part 2 (upload to OneDrive)
- `sample-documents/policy-renewal-01.pdf`, `-02.pdf`, `-03.pdf` — synthetic renewal forms for Part 2 (already correctly formatted for AI Builder to read — no upload needed, just attach these to test emails)

---

## Part 1 — BASIC: Email Triage Flow

**Goal:** an email arrives → AI classifies it into a category → the result
gets logged automatically to Excel.

1. In Power Automate, **Create → Automated cloud flow**.
2. Trigger: search for **"When a new email arrives (V3)"** (Outlook
   connector). Under its advanced options, set **Subject Filter** to
   `[PolicyOps]` so it only fires on your test emails.
3. Add an AI step. Search Power Automate's action list for **AI Builder**
   — look for an action like **"Extract information from text"** or
   **"Create text with GPT using a prompt"** (exact name varies by tenant/
   region — if you don't see either, search just "AI Builder" and take a
   screenshot of what's available and I'll point you to the right one).
   Give it a prompt like:
   > Classify this email into exactly one category: Policy Renewal, Claim
   > Inquiry, Document Submission, or General Inquiry. Reply with only the
   > category name.

   Pass in the trigger's **Subject** and **Body** as the input text.
4. Add **"Add a row into a table"** (Excel Online connector) → pick your
   OneDrive file `PolicyOpsLog-Basic.xlsx` → table `PolicyOpsLog` → map:
   - Timestamp → `utcNow()` (an expression, or just the trigger's received time)
   - SenderEmail → trigger's **From**
   - Subject → trigger's **Subject**
   - Category → the AI step's output
   - Status → type the literal text `Logged`
5. Save the flow.

**Test it:** send yourself 4 emails, one per category, each subject
starting with `[PolicyOps]`:

| Subject | Body |
|---|---|
| `[PolicyOps] Renewal Request - Policy BA-MOT-224871` | "Hi, I'd like to renew my motor policy before it expires next month. Please confirm the renewal premium." |
| `[PolicyOps] Status update needed on my claim` | "Following up again — it's been 10 days since I filed my claim and I haven't heard back. Can someone check on this?" |
| `[PolicyOps] Sending my updated KYC documents` | "Please find my updated address proof attached as requested. Let me know if anything else is needed." |
| `[PolicyOps] Question about premium payment options` | "Do you offer monthly installment payments instead of a lump sum premium? Just checking before I decide." |

Check the flow run history (each should show success), then open
`PolicyOpsLog-Basic.xlsx` in OneDrive and confirm all 4 rows landed with
sensible categories.

**Screenshot for me:** the flow's designer view (all 3 steps), one
successful run's details, and the Excel table with all 4 rows.

---

## Part 2 — ADVANCED: Document Extraction + Routing

**Goal:** an email with an attached policy renewal PDF arrives → AI Builder
extracts the structured fields (name, policy number, premium, expiry) → a
condition checks whether extraction actually got the key fields → routes to
an auto-logged record or a "needs manual review" flag, the same
confidence-gate concept as OpsPilot, this time built in a real enterprise
tool instead of a prototype.

1. **New flow**, same trigger as Part 1 (`[PolicyOps]` subject filter), but
   this time also add a **"Has Attachment"** condition so it only proceeds
   for emails with a PDF attached.
2. Add **"Get attachment"** (or use the trigger's built-in attachment
   output, depending on which trigger version you used).
3. Add an AI Builder document step — look for **"Extract information from
   documents"** or a similar document-understanding action. Point it at
   the attachment, and prompt/configure it to extract: **Policyholder
   Name, Policy Number, Premium, Policy Expiry Date**. (If your tenant only
   offers the older prebuilt models like "Invoice processing," that's a
   reasonable substitute — screenshot what you see and I'll help you map
   fields either way.)
4. Add a **Condition**: check whether the extracted **Policy Number** field
   is not blank (a simple, real proxy for "extraction succeeded").
   - **If yes** → "Add a row into a table" on `PolicyRenewals-Advanced.xlsx`
     → table `PolicyRenewals`, mapping the extracted fields, with
     `ExtractionStatus = Success` and `NeedsManualReview = No`.
   - **If no** → same action, but `ExtractionStatus = Failed` and
     `NeedsManualReview = Yes` (leave the extracted fields blank/partial —
     that's the honest result).
5. Save the flow.

**Test it:** send yourself 3 emails, each subject starting
`[PolicyOps] Renewal Request`, each with **one** of the 3 sample PDFs from
`sample-documents/` attached (one PDF per email). All 3 should extract
successfully and land as `Success` rows, since the sample forms are clean
and clearly labeled — that's deliberate, so you see the success path
working end to end before worrying about the failure path.

**Optional stretch:** send a 4th test email with a blurry photo of a
random receipt (not the sample forms) attached, to see the extraction
genuinely fail and land in the `NeedsManualReview = Yes` path — a real
"here's what happens when it doesn't work" moment, worth having for the
case study if you're up for it.

**Screenshot for me:** the flow's designer view (all steps, including the
condition branch), a successful run showing the extracted fields, and the
Excel table with the 3 (or 4) rows.

---

## What to send back

Screenshots as noted above for both parts, plus — in your own words — one
real observation: what would you change about the confidence/validation
logic if this were a live system handling real customer documents instead
of 3 clean sample forms? That's the part that turns this into a case study
instead of a working flow.

Once you send these, I'll write up the Basic and Advanced case studies with
your real screenshots and add them to the site.
