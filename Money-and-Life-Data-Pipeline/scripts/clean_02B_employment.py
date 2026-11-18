"""02B: employment. Keep thousands-of-persons and rate measures separate."""
from common import (
    load_csv, must_have, add_statcan_value, ensure_unique,
    month_start, write_table, write_report, summary,
)

SOURCE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1410001701"


def main() -> None:
    raw, src, raw_count = load_csv("02B*.csv")
    must_have(raw, ["REF_DATE", "GEO", "Labour force characteristics", "Gender",
                    "Age group", "UOM", "VALUE", "STATUS", "VECTOR"])
    df = add_statcan_value(raw)
    df = df.rename(columns={
        "Labour force characteristics": "Labour_Force_Measure",
        "Age group": "Age_Group", "UOM": "Unit", "VECTOR": "Vector_ID"
    })
    df["Month_Start"] = month_start(df["REF_DATE"])
    df["Measurement_Type"] = df["Unit"].map(
        lambda x: "Rate" if x.lower() in {"percent", "percentage"} else "Number of persons"
    )
    df["Source_Table"] = "14-10-0017-01"
    df["Source_URL"] = SOURCE
    cols = ["REF_DATE", "Month_Start", "GEO", "Gender", "Age_Group",
            "Labour_Force_Measure", "Measurement_Type", "Unit", "Value",
            "Value_Status", "Status", "Vector_ID", "Source_Table", "Source_URL"]
    out = df[cols].copy()
    ensure_unique(out, ["REF_DATE", "GEO", "Gender", "Age_Group", "Labour_Force_Measure"])
    output = write_table(out, "02B_Employment_Tableau.csv")
    qa = summary(out, source=src, output=output, original_rows=raw_count)
    qa["units"] = out["Unit"].value_counts().to_dict()
    qa["note"] = "Never put counts in thousands and percentage rates on one numeric axis without separating units."
    write_report("02B_Employment_QA", qa)
    print(f"02B: {len(out)} records -> {output.name}")


if __name__ == "__main__":
    main()
