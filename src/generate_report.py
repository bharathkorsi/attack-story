import html
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
REPORTS = PROJECT / "reports"


def escape(value):
    return html.escape(str(value), quote=True)


def main():
    cases = json.loads(
        (REPORTS / "incident-cases.json").read_text(encoding="utf-8")
    )
    validation = json.loads(
        (REPORTS / "correlation-validation.json").read_text(encoding="utf-8")
    )

    cards = []

    for case in cases:
        rows = []

        for event in case["evidence"]:
            details = []
            for field in ("source_ip", "actor", "group"):
                if field in event:
                    details.append(f"{field}: {event[field]}")

            rows.append(
                "<tr>"
                f"<td>{escape(event['timestamp'])}</td>"
                f"<td>{escape(event['event_type'])}</td>"
                f"<td>{escape(event['user'])}</td>"
                f"<td>{escape(event['host'])}</td>"
                f"<td>{escape(' | '.join(details))}</td>"
                "</tr>"
            )

        cards.append(f"""
        <section>
          <span class="badge">REQUIRES REVIEW</span>
          <h2>{escape(case['case_id'])}: {escape(case['title'])}</h2>
          <p><strong>Account:</strong> {escape(case['user'])}
          &nbsp; <strong>Host:</strong> {escape(case['host'])}</p>
          <h3>Why these events were connected</h3>
          <p>{escape(case['reason'])}</p>
          <div class="table-wrap">
            <table>
              <thead><tr>
                <th>Time</th><th>Event</th><th>User</th>
                <th>Host</th><th>Details</th>
              </tr></thead>
              <tbody>{''.join(rows)}</tbody>
            </table>
          </div>
          <p class="assessment">{escape(case['assessment'])}</p>
        </section>
        """)

    page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Attack Story — Investigation Report</title>
<style>
* { box-sizing: border-box; }
body {
  margin: 0; background: #101827; color: #e5edf7;
  font: 16px/1.6 system-ui, sans-serif;
}
main { max-width: 1150px; margin: auto; padding: 36px 20px; }
h1 { font-size: 38px; margin-bottom: 4px; }
h2 { font-size: 23px; }
h3 { font-size: 17px; }
.subtitle, footer { color: #b6c5d8; }
.stats { display: flex; flex-wrap: wrap; gap: 16px; margin: 26px 0; }
.stat, section {
  background: #1a2638; border: 1px solid #34465f;
  border-radius: 12px; padding: 22px;
}
.stat { flex: 1; min-width: 180px; }
.stat strong { display: block; font-size: 28px; color: #78e2ce; }
section { margin-bottom: 24px; }
.badge {
  display: inline-block; background: #503b18; color: #ffdb8d;
  padding: 4px 12px; border-radius: 20px; font-size: 12px;
}
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; font-size: 14px; }
th, td { text-align: left; padding: 12px; border-bottom: 1px solid #34465f; }
th { color: #78e2ce; }
.assessment { border-left: 3px solid #ffdb8d; padding-left: 12px; }
@media print {
  body { background: white; color: black; }
  .stat, section { background: white; color: black; }
}
</style>
</head>
<body><main>
<h1>Attack Story</h1>
<p class="subtitle">Automated security event correlation and investigation evidence</p>
"""

    page += f"""
<div class="stats">
  <div class="stat"><strong>{len(cases)}</strong>Generated cases</div>
  <div class="stat">
    <strong>{escape(validation['passed'])}/{escape(validation['total'])}</strong>
    Saved validation results
  </div>
  <div class="stat"><strong>Synthetic</strong>Demonstration data</div>
</div>
"""

    page += "".join(cards) or "<section>No matching sequences found.</section>"
    page += """
<footer>
<p>Portfolio prototype. Related events are investigation leads;
they do not establish compromise or causation.</p>
<p>Case data: incident-cases.json · Test results: correlation-validation.json.
These files are generated separately; rerun both before sharing.</p>
</footer>
</main></body></html>
"""

    output = REPORTS / "investigation-report.html"
    output.write_text(page, encoding="utf-8")
    print(f"Created: {output.relative_to(PROJECT)}")


if __name__ == "__main__":
    main()
