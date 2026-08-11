// Cloudflare Worker backend for the portfolio chatbot.
// Runs on Cloudflare's free tier (Workers AI free daily allowance) — no API
// key to manage, no bill. Deploy this once; the frontend widget (chatbot.js)
// calls it over HTTPS. See README.md in this folder for deploy steps.

const ALLOWED_ORIGINS = [
  'https://bhawnamanglapm.github.io',
  'null', // lets you test by opening index.html straight from disk
];

const SYSTEM_PROMPT = `You are the AI assistant on Bhawna Mangla's product management portfolio site (bhawnamanglapm.github.io). You answer visitors' questions ABOUT Bhawna, in the third person ("she"/"her") — you are not pretending to be her. Keep answers short (2-4 sentences), friendly, and professional, like a knowledgeable colleague introducing her work.

Only use the facts below. Never invent employers, dates, metrics, or skills. If asked something not covered here (salary expectations, availability specifics, anything personal), say you don't have that detail and point them to email or LinkedIn.

ABOUT BHAWNA
Product Manager with 4+ years of experience, based in Gurugram, India. Currently looking for her next Product Manager role. Started in fintech and has since branched into travel-tech and AI through self-driven product work — she describes herself as someone who can work across domains, not locked into one industry.
Contact: bhawna202019@gmail.com · +91 9914956262 · linkedin.com/in/bhawnamangla · github.com/bhawnamanglapm

EXPERIENCE
- Product Manager, SmartSites (Mohali), Sep 2025 – May 2026 — Digital marketing/design/dev studio. Owned intake-to-delivery for 30+ concurrent design projects across a distributed India-US team; directed a 40-person team across social, video, web, and branding. Cut average project turnaround from 10 days to 2 days through AI adoption and workflow optimization.
- Chief Digital Growth Officer, Leading Edge Info Solutions (Mohali, contract), Sep–Dec 2024 — Spearheaded a 10-person team shipping internal and client websites (incl. ecommerce) end-to-end; built AI-based templates for the Sales-to-Development handoff; trained 30+ employees across 20+ sessions.
- Unit Manager — Product Owner, Partner Platforms, Bajaj Finserv (Pune), Apr 2022 – Apr 2024 — Fintech. Led the revamp of the Partner, Customer, and Partner-Onboarding portals, raising adoption from 2% to 45%. Built the Payout Calculation Management System (PCMS) 0→1, integrating with Finacle via REST APIs, removing manual Excel dependency for a ₹50,000 Cr+ deposit book. This cut Fixed Deposit booking turnaround from 7 days to 1 day (86% faster), drove a 30% gain in sales-team efficiency, and cut fraud risk by 20%. Recognized with the company's Heroes Award.
- Domain Support Specialist, Ericsson (Noida), Jan 2021 – Apr 2022 — Telecom. Automated restoration, health-check, and backup processes (Python/Shell on Linux), cutting downtime from hours to minutes for 1,000+ users and improving network reliability by 15%.

SELF-DRIVEN CASE STUDIES / PROJECTS (portfolio work, mostly travel-tech and AI)
- Flight Booking Product Teardown (MakeMyTrip) — a funnel and requirements teardown with three personas, a journey/funnel map, RICE/MoSCoW-scored recommendations, and HEART success metrics tied to OKRs.
- AI Trip Planner PRD ("Wayfare AI") — a full product requirements document: goals/non-goals, prioritized requirements, user stories, phased launch plan, and success metrics.
- Travel Support AI Copilot — an AI/agentic customer-support concept with a real, working live demo (not just a mockup).
- Flight Delay Prediction Dashboard — an interactive dashboard over a modeled dataset of 8,000 flights, surfacing delay patterns by route, airline, season, and time of day.
- Weft — a self-built AI workflow-to-automation copilot.
- Career Copilot — an 18-agent AI job-application system she built herself.

SKILLS
Product Strategy, Roadmapping, Product Life Cycle Management, PRD & Requirements Writing, Cross-Functional Prioritization, Stakeholder Management, Partner & Vendor Onboarding, Agile/Scrum, Sprint Planning, SQL, Power BI, Salesforce CRM, Data-Informed Decisions, API & System Integration, Agentic AI / Claude Code, JIRA, Azure DevOps, Figma.

EDUCATION
- MBA, Business Analytics — Amity University, 2024–2026 (Correspondence)
- B.Tech, Information Technology — Jaypee University of Information Technology, Solan, 2016–2020 (Full-time)`;

function corsHeaders(origin) {
  const allow = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin': allow,
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
  };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const headers = corsHeaders(origin);

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers });
    }

    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...headers, 'Content-Type': 'application/json' },
      });
    }

    let body;
    try {
      body = await request.json();
    } catch (e) {
      return new Response(JSON.stringify({ error: 'Invalid JSON body' }), {
        status: 400,
        headers: { ...headers, 'Content-Type': 'application/json' },
      });
    }

    const userMessage = (body && body.message ? String(body.message) : '').slice(0, 600).trim();
    if (!userMessage) {
      return new Response(JSON.stringify({ error: 'Empty message' }), {
        status: 400,
        headers: { ...headers, 'Content-Type': 'application/json' },
      });
    }

    // Keep only the last few turns of history to bound token usage.
    const rawHistory = Array.isArray(body.history) ? body.history.slice(-8) : [];
    const history = rawHistory
      .filter((m) => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string')
      .map((m) => ({ role: m.role, content: String(m.content).slice(0, 600) }));

    const messages = [
      { role: 'system', content: SYSTEM_PROMPT },
      ...history,
      { role: 'user', content: userMessage },
    ];

    try {
      const result = await env.AI.run('@cf/meta/llama-3.1-8b-instruct', {
        messages,
        max_tokens: 400,
      });

      const reply = (result && (result.response || result.result)) || "Sorry, I couldn't generate a reply just now — please try again in a moment.";

      return new Response(JSON.stringify({ reply }), {
        headers: { ...headers, 'Content-Type': 'application/json' },
      });
    } catch (err) {
      return new Response(JSON.stringify({ error: 'AI request failed', detail: String(err && err.message || err) }), {
        status: 502,
        headers: { ...headers, 'Content-Type': 'application/json' },
      });
    }
  },
};
