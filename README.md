# Attack Story 🔎

Turn related security events into an investigation timeline.

A Python security automation prototype that connects repeated
login failures, a successful login, and an Administrators group
addition, then generates a JSON case and an HTML investigation report.

## Demo Scenario

Eight fictional events produce one case containing seven related
events for alex on LAB-PC. An unrelated login for jamie is excluded.

## What It Automates

- Loads and validates JSONL event records.
- Sorts events by timestamp.
- Ignores exact duplicate records.
- Detects five or more failures within five minutes before success
  for the same user, host, and source IP.
- Connects an Administrators addition within ten minutes after
  that success for the same affected user and host.
- Saves supporting evidence in a JSON case.
- Generates a browser-readable investigation report.

## Run the Demo

Requirements: Python 3.10 or newer. No external packages required.

From the project folder, run:

    python3 run_demo.py

On macOS, open the report with:

    open reports/investigation-report.html

The workflow runs validation, generates cases, and builds the report.
It stops if a step fails.

## Explore the Project

- [Correlation engine](src/correlate_events.py)
- [Sample events](sample-data/demo-events.jsonl)
- [Validation script](tests/validate_correlation.py)
- [Validation results](reports/correlation-validation.json)
- [Generated case](reports/incident-cases.json)
- [HTML report source — download to view](reports/investigation-report.html)
- [Demo runner](run_demo.py)

## Validation

Ten checks passed against the supplied fixtures:

- Complete sequence.
- Only four failures.
- Failure outside the five-minute window.
- Group addition for another user.
- Group addition on another host.
- Successful login from another IP.
- Group addition exactly ten minutes after success.
- Group addition beyond ten minutes.
- Four failures plus a duplicate.
- Duplicate excluded from case evidence.

## Scope and Limitations

- Uses synthetic records; no live SIEM or endpoint integration.
- Related events do not prove compromise or causation.
- Group changes are associated by affected user and host.
  The group-change actor may be a different account.
- Duplicate detection compares all supplied field values.
  Separate real events with identical values may be collapsed.
- Only the English group name Administrators is supported.
- Keeps the latest qualifying login sequence per user and host.
- Requires the input to fit in memory.
- Tests cover selected scenarios, not production effectiveness.
- Reports overwrite the previous generated outputs.
- Run the complete workflow before sharing refreshed results.

## Next Improvements

- Source event IDs and stronger input validation.
- Configurable thresholds and input paths.
- Multiple overlapping investigation sequences.
- Additional negative and malformed-input tests.
- Real telemetry adapters.
