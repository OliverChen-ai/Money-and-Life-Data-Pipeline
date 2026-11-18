"""04C: parse Bank of Canada CSVs with SERIES and OBSERVATIONS sections.

Use official series labels. Never assume 25–54 is the same as 25–34.
Outputs are long-form CSVs with explicit gaps, metadata and QA reports.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

import pandas as pd
from common import RAW, CLEAN, DOCS, QA, make_dirs, write_table, write_report, source_file

CHARTS = ("C15", "C12", "C5", "C11", "C8")
SEGMENTS = {
    "": "All respondents", "A": "Age group", "B": "Education",
    "C": "Household income", "D": "Numeracy", "E": "Geography",
    "F": "Other demographic group", "G": "Housing tenure",
    "H": "Newcomer status"
}


def find_section(rows: list[list[str]], name: str) -> int:
    matching = [i for i, row in enumerate(rows) if row and row[0].strip() == name]
    if len(matching) != 1:
        raise ValueError(f"Expected one {name} section, found {len(matching)}")
    return matching[0]


def load_bank_file(src: Path):
    """Split a Bank of Canada export into metadata, series and observation rows."""
    with src.open("r", newline="", encoding="utf-8-sig") as f:
        lines = list(csv.reader(f))
    s = find_section(lines, "SERIES")
    o = find_section(lines, "OBSERVATIONS")
    if not (s < o):
        raise ValueError("SERIES must precede OBSERVATIONS")
    series_columns = lines[s + 1]
    metadata = {}
    for row in lines[s + 2:o]:
        if row and row[0].strip():
            info = dict(zip(series_columns, row))
            code = info.get("id")
            if not code or code in metadata:
                raise ValueError(f"Missing/duplicate series code: {code}")
            metadata[code] = info
    obs_columns = lines[o + 1]
    if obs_columns[0] != "date" or len(obs_columns) != len(set(obs_columns)):
        raise ValueError("Observation header lacks date or includes duplicates")
    if set(obs_columns[1:]) != set(metadata):
        raise ValueError("Series IDs in metadata and observations do not match")
    observations = [row for row in lines[o + 2:] if row]
    for row in observations:
        if len(row) != len(obs_columns):
            raise ValueError(f"Bad observation row length: {row[:3]}")
    return metadata, series_columns, obs_columns, observations


def explain_series(code: str, label: str) -> dict:
    """Use ID to identify the demographic dimension, but keep official full label."""
    m = re.match(r"^CES_C\d+([A-H]?)_", code)
    if not m:
        return {"Segment_Type": "Other", "Group_Label": "", "Age_Group": ""}
    subgroup = m.group(1)
    kind = SEGMENTS.get(subgroup, "Other")
    group = label.rsplit(", ", 1)[-1].strip() if subgroup and ", " in label else "All respondents"
    age = ""
    if subgroup == "A":
        age_match = re.search(r"(18\s*[-–]\s*24|25\s*[-–]\s*54|55\+)", label)
        age = re.sub(r"\s+", "", age_match.group(1)) if age_match else ""
        if not age:
            raise ValueError(f"Age label could not be read from official series: {code}: {label}")
        group = age
    return {"Segment_Type": kind, "Group_Label": group, "Age_Group": age}


def parse_chart(chart: str):
    if chart not in CHARTS:
        raise ValueError(f"Unsupported chart: {chart}")
    make_dirs()
    src = source_file(f"CES_{chart}_DEMOGRAPHICS.csv")
    meta, meta_header, col_header, rows = load_bank_file(src)
    ids = col_header[1:]
    records = []
    seen_quarters = set()
    for row in rows:
        quarter = row[0].strip()
        m = re.fullmatch(r"(\d{4})Q([1-4])", quarter)
        if not m or quarter in seen_quarters:
            raise ValueError(f"Bad or duplicate quarter: {quarter}")
        seen_quarters.add(quarter)
        year, q = map(int, m.groups())
        quarter_start = f"{year}-{3 * q - 2:02d}-01"
        for code, raw in zip(ids, row[1:]):
            raw = raw.strip()
            if raw:
                try:
                    val = float(raw)
                except ValueError as exc:
                    raise ValueError(f"Invalid numeric observation: {quarter} {code}={raw}") from exc
            else:
                val = None
            label = meta[code]["label"]
            detail = explain_series(code, label)
            question = (
                "Past 12 months" if "_PAST" in code else
                "Next 12 months" if "_FUTURE" in code else
                "See Series_Label"
            )
            records.append({
                "Quarter": quarter, "Quarter_Start_Date": quarter_start,
                "Source_Chart": chart, "Series_ID": code,
                "Series_Label": label, "Question": question,
                "Segment_Type": detail["Segment_Type"],
                "Group_Label": detail["Group_Label"],
                "Age_Group": detail["Age_Group"],
                "Value": val,
                "Value_Status": "Available" if val is not None else "Missing in source",
                "Source_File": src.name,
                "Source_URL": "https://www.bankofcanada.ca/publications/canadian-survey-of-consumer-expectations/canadian-survey-of-consumer-expectations-survey-data/",
            })
    df = pd.DataFrame.from_records(records)
    if df.duplicated(["Quarter", "Series_ID"]).any():
        raise ValueError("Duplicate quarter-series observations")
    if df["Series_ID"].nunique() != len(ids):
        raise ValueError("Some series missing from output")
    if df.loc[df["Segment_Type"].eq("Age group"), "Age_Group"].eq("").any():
        raise ValueError("Empty label in age series")
    historical = write_table(df, f"04C_{chart}_All_History.csv")
    study = df.loc[(df["Quarter"] >= "2019Q1") & (df["Quarter"] <= "2026Q3")].copy()
    filtered = write_table(study, f"04C_{chart}_2019Q1_2026Q3.csv")
    dictionary = pd.DataFrame([meta[c] for c in ids], columns=meta_header)
    dictionary.to_csv(DOCS / f"04C_{chart}_Series_Dictionary.csv", index=False, encoding="utf-8-sig")
    qa = {
        "source_file": src.name,
        "series": len(ids),
        "historical_quarters": df["Quarter"].nunique(),
        "study_quarters_present": study["Quarter"].nunique(),
        "historical_records": len(df),
        "study_records": len(study),
        "study_values_available": int(study["Value"].notna().sum()),
        "study_values_missing_in_source": int(study["Value"].isna().sum()),
        "duplicate_quarter_series": int(df.duplicated(["Quarter", "Series_ID"]).sum()),
        "missing_age_labels": int(df.loc[df["Segment_Type"].eq("Age group"), "Age_Group"].eq("").sum()),
        "missing_values_were_not_imputed": True,
        "note": "Series units vary. C15 financial well-being values are not percentages. Read source series descriptions."
    }
    # Keep known 2026 Q3 values as a regression check for the detailed class case.
    if chart == "C15":
        check = df.set_index(["Quarter", "Series_ID"])["Value"]
        assert abs(check.loc[("2026Q3", "CES_C15_PAST")] - (-0.17)) < 1e-9
        assert abs(check.loc[("2026Q3", "CES_C15_FUTURE")] - (-0.06)) < 1e-9
        (QA / "04C_C15_QA_Summary.txt").write_text(
            "\n".join(f"{key}: {val}" for key, val in qa.items()) + "\n", encoding="utf-8"
        )
    write_report(f"04C_{chart}_QA", qa)
    print(f"04C {chart}: {len(study)} study combinations, {qa['study_values_missing_in_source']} missing -> {filtered.name}")
    return qa


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean Bank of Canada CSV series")
    parser.add_argument("--topic", choices=[*CHARTS, "all"], default="all")
    args = parser.parse_args()
    for topic in CHARTS if args.topic == "all" else [args.topic]:
        parse_chart(topic)


if __name__ == "__main__":
    main()
