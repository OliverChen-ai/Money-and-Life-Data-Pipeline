"""Checks the cleaned C15 financial well-being series and actual age labels."""
import pandas as pd
from common import CLEAN

path = CLEAN / "04C_C15_2019Q1_2026Q3.csv"
df = pd.read_csv(path)
age = df.loc[df["Segment_Type"].eq("Age group")]
result = {
    "age_series": int(age["Series_ID"].nunique()),
    "missing_age_labels": int(age["Age_Group"].isna().sum()),
    "duplicate_quarter_series": int(df.duplicated(["Quarter", "Series_ID"]).sum()),
    "age_groups": age["Age_Group"].dropna().unique().tolist(),
}
for k, v in result.items():
    print(f"{k}: {v}")
assert result["age_series"] == 6
assert result["missing_age_labels"] == 0
assert result["duplicate_quarter_series"] == 0
print("\nVerification completed.")
