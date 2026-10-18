// Offline tests for the chatbot Worker. The Workers AI binding is stubbed, so this needs no
// Cloudflare account and makes no AI calls.   Run: node cf-worker/worker.test.mjs
import worker from "./worker.js";

const failures = [];
const check = (ok, label) => {
  console.log((ok ? "PASS " : "FAIL ") + label);
  if (!ok) failures.push(label);
};

const SITE = "https://bhawnamanglapm.github.io";
let aiCalls = 0;
const env = { AI: { run: async () => { aiCalls++; return { response: "ok" }; } } };
const call = async (method, { origin, body, headers = {} } = {}) => {
  const h = { ...headers };
  if (origin !== undefined) h.Origin = origin;
  const res = await worker.fetch(new Request("https://worker.test/", { method, headers: h, body }), env);
  return { res, json: async () => JSON.parse(await res.text()) };
};
const msg = (m) => JSON.stringify({ message: m });

{
  const r = await call("POST", { origin: SITE, body: msg("hello") });
  check(r.res.status === 200 && (await r.json()).reply === "ok", "request from the live site gets a reply");
  check(r.res.headers.get("Access-Control-Allow-Origin") === SITE, "CORS header names the live site");
}
{
  const before = aiCalls;
  const r = await call("POST", { origin: "null", body: msg("hello") });
  check(r.res.status === 403 && aiCalls === before, "opaque null origin is refused and no AI call is made");
  check(r.res.headers.get("Access-Control-Allow-Origin") === SITE, "null origin is never echoed back in CORS");
}
{
  const before = aiCalls;
  const r = await call("POST", { origin: "https://example.com", body: msg("hi") });
  check(r.res.status === 403 && aiCalls === before, "another website's origin is refused, no AI call");
  const none = await call("POST", { body: msg("hi") });
  check(none.res.status === 403 && aiCalls === before, "request with no Origin is refused, no AI call");
}
{
  const r = await call("OPTIONS", { origin: SITE });
  check(r.res.status === 200 && r.res.headers.get("Access-Control-Allow-Methods").includes("POST"), "preflight from the live site succeeds");
}
check((await call("GET", { origin: SITE })).res.status === 405, "GET is refused (405)");
check((await call("POST", { origin: SITE, body: "not json" })).res.status === 400, "invalid JSON is refused (400)");
check((await call("POST", { origin: SITE, body: msg("   ") })).res.status === 400, "empty message is refused (400)");
{
  const big = JSON.stringify({ message: "hi", history: [{ role: "user", content: "x".repeat(20000) }] });
  const r = await call("POST", { origin: SITE, body: big, headers: { "Content-Length": String(big.length) } });
  check(r.res.status === 413, "oversized body is refused (413)");
}
{
  const failing = { AI: { run: async () => { throw new Error("secret internal detail"); } } };
  const res = await worker.fetch(new Request("https://worker.test/", { method: "POST", headers: { Origin: SITE }, body: msg("hi") }), failing);
  const text = await res.text();
  check(res.status === 502 && !text.includes("secret internal detail"), "AI failure returns 502 without leaking the internal error text");
}

console.log(failures.length ? `\n${failures.length} failure(s)` : "\nAll Worker tests passed.");
process.exit(failures.length ? 1 : 0);
