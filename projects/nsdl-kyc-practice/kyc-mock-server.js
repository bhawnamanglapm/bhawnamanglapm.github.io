/**
 * Bajaj Finserv – NSDL KYC API (practice mock)
 *
 * A self-directed practice exercise, not a real NSDL integration. Simulates a
 * realistic third-party KYC verification endpoint with actual validation
 * logic — auth check, required-field checks, PAN/DOB format validation, and
 * a handful of business-rule branches — rather than returning one canned
 * response regardless of input. Used to rehearse and verify, for real, the
 * full connectivity -> authentication -> request validation -> business
 * logic -> error handling test matrix for a third-party API integration.
 */
const http = require('http');
const PORT = process.env.PORT || 4501;

function send(res, status, body) {
  res.writeHead(status, {"Content-Type": "application/json"});
  res.end(JSON.stringify(body));
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url || '', 'http://localhost');
  const pathname = url.pathname;

  if (req.method === 'POST' && pathname === '/v1/kyc/verify') {
    let raw = '';
    req.on('data', chunk => raw += chunk);
    req.on('end', () => {
      // -- Authentication --
      const authHeader = req.headers['authorization'] || '';
      if (!authHeader) {
        return send(res, 401, { status: "FAILED", errorCode: "MISSING_AUTH", message: "Authorization header is required" });
      }
      if (authHeader !== 'Bearer VALID_TEST_TOKEN') {
        return send(res, 401, { status: "FAILED", errorCode: "INVALID_TOKEN", message: "Invalid or expired token" });
      }

      // -- Body parsing --
      let body;
      try { body = raw ? JSON.parse(raw) : {}; }
      catch (e) { return send(res, 400, { status: "FAILED", errorCode: "INVALID_JSON", message: "Request body is not valid JSON" }); }

      const { customerId, pan, dob } = body;

      // -- Required fields --
      if (!customerId) return send(res, 400, { status: "FAILED", errorCode: "MISSING_FIELD", message: "customerId is required" });
      if (!pan) return send(res, 400, { status: "FAILED", errorCode: "MISSING_FIELD", message: "PAN is required" });
      if (!dob) return send(res, 400, { status: "FAILED", errorCode: "MISSING_FIELD", message: "dob is required" });

      // -- Format validation --
      if (!/^[A-Z]{5}[0-9]{4}[A-Z]$/.test(pan)) {
        return send(res, 400, { status: "FAILED", errorCode: "INVALID_FORMAT", message: "PAN format is invalid (expected AAAAA9999A)" });
      }
      if (!/^\d{4}-\d{2}-\d{2}$/.test(dob)) {
        return send(res, 400, { status: "FAILED", errorCode: "INVALID_DATE_FORMAT", message: "dob must be in YYYY-MM-DD format" });
      }

      // -- Business-rule scenarios, keyed off customerId --
      if (customerId === 'NOTFOUND001') return send(res, 404, { status: "FAILED", errorCode: "CUSTOMER_NOT_FOUND", message: "No customer found with this ID" });
      if (customerId === 'DUPLICATE001') return send(res, 409, { status: "FAILED", errorCode: "DUPLICATE_REQUEST", message: "A KYC request for this customer is already in progress" });
      if (customerId === 'ERROR001') return send(res, 500, { status: "FAILED", errorCode: "INTERNAL_ERROR", message: "Something went wrong on our end" });
      if (customerId === 'TIMEOUT001') {
        // Simulates a slow/unresponsive third-party dependency — deliberately
        // delays the response so a short client-side request timeout fires
        // a real connection error, not a clean HTTP response.
        return setTimeout(() => send(res, 200, { status: "SUCCESS", customerId, kycStatus: "VERIFIED", verificationDate: "2026-09-10", requestId: "REQ-10002" }), 5000);
      }

      // -- Success --
      return send(res, 200, { status: "SUCCESS", customerId, kycStatus: "VERIFIED", verificationDate: "2026-09-10", requestId: "REQ-10001" });
    });
    return;
  }

  send(res, 404, { error: "Not Found" });
});

server.listen(PORT, () => console.log('Mock server listening on port ' + PORT));
