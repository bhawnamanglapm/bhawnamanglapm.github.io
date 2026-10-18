// Offline checks for the portfolio site. No network, no browser.   Run: node scripts/check.mjs
import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, normalize } from "node:path";

const failures = [];
const check = (ok, label, detail = "") => {
  console.log((ok ? "PASS " : "FAIL ") + label + (ok || !detail ? "" : "\n     " + detail));
  if (!ok) failures.push(label);
};

const walk = (dir) =>
  readdirSync(dir).flatMap((f) => {
    if (f === ".git" || f === "node_modules") return [];
    const p = join(dir, f);
    return statSync(p).isDirectory() ? walk(p) : [p];
  });
const pages = walk(".").filter((p) => p.endsWith(".html")).map((p) => normalize(p));
check(pages.includes("index.html") && pages.includes("404.html"), `found ${pages.length} HTML pages including index.html and 404.html`);

// 1. Every local file a page references exists, and every #fragment points at a real id.
const stripComments = (s) => s.replace(/<!--[\s\S]*?-->/g, "");
const brokenFiles = [];
const brokenFrags = [];
const noAlt = [];
for (const page of pages) {
  const html = stripComments(readFileSync(page, "utf8"));
  const ids = new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]));
  for (const m of html.matchAll(/\s(?:src|href)="([^"]*)"/g)) {
    const ref = m[1];
    if (!ref || /^(https?:|mailto:|tel:|data:|javascript:|\/\/)/.test(ref)) continue;
    const [path, frag] = ref.split("#");
    const clean = path.split("?")[0];
    if (!clean) {
      if (!frag || ref === "#") continue;
      // "#case-<slug>" links are opened as an overlay by script.js, which looks up a card with
      // data-case="<slug>" on the same page. So the card must exist, not an element with that id.
      const slug = frag.startsWith("case-") ? frag.slice(5) : null;
      const ok = slug ? html.includes(`data-case="${slug}"`) : ids.has(frag);
      if (!ok) brokenFrags.push(`${page} -> #${frag}`);
      continue;
    }
    const target = clean.startsWith("/") ? clean.slice(1) : join(dirname(page), clean);
    if (!existsSync(target) && !existsSync(join(target, "index.html"))) brokenFiles.push(`${page} -> ${ref}`);
  }
  for (const m of html.matchAll(/<img\b[^>]*>/g)) if (!/\salt=/.test(m[0])) noAlt.push(`${page}: ${m[0].slice(0, 60)}`);
}
check(brokenFiles.length === 0, `all local files referenced by pages exist (${brokenFiles.length} missing)`, brokenFiles.slice(0, 8).join("\n     "));
check(brokenFrags.length === 0, `all in-page #links point at an existing id (${brokenFrags.length} broken)`, brokenFrags.slice(0, 8).join("\n     "));
check(noAlt.length === 0, `all images have an alt attribute (${noAlt.length} without)`, noAlt.slice(0, 5).join("\n     "));

// 2. Pages have the basics.
const index = readFileSync("index.html", "utf8");
check(/<html[^>]*\slang="/.test(index), "index.html has a lang attribute");
check(/<title>[^<]+<\/title>/.test(index) && /name="description"/.test(index), "index.html has a title and meta description");
check((index.match(/<h1\b/g) || []).length === 1, "index.html has exactly one h1");

// 3. Chatbot wiring and Worker origin policy.
const bot = readFileSync("chatbot.js", "utf8");
check(/WORKER_URL\s*=\s*'https:\/\/[^']+\.workers\.dev'/.test(bot), "chatbot.js points at an https workers.dev URL");
const worker = readFileSync("cf-worker/worker.js", "utf8");
const origins = (worker.match(/const ALLOWED_ORIGINS = \[([\s\S]*?)\];/) || [])[1] || "";
check(/bhawnamanglapm\.github\.io/.test(origins) && !/'null'|"null"/.test(origins.replace(/\/\/.*$/gm, "")), "Worker allows only the live site origin, not the opaque 'null' origin");

// 4. No credentials committed. Contact details that the site shows publicly are not flagged.
const secretish = pages.concat(["chatbot.js", "script.js", "cf-worker/worker.js", "cf-worker/wrangler.toml"])
  .filter((f) => existsSync(f))
  .filter((f) => /(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)/.test(readFileSync(f, "utf8")));
check(secretish.length === 0, "no API keys or private keys found in pages, scripts or Worker files", secretish.join(", "));

// 5. Case studies that have their own GitHub repo must link to it. Cards not listed here are
// write-ups with no files behind them, so they have no repo; the count is printed, not failed.
const HAS_REPO = [
  "makemytrip-flight-booking-teardown", "ai-trip-planner-prd", "travel-support-ai-copilot", "weft-workflow-copilot",
  "career-copilot-ai-agents", "ai-ops-copilot", "ai-verification-research", "verification-gap-platform",
  "verification-gap-product-pass", "merchant-dispute-hub", "flight-delay-prediction-dashboard", "airline-operations-dashboard",
  "sql-saas-analytics-basic", "sql-saas-analytics-advanced", "amplitude-strideway-basic", "amplitude-strideway-advanced",
  "partner-ops-practice", "fintech-api-landscape",
];
const more = stripComments(readFileSync("travel-tech-more.html", "utf8"));
const cards = new Map([...more.matchAll(/<article\b[^>]*data-case="([^"]+)"[\s\S]*?<\/article>/g)].map((m) => [m[1], m[0]]));
const repoRe = /href="https:\/\/github\.com\/bhawnamanglapm\/[A-Za-z0-9_.-]+"/;
const missingRepo = HAS_REPO.filter((slug) => !cards.has(slug) || !repoRe.test(cards.get(slug)));
check(missingRepo.length === 0, `all ${HAS_REPO.length} case studies with their own repo link to it (${missingRepo.length} missing)`, missingRepo.join(", "));
console.log(`INFO ${cards.size - [...cards.values()].filter((c) => repoRe.test(c)).length} of ${cards.size} case-study cards have no dedicated repo (written analyses with no files)`);

console.log(failures.length ? `\n${failures.length} failure(s)` : "\nAll checks passed.");
process.exit(failures.length ? 1 : 0);
