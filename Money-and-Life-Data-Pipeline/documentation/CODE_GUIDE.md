# Code Guide

## The basic logic

1. **Read** the original CSV or Excel file without changing it.
2. **Inspect** the dates, groups, metrics, units and data flags.
3. **Reshape** only when it makes the file easier to analyze.
4. **Validate** duplicates, data types and missing or suppressed values.
5. **Export** a new CSV for Tableau and save a QA report.

## Which script handles which data?

| Script | Input | Main task |
| --- | --- | --- |
| `clean_02A_wages.py` | 02A wage CSV | Check wages, age and work type. Keep nominal dollars. |
| `clean_02B_employment.py` | Updated 02B CSV | Keep rates separate from counts in thousands. |
| `clean_03_rent.py` | 03 rent CSV | Keep CMA and apartment type, preserve `E` flags. |
| `validate_04B.py` | 04B workbook | Export the three source-compiled sheets separately. |
| `clean_04C_C15.py` | Bank of Canada C15 | Featured example. Parse metadata and quarters. |
| `clean_04C_bankofcanada.py` | Five `CES_*` CSVs | Parse all five charts and keep original labels. |
| `clean_04D_charts.py` | Three Chart CSVs | Move four indicator rows into long format. |
| `clean_04E_housing.py` | Three housing files | Keep renter/owner groups, suppressed values and confidence intervals. |
| `run_all.py` | All inputs | Execute each module in sequence. |

Run just the featured case:

```bash
python scripts/inspect_04C.py
python scripts/inspect_04C_structure.py
python scripts/clean_04C_C15.py
python scripts/verify_04C.py
```

Run all modules:

```bash
python scripts/run_all.py
```

## Important limits

- CPI (01) was cleaned in Tableau. Financial difficulty (04A) was cleaned in Excel. Neither is processed again here.
- The three 04B sheets were compiled from official releases. They are not direct exports from one StatCan table.
- Bank of Canada C15 financial well-being scores are **not percentages**.
- The age group **25–54** is not the same as **25–34**.
- The three 04D chart datasets are separate marginal summaries, not joint demographic data.
- Empty, suppressed and absent data must not become zero.
- For 03, an `E` quality flag is kept, not deleted.
- For 04E, an `x` suppression flag and missing combinations are kept as unavailable.

Data sources: Statistics Canada and Bank of Canada. Original source links are also stored in the cleaned CSVs.
