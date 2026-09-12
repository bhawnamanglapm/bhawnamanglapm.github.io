# Merchant Payment Operations & Dispute Hub
### A Product Owner case study in regulated fintech: from discovery to post-launch

> **Simulation project.** This is a self-directed portfolio exercise that demonstrates end-to-end Product Owner practice. It does not describe an actual client system. All merchants, figures, dates, teams, vendors and reason codes are fictional or illustrative. Market research refers to publicly available information about real providers, with sources listed in the Discovery & Decision Log.

---

## At a glance

| | |
|---|---|
| **Role** | Product Owner (simulated) |
| **Domain** | Card payments, merchant dispute and chargeback operations |
| **Product** | Self-service dispute portal for merchants, plus an internal operations workbench |
| **Simulated timeline** | Build July–December 2026, pilot January 2027, general availability December 2027 |
| **Artifacts** | 17 files: PRD, backlog, RTM, KPIs, roadmap, RAID, change log, engagement plan, business case, post-launch plan, discovery log, wireframes, executive deck, SQL lab |

## The problem

Merchants handle card disputes by email and spreadsheets. Deadlines are tracked by hand, evidence is emailed to dispute operations and re-keyed, and nobody can see where a dispute stands. In the simulated baseline:

- **78%** of merchant responses arrive on time, and **9%** of closed disputes are lost only because the deadline passed
- Dispute operations spends **42 minutes** handling each dispute, and **100%** of evidence arrives by email
- Card numbers sit in email attachments, creating PCI DSS exposure
- Finance and Operations calculate win rate differently: **40% vs 62.5%** on the same disputes

## The solution

One portal where merchants see every dispute and its deadline, get reminders, upload evidence with card numbers redacted automatically, and understand how disputes affect their payouts. Behind it: processor integration, a prioritized ops work queue, and one agreed set of dispute numbers.

Beyond the MVP, the roadmap differentiates through **prevention and explainable AI**: pre-dispute alerts, dispute ratio health, an AI evidence copilot with human review, friendly fraud evidence automation, and readiness for purchases made by AI shopping agents.

## How I approached it

| Stage | What I did | Where to look |
|---|---|---|
| **1. Discover** | Benchmarked American Express, Adyen, Stripe and Razorpay; logged findings, gaps and decisions with sources and status | [`01-discovery`](01-discovery) |
| **2. Define** | Wrote the PRD; built a 47-item backlog across 9 epics (252 MVP points); traced 24 requirements to 62 test cases and 9 compliance controls; defined 21 KPIs with outcome definitions | [`02-product-definition`](02-product-definition) |
| **3. Design** | Created 13 annotated wireframes: 8 MVP screens and 5 concept screens, with rules, edge states and open questions | [`03-design`](03-design) |
| **4. Plan and govern** | Outcome-based roadmap (30 initiatives), RAID log, change control with impact assessments, stakeholder map, RACI and governance calendar | [`04-planning-and-governance`](04-planning-and-governance) |
| **5. Justify and launch** | Three-scenario business case, pilot-led go-to-market with KPI gates, launch readiness, hypercare, benefits tracking and BAU transition | [`05-business-case-and-launch`](05-business-case-and-launch) |
| **6. Communicate** | 17-slide executive review ending in five explicit decisions | [`06-executive-communication`](06-executive-communication) |
| **7. Measure** | SQL practice database with KPI, reconciliation and data quality queries, including deliberately planted data problems | [`07-data-and-sql`](07-data-and-sql) |

## Decisions worth discussing

1. **Resolving a stakeholder conflict without escalating or giving in.** The Fraud Operations Lead wanted full fraud case management in the MVP. I proposed a read-only fraud case reference in the MVP with a Phase 2 commitment (CR-01, Option C).
2. **Fixing a metric before reporting it.** Finance and Ops disagreed on win rate. The proposed definition reports Won, Partially won and Lost separately, with value recovery as the North Star (CR-05).
3. **Tracing one risk end to end.** Stale deadlines (R-03) → webhook assumption (A-02) → sandbox issue (I-01) → blocked story (US-019) → mapping defect (DEF-03) → failing requirement (BR-06) → latency KPI (KPI-12) → incident playbook (PB-02).
4. **Showing a business case that can lose money.** Base case NPV is $149k with a 2.3-year payback, but the conservative case is ($839k). That points leadership at the two assumptions that matter: merchant adoption and whether released ops capacity is cashable.
5. **Exiting hypercare on evidence, not a date.** Twelve exit criteria, including 10 business days without Sev 1 or Sev 2 incidents.
6. **Differentiating in a crowded market.** Online dispute portals are standard, including at American Express, so the roadmap competes on prevention and explainable AI rather than the portal itself.

