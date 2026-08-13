"""
Sends events.jsonl to a real Amplitude project via Amplitude's own HTTP API
V2 (the same endpoint Amplitude's official SDKs use under the hood).

Run this yourself, with your own API key — that's deliberate. The data
that lands in your Amplitude project should be something you actually
sent, not something injected on your behalf.

SETUP
-----
1. In Amplitude: Settings (gear icon, bottom left) -> Projects -> your
   project ("default") -> copy the "API Key" (NOT the Secret Key; the API
   Key is the write-only ingestion key, safe to use in a local script).
2. Set it as an environment variable, then run this script:

   Windows (PowerShell):
     $env:AMPLITUDE_API_KEY = "paste-your-api-key-here"
     python send_to_amplitude.py

   macOS/Linux:
     export AMPLITUDE_API_KEY="paste-your-api-key-here"
     python3 send_to_amplitude.py

3. Requires the `requests` library: pip install requests
"""

import json
import os
import sys
import time

import requests

AMPLITUDE_HTTP_API = "https://api2.amplitude.com/2/httpapi"
BATCH_SIZE = 500
INPUT_FILE = "events.jsonl"


def to_epoch_millis(iso_time):
    # events.jsonl stores "YYYY-MM-DDTHH:MM:SSZ"
    import datetime
    dt = datetime.datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%SZ")
    dt = dt.replace(tzinfo=datetime.timezone.utc)
    return int(dt.timestamp() * 1000)


def load_events():
    events = []
    with open(INPUT_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            events.append({
                "user_id": e["user_id"],
                "event_type": e["event_type"],
                "time": to_epoch_millis(e["time"]),
                "event_properties": e.get("event_properties", {}),
                "user_properties": e.get("user_properties", {}),
            })
    return events


def send_batch(api_key, batch):
    resp = requests.post(
        AMPLITUDE_HTTP_API,
        headers={"Content-Type": "application/json", "Accept": "*/*"},
        data=json.dumps({"api_key": api_key, "events": batch}),
        timeout=30,
    )
    return resp


def main():
    api_key = os.environ.get("AMPLITUDE_API_KEY")
    if not api_key:
        print("ERROR: AMPLITUDE_API_KEY environment variable is not set.")
        print("See the setup instructions at the top of this file.")
        sys.exit(1)

    events = load_events()
    total = len(events)
    print(f"Loaded {total} events from {INPUT_FILE}")

    sent = 0
    for i in range(0, total, BATCH_SIZE):
        batch = events[i:i + BATCH_SIZE]
        resp = send_batch(api_key, batch)
        if resp.status_code == 200:
            sent += len(batch)
            print(f"  batch {i // BATCH_SIZE + 1}: sent {len(batch)} events (total {sent}/{total}) — OK")
        else:
            print(f"  batch {i // BATCH_SIZE + 1}: FAILED (status {resp.status_code})")
            print(f"  response: {resp.text[:500]}")
            print("Stopping — fix the issue above, then re-run (Amplitude dedupes safely on retry).")
            sys.exit(1)
        time.sleep(0.3)  # stay well under rate limits

    print(f"\nDone. Sent {sent}/{total} events to Amplitude.")
    print("Give it 1-2 minutes to process, then check Data > Events in Amplitude —")
    print("event counts should start showing up under each event name.")


if __name__ == "__main__":
    main()
