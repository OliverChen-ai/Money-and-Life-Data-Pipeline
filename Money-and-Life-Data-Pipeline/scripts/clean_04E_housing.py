"""04E: tenure and housing affordability. Keep x suppression and missing groups."""
from __future__ import annotations

import csv

import pandas as pd
from common import (
    source_file, load_csv, must_have, add_statcan_value,
    ensure_unique, write_table, write_report, summary,
)

SOURCE = "https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=4610008301"
AFFORDABILITY = "https://www150.statcan.gc.ca/n1/daily-quotidien/260921/t001a-eng.htm"


def tenure_chart(chart_number: int) -> dict:
    raw, src, original_rows = load_csv(f"04E-{chart_number}*.csv")
    must_have(raw, [
        "REF_DATE", "GEO", "Tenure including first-time homebuyer status",
        "Select household characteristics", "Statistics", "UOM", "VALUE", "STATUS"
    ])
    df = add_statcan_value(raw).rename(columns={
        "Tenure including first-time homebuyer status": "Tenure",
        "Select household characteristics": "Household_Characteristic",
        "Statistics": "Statistics", "UOM": "Unit", "VECTOR": "Vector_ID"
    })
    df["Source_Table"] = "46-10-0083-01"
    df["Source_URL"] = SOURCE
    cols = ["REF_DATE", "GEO", "Tenure", "Household_Characteristic",
            "Statistics", "Unit", "Value", "Value_Status", "Status",
            "Vector_ID", "Source_Table", "Source_URL"]
    out = df[cols].copy()
    ensure_unique(out, ["REF_DATE", "GEO", "Tenure", "Household_Characteristic", "Statistics"])
    name = f"04E_{chart_number}_Housing_Tableau.csv"
    output = write_table(out, name)
    qa = summary(out, source=src, output=output, original_rows=original_rows)
    qa["note"] = (
        "x is a confidentiality suppression, never zero. Some official combinations "
        "are absent entirely. Age is of the household reference person."
    )
    write_report(f"04E_{chart_number}_Housing_QA", qa)
    print(f"04E-{chart_number}: {len(out)} rows -> {name}")
    return qa


def affordability_table() -> dict:
    src = source_file("04E_3*.csv")
    with src.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    # Official chart has a title row, then the actual years on row 2.
    years = [s.strip().replace("\u00a0", "") for s in rows[1][1:]]
    if years != ["2018", "2021", "2022", "2024"]:
        raise ValueError(f"Unexpected years in affordability figure: {years}")
    data = []
    for row in rows[3:]:
        if len(row) != len(years) + 1 or not row[0].strip():
            continue
        group = row[0].strip()
        for year, raw in zip(years, row[1:]):
            value = float(raw)
            if not 0 <= value <= 100:
                raise ValueError(f"Out-of-range affordability estimate: {group} {year}")
            data.append({
                "Reference_Year": year,
                "Geography": "Canada",
                "Housing_Category": group,
                "Shelter_Cost_At_Least_30Pct_Income": value,
                "Unit": "Percent of households",
                "Survey": "Canadian Housing Survey",
                "Source_URL": AFFORDABILITY,
            })
    df = pd.DataFrame(data)
    ensure_unique(df, ["Reference_Year", "Housing_Category"])
    output = write_table(df, "04E_3_Housing_Affordability_Tableau.csv")
    qa = {
        "source_file": src.name,
        "rows_in_output": len(df),
        "housing_categories": df["Housing_Category"].nunique(),
        "years": years,
        "note": "The category hierarchy overlaps. Do not add owners to owner subtypes or renters to rental subtypes."
    }
    write_report("04E_3_Affordability_QA", qa)
    print(f"04E-3: {len(df)} rows -> {output.name}")
    return qa


def main() -> None:
    tenure_chart(1)
    tenure_chart(2)
    affordability_table()


if __name__ == "__main__":
    main()
