import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
INPUT = PROJECT / "sample-data" / "demo-events.jsonl"
OUTPUT = PROJECT / "reports" / "incident-cases.json"

LOGIN_WINDOW = timedelta(minutes=5)
GROUP_WINDOW = timedelta(minutes=10)
THRESHOLD = 5


def parse_time(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include a timezone")
    return parsed


def load_events(path):
    events = []
    with path.open(encoding="utf-8") as file:
        for number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
                for field in ("timestamp", "event_type", "user", "host"):
                    if not isinstance(event.get(field), str) or not event[field]:
                        raise ValueError(f"Missing or invalid {field}")
                parse_time(event["timestamp"])
                if event["event_type"] in ("login_failure", "login_success"):
                    if not event.get("source_ip"):
                        raise ValueError("Login event requires source_ip")
                events.append(event)
            except (ValueError, TypeError) as error:
                raise ValueError(f"Invalid event on line {number}: {error}")

    return sorted(events, key=lambda item: parse_time(item["timestamp"]))


def correlate(events):
    failures = defaultdict(deque)
    pending = {}
    cases = []

    seen = set()

    for event in events:
        fingerprint = json.dumps(event, sort_keys=True)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)

        time = parse_time(event["timestamp"])
        account = (event["user"], event["host"])
        kind = event["event_type"]

        if kind in ("login_failure", "login_success"):
            login_key = account + (event["source_ip"],)
            recent = failures[login_key]

            while recent and parse_time(recent[0]["timestamp"]) < time - LOGIN_WINDOW:
                recent.popleft()

            if kind == "login_failure":
                recent.append(event)
            else:
                if len(recent) >= THRESHOLD:
                    pending[account] = {
                        "success_time": time,
                        "events": list(recent) + [event]
                    }
                recent.clear()

        elif (
            kind == "group_member_added"
            and event.get("group", "").strip().casefold() == "administrators"
        ):
            candidate = pending.get(account)
            if candidate and timedelta(0) <= time - candidate["success_time"] <= GROUP_WINDOW:
                cases.append({
                    "case_id": f"CASE-{len(cases) + 1:03d}",
                    "title": "Repeated login failures, success, and admin addition",
                    "user": event["user"],
                    "host": event["host"],
                    "assessment": "Requires review; malicious activity undetermined",
                    "reason": (
                        "At least five failures within five minutes before success "
                        "for the same user, host, and IP; Administrators addition "
                        "within ten minutes for the same user and host."
                    ),
                    "evidence": candidate["events"] + [event]
                })
                del pending[account]

    return cases


def main():
    events = load_events(INPUT)
    cases = correlate(events)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")

    print(f"Events processed: {len(events)}")
    print(f"Cases generated: {len(cases)}")

    for case in cases:
        print(f"\n{case['case_id']} | User: {case['user']} | Host: {case['host']}")
        for event in case["evidence"]:
            print(f"  {event['timestamp']} | {event['event_type']}")
        print(f"Assessment: {case['assessment']}")

    print(f"\nSaved: {OUTPUT.relative_to(PROJECT)}")


if __name__ == "__main__":
    main()
