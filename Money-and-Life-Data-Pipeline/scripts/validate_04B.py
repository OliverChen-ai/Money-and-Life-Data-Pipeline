"""04B: validate a researcher-compiled workbook from official published figures.

Unlike the other inputs, this workbook was assembled from several official releases.
It is not a single Statistics Canada raw-data export.
"""
import pandas as pd
from common import source_file, must_have, ensure_unique, write_table, write_report, summary

SHEETS = {
    "04B National Oct": "04B_National_October_Tableau.csv",
    "04B Early Monthly": "04B_Early_Monthly_Tableau.csv",
    "04B CMA": "04B_CMA_Tableau.csv",
}


def main() -> None:
    src = source_file("Money_and_Life_04B_Revised_Observed_Data_2020-2026.xlsx")
    for sheet_name, output_name in SHEETS.items():
        # The real header is row 5, after the title, blank and explanatory rows.
        df = pd.read_excel(src, sheet_name=sheet_name, header=4, engine="openpyxl")
        must_have(df, ["Reference_Period", "Age_Group", "Financial_Difficulty_Pct", "Source_URL"])
        df = df.loc[df["Reference_Period"].notna()].copy()
        df["Reference_Period"] = df["Reference_Period"].astype(str).str.strip()
        df["Financial_Difficulty_Pct"] = pd.to_numeric(
            df["Financial_Difficulty_Pct"], errors="coerce"
        )
        bad = df["Financial_Difficulty_Pct"].dropna()
        if not bad.between(0, 100).all():
            raise ValueError(f"Out-of-range published percentage in {sheet_name}")
        geography_key = "CMA" if sheet_name == "04B CMA" else "Geography"
        ensure_unique(df, ["Reference_Period", geography_key, "Age_Group"])
        df["Source_Type"] = "Researcher-compiled from published official figures"
        df["Observation_Available"] = df["Financial_Difficulty_Pct"].notna()
        output = write_table(df, output_name)
        qa = summary(df, source=src, output=output)
        qa["source_sheet"] = sheet_name
        qa["missing_published_values"] = int(df["Financial_Difficulty_Pct"].isna().sum())
        qa["note"] = (
            "The early monthly series includes all ages, while the later October "
            "series is 15+. Keep them separate. Do not fill missing periods with zero."
        )
        write_report(output_name.replace("_Tableau.csv", "_QA"), qa)
        print(f"04B {sheet_name}: {len(df)} rows -> {output.name}")


if __name__ == "__main__":
    main()
