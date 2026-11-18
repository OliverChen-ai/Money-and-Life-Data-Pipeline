"""Small helpers shared by the Money & Life dataset scripts.

All transformations write new files. Raw data is never changed.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data_raw"
CLEAN = ROOT / "data_clean"
QA = ROOT / "qa"
DOCS = ROOT / "documentation"


def make_dirs() -> None:
    for folder in (RAW, CLEAN, QA, DOCS):
        folder.mkdir(parents=True, exist_ok=True)


def source_file(pattern: str) -> Path:
    """Find exactly one original local file matching a simple filename pattern."""
    found = sorted(RAW.glob(pattern))
    if len(found) != 1:
        raise FileNotFoundError(
            f"Expected one file matching '{pattern}' inside {RAW}, found {len(found)}. "
            "Copy the original download there and keep its filename."
        )
    return found[0]


def load_csv(pattern: str) -> tuple[pd.DataFrame, Path, int]:
    """Load a normal Statistics Canada CSV, retaining original text and flags."""
    src = source_file(pattern)
    df = pd.read_csv(src, dtype=str, encoding="utf-8-sig", keep_default_na=False)
    original_rows = len(df)
    if "REF_DATE" in df:
        # Official downloads may end with blank lines. Do not keep blank dates.
        df = df.loc[df["REF_DATE"].str.strip().ne("")].copy()
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df, src, original_rows


def must_have(df: pd.DataFrame, fields: list[str]) -> None:
    missing = sorted(set(fields) - set(df.columns))
    if missing:
        raise ValueError(f"Source does not have required columns: {missing}")


def ensure_unique(df: pd.DataFrame, keys: list[str]) -> None:
    count = int(df.duplicated(subset=keys).sum())
    if count:
        examples = df[df.duplicated(subset=keys, keep=False)][keys].head(3)
        raise ValueError(f"Found {count} duplicate observation keys:\n{examples}")


def add_statcan_value(df: pd.DataFrame) -> pd.DataFrame:
    """Keep source VALUE as text, make separate numeric Value, never fill missing."""
    must_have(df, ["VALUE", "STATUS"])
    result = df.copy()
    result["Value_Original"] = result["VALUE"]
    result["Value"] = pd.to_numeric(result["VALUE"], errors="coerce")
    invalid = result["VALUE"].ne("") & result["Value"].isna()
    if invalid.any():
        raise ValueError("Non-empty official VALUE could not be parsed as a number")
    result["Value_Status"] = "Available"
    result.loc[result["Value"].isna(), "Value_Status"] = "Missing in source"
    result.loc[
        result["Value"].isna() & result["STATUS"].str.lower().eq("x"),
        "Value_Status"
    ] = "Suppressed in source"
    result["Status"] = result["STATUS"]
    return result


def month_start(date_column: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(date_column, format="%Y-%m", errors="raise")
    return parsed.dt.strftime("%Y-%m-%d")


def quarter_from_month(date_column: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(date_column, format="%Y-%m", errors="raise")
    if not parsed.dt.month.isin([1, 4, 7, 10]).all():
        raise ValueError("Expected dates at the start of each quarter")
    return parsed.dt.year.astype(str) + "Q" + parsed.dt.quarter.astype(str)


def write_table(df: pd.DataFrame, filename: str) -> Path:
    make_dirs()
    path = CLEAN / filename
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def write_report(name: str, details: dict) -> Path:
    make_dirs()
    path = QA / f"{name}.json"
    path.write_text(json.dumps(details, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    return path


def summary(df: pd.DataFrame, *, source: Path, output: Path, original_rows: int | None = None) -> dict:
    report = {
        "source_filename": source.name,
        "cleaned_filename": output.name,
        "rows_in_output": len(df),
        "columns_in_output": len(df.columns),
        "no_missing_values_were_imputed": True,
    }
    if original_rows is not None:
        report["rows_after_csv_read"] = original_rows
        report["rows_removed_for_blank_REF_DATE"] = original_rows - len(df)
    if "Value" in df:
        report["missing_values_in_output"] = int(df["Value"].isna().sum())
    if "Status" in df:
        report["nonempty_status_flags"] = df.loc[df["Status"].ne(""), "Status"].value_counts().to_dict()
    if "REF_DATE" in df:
        report["first_period"] = df["REF_DATE"].min()
        report["last_period"] = df["REF_DATE"].max()
    return report
