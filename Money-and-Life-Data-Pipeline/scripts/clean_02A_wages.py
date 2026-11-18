"""02A: monthly wages. Keep work type, age, nominal dollars and source units."""
from common import (
    load_csv, must_have, add_statcan_value, ensure_unique,
    month_start, write_table, write_report, summary,
)

SOURCE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410006301"


def main() -> None:
    raw, src, raw_count = load_csv("02A.csv")
    fields = [
        "REF_DATE", "GEO", "Wages", "Type of work",
        "North American Industry Classification System (NAICS)",
        "Gender", "Age group", "UOM", "VALUE", "STATUS", "VECTOR"
    ]
    must_have(raw, fields)
    df = add_statcan_value(raw)
    renames = {
        "Wages": "Wage_Measure", "Type of work": "Work_Type",
        "North American Industry Classification System (NAICS)": "Industry",
        "Age group": "Age_Group", "Gender": "Gender", "UOM": "Unit",
        "VECTOR": "Vector_ID"
    }
    df = df.rename(columns=renames)
    df["Month_Start"] = month_start(df["REF_DATE"])
    df["Source_Table"] = "14-10-0063-01"
    df["Source_URL"] = SOURCE
    cols = ["REF_DATE", "Month_Start", "GEO", "Age_Group", "Gender",
            "Wage_Measure", "Work_Type", "Industry", "Unit", "Value",
            "Value_Status", "Status", "Vector_ID", "Source_Table", "Source_URL"]
    out = df[cols].copy()
    ensure_unique(out, ["REF_DATE", "GEO", "Age_Group", "Gender",
                        "Wage_Measure", "Work_Type", "Industry"])
    output = write_table(out, "02A_Wages_Tableau.csv")
    qa = summary(out, source=src, output=output, original_rows=raw_count)
    qa["note"] = "Current dollars are nominal wages. Do not treat this as real wage growth."
    write_report("02A_Wages_QA", qa)
    print(f"02A: {len(out)} records -> {output.name}")


if __name__ == "__main__":
    main()
