"""First inspection of the original Bank of Canada C15 CSV (no edits)."""
from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parent.parent
src = ROOT / "data_raw" / "CES_C15_DEMOGRAPHICS.csv"
with src.open("r", newline="", encoding="utf-8-sig") as f:
    for i, row in enumerate(csv.reader(f), 1):
        print(f"Line {i}: {row}")
        if i >= 35:
            break
print("\nInitial data inspection completed.")
