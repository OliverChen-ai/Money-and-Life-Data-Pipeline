# Money & Life — Data Pipeline

This is a small Python project for my data visualization class at Sheridan College.

I collected public data from Statistics Canada and the Bank of Canada. These scripts help check the files, organize the data and export CSVs for Tableau. Missing values stay missing.

I used Tableau for CPI data and Excel for one financial difficulty dataset. Python helps with the other files, especially the ones with unusual layouts.

## How to run

1. Install Python and open this folder in VS Code.
2. Put the original downloaded files in `data_raw/`.
3. Open a terminal and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/run_all.py
```

Cleaned CSVs go to `data_clean/`. Data checks go to `qa/`.

I kept the scripts separate so I can reuse this setup with other datasets in the future.

**Sources:** [Statistics Canada](https://www.statcan.gc.ca/) and [Bank of Canada](https://www.bankofcanada.ca/).