## Business case (base scenario, illustrative)

| Measure | Value |
|---|---|
| One-time investment | $612k |
| 3-year NPV | $149k (conservative ($839k), optimistic $1.34M) |
| 3-year ROI | 26% |
| Payback after go-live | 2.3 years |
| Share of benefit from released ops capacity | ~85% |
| Merchant value at Year 3 (excluded from NPV) | ~$771k a year |

## Artifacts

| Folder | File | What it shows |
|---|---|---|
| `01-discovery` | Product_Discovery_and_Decision_Log.xlsx | 15 decisions (DSC-01 to DSC-15) with evidence, 21 cited sources and change notes |
| `02-product-definition` | PRD_Merchant_Dispute_Hub (.docx and .pdf) | Problem, goals, personas, journeys, requirements, NFRs, status model, metrics, release plan, beyond-MVP roadmap |
| | Product_Backlog_Merchant_Dispute_Hub.xlsx | Epics, user stories with acceptance criteria, sprint plan and dashboard |
| | RTM_Merchant_Dispute_Hub.xlsx | Requirements, test cases, compliance controls and defects with coverage gaps |
| | KPI_Definitions_Merchant_Dispute_Hub.xlsx | KPI catalog by tier, outcome definitions with a worked example, data dictionary |
| `03-design` | Dispute_Hub_Wireframes.html | 13 annotated screens with navigation, filters and a mobile view (open in a browser) |
| `04-planning-and-governance` | Product_Roadmap_Merchant_Dispute_Hub.xlsx | Timeline, Now / Next / Later board, themes, milestones and gates |
| | RAID_Log_Merchant_Dispute_Hub.xlsx | Risks, assumptions, issues and dependencies with a leadership dashboard |
| | Change_Log_Merchant_Dispute_Hub.xlsx | 9 change requests with options, impact and approval thresholds |
| | Engagement_Plan_Merchant_Dispute_Hub.xlsx | Stakeholder register, RACI, governance forums, communication plan, deliverables |
| `05-business-case-and-launch` | Business_Case_GTM_Merchant_Dispute_Hub.xlsx | Assumptions, three-scenario model, segments, rollout plan, enablement, launch readiness |
| | Post_Launch_Plan_Merchant_Dispute_Hub.xlsx | Hypercare, support model, KPI triggers, benefits tracker, iteration roadmap, BAU transition, lessons learned |
| `06-executive-communication` | Dispute_Hub_Executive_Review_v2 (.pptx and .pdf) | Executive narrative from problem to decisions |
| `07-data-and-sql` | Dispute_Hub_SQL_Lab.html | Interactive SQL lab with lessons and self-checking exercises (open in a browser) |
| | Dispute_Hub_SQL_Practice_Guide.md | Written guide: 8 levels, 54 lessons, 24 exercises, answer key |
| | dispute_hub_practice.db / .sql | Simulated data: 30 merchants, 400 disputes, settlements, events and more |

## How to view

- **In GitHub:** this README, the PRD PDF, the executive deck PDF and the SQL guide render directly.
- **Spreadsheets, Word and PowerPoint files:** download and open in Excel, Word or PowerPoint. Workbooks use live formulas, so dashboards update when inputs change.
- **Wireframes and SQL lab:** download and open in a browser, or enable GitHub Pages on this repository. The SQL lab loads sql.js from a CDN, so it needs an internet connection.

## Traceability

Every artifact uses shared IDs, so any item can be followed across documents:

`R- A- I- D-` RAID · `CR-` change requests · `EP- US-` backlog · `BR- TC- CTL- DEF-` requirements, tests, controls, defects · `KPI-` metrics · `LR-` launch readiness · `RM- MS-` roadmap · `DSC- SRC-` discovery decisions and sources · `S01–S13` wireframes · `SH- RA- DL-` engagement plan · `IR- BT- RV- LL-` post-launch

## Known gaps and next steps

- The Post-Launch Plan's iteration roadmap doesn't yet include the six beyond-MVP initiatives (RM-25 to RM-30) added to the Product Roadmap.
- Concept screens S09 to S13 are directional; each needs discovery, compliance review and a business case.
- Next artifacts: API specification with a Postman collection, analytics tracking plan, and a BI dashboard mockup.

## How this was built

Built as a self-directed simulation using Excel (formula-driven workbooks), Word, PowerPoint, HTML and SQLite, with AI assistance (Claude) for drafting and building artifacts.

---

*Simulation project for Product Owner practice. Not an actual client system.*
