import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent

steps = [
    ("Validate correlation", "tests/validate_correlation.py"),
    ("Generate incident cases", "src/correlate_events.py"),
    ("Build HTML report", "src/generate_report.py"),
]

for title, script in steps:
    print(f"\n--- {title} ---", flush=True)
    subprocess.run(
        [sys.executable, str(PROJECT / script)],
        cwd=PROJECT,
        check=True
    )

print("\nDemo completed successfully.")
print(f"Report: {PROJECT / 'reports' / 'investigation-report.html'}")
