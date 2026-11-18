"""Find the SERIES and OBSERVATIONS markers in the Bank of Canada export."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = ROOT / "data_raw" / "CES_C15_DEMOGRAPHICS.csv"
with src.open("r", encoding="utf-8-sig", newline="") as f:
    rows = list(csv.reader(f))
print("Total CSV rows:", len(rows))
for section in ["SERIES", "OBSERVATIONS"]:
    matches = [i for i, r in enumerate(rows) if r and r[0].strip() == section]
    print(f"\n--- {section} ---")
    if not matches:
        raise ValueError(f"Missing section: {section}")
    pos = matches[0]
    print("Found at line:", pos + 1)
    for i in range(pos, min(pos + 12, len(rows))):
        print(f"Line {i + 1}: {rows[i][:8]}")
print("\nStructure inspection completed.")
