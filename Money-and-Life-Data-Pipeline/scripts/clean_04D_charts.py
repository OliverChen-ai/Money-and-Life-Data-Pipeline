"""04D: clean three 2024 Statistics Canada chart CSVs into one long table.

Each chart is a separate marginal breakdown. These are NOT joint age-income-
living-arrangement observations.
"""
from __future__ import annotations

import csv

import pandas as pd

from common import source_file, ensure_unique, write_table, write_report

CHARTS = {
    1: {"dimension": "Income quintile", "source": "https://www150.statcan.gc.ca/n1/daily-quotidien/240815/cg-b001-eng.htm"},
    2: {"dimension": "Age group", "source": "https://www150.statcan.gc.ca/n1/daily-quotidien/240815/cg-b002-eng.htm"},
    3: {"dimension": "Living arrangement", "source": "https://www150.statcan.gc.ca/n1/daily-quotidien/240815/cg-b003-eng.htm"},
}


def read_chart(number: int) -> tuple[pd.DataFrame, dict]:
    src = source_file(f"Chart {number}*.csv")
    with src.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if len(rows) < 6:
        raise ValueError(f"Chart {number} is too short")
    column_names = [name.strip() for name in rows[1]]
    if len(column_names) < 2 or column_names[0]:
        raise ValueError(f"Chart {number} age/income header not recognized")
    groups = column_names[1:]
    content = []
    notes = []
    for row in rows[2:]:
        if len(row) == len(column_names) and row[0].strip():
            indicator = row[0].strip()
            for group, raw in zip(groups, row[1:]):
                try:
                    value = float(raw)
                except ValueError as exc:
                    raise ValueError(f"Bad chart {number} value for {group}: {raw!r}") from exc
                if not 0 <= value <= 100:
                    raise ValueError(f"Chart {number} percentage outside 0–100: {value}")
                content.append({
                    "Survey_Year": 2024,
                    "Survey": "Canadian Social Survey, Wave 13",
                    "Source_Chart": number,
                    "Dimension_Type": CHARTS[number]["dimension"],
                    "Group_Label": group,
                    "Indicator": indicator,
                    "Value_Pct": value,
                    "Unit": "Percent",
                    "Source_URL": CHARTS[number]["source"],
                })
        elif row and row[0].strip():
            notes.append(row[0].strip())
    result = pd.DataFrame(content)
    if result.empty:
        raise ValueError(f"Chart {number} has no parsed measurements")
    ensure_unique(result, ["Source_Chart", "Group_Label", "Indicator"])
    qa = {
        "source_file": src.name,
        "data_rows": result["Indicator"].nunique(),
        "groups": len(groups),
        "measurements": len(result),
        "source_footnotes": notes,
        "note": "This is a separate group-wise summary, not a joint distribution."
    }
    return result, qa


def main() -> None:
    outputs = []
    qa = {}
    for num in (1, 2, 3):
        df, report = read_chart(num)
        file = write_table(df, f"04D_Chart{num}_Tableau.csv")
        outputs.append(df)
        qa[f"chart_{num}"] = report
        print(f"04D chart {num}: {len(df)} rows -> {file.name}")
    merged = pd.concat(outputs, ignore_index=True)
    write_table(merged, "04D_All_Three_Charts_Tableau.csv")
    qa["total_measurements"] = len(merged)
    qa["note"] = "Do not join age, income, and living arrangement to invent combined subgroups."
    write_report("04D_Rising_Prices_QA", qa)
    print(f"04D: {len(merged)} records across three separate marginal datasets")


if __name__ == "__main__":
    main()
