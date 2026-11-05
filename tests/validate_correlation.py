import copy
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "src"))

from correlate_events import correlate, load_events

original = load_events(PROJECT / "sample-data" / "demo-events.jsonl")
cases = []


def scenario(name, expected, change):
    events = copy.deepcopy(original)
    change(events)
    cases.append((name, expected, events))


scenario("Complete sequence", 1, lambda events: None)

scenario(
    "Only four failures", 0,
    lambda events: events.pop(0)
)

scenario(
    "Failures outside five-minute window", 0,
    lambda events: events[0].update(timestamp="2026-11-05T09:59:00Z")
)

scenario(
    "Group addition for different user", 0,
    lambda events: events[6].update(user="another-user")
)

scenario(
    "Group addition on different host", 0,
    lambda events: events[6].update(host="OTHER-PC")
)

scenario(
    "Successful login from different IP", 0,
    lambda events: events[5].update(source_ip="192.0.2.99")
)

scenario(
    "Group addition exactly ten minutes later", 1,
    lambda events: events[6].update(timestamp="2026-11-05T10:14:30Z")
)

scenario(
    "Group addition beyond ten minutes", 0,
    lambda events: events[6].update(timestamp="2026-11-05T10:14:31Z")
)

def four_failures_with_duplicate(events):
    events.pop(0)
    events.append(copy.deepcopy(events[0]))


scenario(
    "Four failures plus duplicate must not trigger", 0,
    four_failures_with_duplicate
)

scenario(
    "Duplicate failure excluded from case evidence", 1,
    lambda events: events.append(copy.deepcopy(events[0]))
)

results = []
failures = 0

for name, expected, events in cases:
    events.sort(key=lambda event: event["timestamp"])
    generated = correlate(events)
    actual = len(generated)

    passed = actual == expected
    if passed and expected:
        evidence = generated[0]["evidence"]
        passed = (
            len(evidence) == 7
            and all(event["user"] == "alex" for event in evidence)
            and all(event["host"] == "LAB-PC" for event in evidence)
        )

    failures += not passed
    status = "PASS" if passed else "FAIL"
    line = f"{status}: {name} | expected={expected}, actual={actual}"
    print(line)
    results.append(line)

report = PROJECT / "reports" / "correlation-validation.json"
report.write_text(
    json.dumps({
        "total": len(cases),
        "passed": len(cases) - failures,
        "failed": failures,
        "results": results
    }, indent=2) + "\n",
    encoding="utf-8"
)

print(f"\nPassed: {len(cases) - failures}/{len(cases)}")
print("Saved: reports/correlation-validation.json")
sys.exit(1 if failures else 0)
