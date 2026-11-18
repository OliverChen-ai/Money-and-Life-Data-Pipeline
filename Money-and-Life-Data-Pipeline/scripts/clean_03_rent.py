"""03: asking/paid rent. Preserve unpublished combinations and E flags."""
from common import (
    load_csv, must_have, add_statcan_value, ensure_unique,
    month_start, quarter_from_month, write_table, write_report, summary,
)

SOURCE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=4610009201"


def main() -> None:
    raw, src, raw_count = load_csv("03.csv")
    must_have(raw, ["REF_DATE", "GEO", "Rental unit type", "Estimates", "UOM",
                    "VALUE", "STATUS", "VECTOR"])
    df = add_statcan_value(raw).rename(columns={
        "Rental unit type": "Rental_Unit_Type", "Estimates": "Rent_Measure",
        "UOM": "Unit", "VECTOR": "Vector_ID"
    })
    df["Quarter"] = quarter_from_month(df["REF_DATE"])
    df["Quarter_Start"] = month_start(df["REF_DATE"])
    df["Source_Table"] = "46-10-0092-01"
    df["Source_URL"] = SOURCE
    cols = ["REF_DATE", "Quarter", "Quarter_Start", "GEO", "Rental_Unit_Type",
            "Rent_Measure", "Unit", "Value", "Value_Status", "Status", "Vector_ID",
            "Source_Table", "Source_URL"]
    out = df[cols].copy()
    ensure_unique(out, ["REF_DATE", "GEO", "Rental_Unit_Type", "Rent_Measure"])
    output = write_table(out, "03_Rent_Tableau.csv")
    qa = summary(out, source=src, output=output, original_rows=raw_count)
    qa["published_series"] = out.groupby(["GEO", "Rental_Unit_Type", "Rent_Measure"]).size().to_dict()
    # JSON dictionaries need string keys. Rewrite this one for readability.
    qa["published_series"] = [
        {"GEO": g, "Rental_Unit_Type": u, "Rent_Measure": m, "observations": int(count)}
        for (g, u, m), count in out.groupby(["GEO", "Rental_Unit_Type", "Rent_Measure"]).size().items()
    ]
    qa["note"] = "No missing Hamilton paid-rent data was invented. E flags remain attached to values."
    write_report("03_Rent_QA", qa)
    print(f"03: {len(out)} records -> {output.name}")


if __name__ == "__main__":
    main()
