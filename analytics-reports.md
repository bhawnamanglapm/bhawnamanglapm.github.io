# Portfolio Analytics — Weekly Check-in Reports

GA4 property: **Bhawna Google analytics** (account `401525622`, property `546059777`, stream `Bhawna Portfolio`)
Site: https://bhawnamanglapm.github.io/ — Measurement ID `G-YNBV84LN1W`

This is a private reference, not part of the public site nav — nothing links to it. Open these each week, export as PDF (or screenshot), and share them in the Claude conversation for a summary and trend read.

1. **Realtime overview** — confirms tracking is live right now
   https://analytics.google.com/analytics/web/#/a401525622p546059777/realtime/overview?params=_u..nav%3Dmaui

2. **User engagement & retention overview** — active/new users, top pages, retention by cohort
   https://analytics.google.com/analytics/web/#/a401525622p546059777/reports/dashboard?params=_u..nav%3Dmaui&ruid=business-objectives-examine-user-behavior-overview,business-objectives,examine-user-behavior&collectionId=business-objectives&r=business-objectives-examine-user-behavior-overview

3. **Traffic acquisition** — which channel is actually sending visitors (Direct, Organic Social/LinkedIn, Organic Search, Referral)
   https://analytics.google.com/analytics/web/#/a401525622p546059777/reports/explorer?params=_u..nav%3Dmaui&ruid=lifecycle-traffic-acquisition-v2,business-objectives,generate-leads&collectionId=business-objectives&r=lifecycle-traffic-acquisition-v2

4. **Tech overview** — device, OS, and browser breakdown of visitors
   https://analytics.google.com/analytics/web/#/a401525622p546059777/reports/dashboard?params=_u..nav%3Dmaui&ruid=user-technology-overview,user,technology&collectionId=user&r=user-technology-overview

5. **Demographic details: Country** — where in the world visitors are
   https://analytics.google.com/analytics/web/#/a401525622p546059777/reports/explorer?params=_u..nav%3Dmaui&ruid=user-demographics-detail,user,demographics&collectionId=user&r=user-demographics-detail

## The weekly routine

A scheduled reminder fires every **Monday, 9:00 AM IST**, into this same Claude conversation.

Claude has no direct access to the Google account behind this GA4 property (no OAuth in this environment), so the reminder can't check the reports on its own. Each week works like this:
1. The reminder prompts a check-in.
2. Open the links above (or the property directly), export/screenshot the reports that have real data by then — start with **Traffic acquisition** and **User engagement & retention**, since those matter most early on.
3. Share them in the conversation.
4. Get a week-over-week read: what changed, what it means, and anything worth acting on (e.g., a case study nobody's opening, a channel that's actually working).

Last set up: 2026-09-08.
