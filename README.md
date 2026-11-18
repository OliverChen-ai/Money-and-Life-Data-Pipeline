# Money & Life: Data Pipeline

This is a Python project for my data visualization class at Sheridan College.

I collected public data from Statistics Canada and the Bank of Canada. I wanted to make the data easier to clean, check and use in Tableau.

I used Tableau and Excel for some datasets. For the other files, I used Python to organize the data and check for problems.

## 1. Project Structure

I organized the project into separate folders to keep everything clear.

- `data_raw/` stores the original data.
- `scripts/` contains the Python code.
- `data_clean/` stores the cleaned CSV files.
- `qa/` stores the data quality reports.
- `documentation/` explains the files and methods.
- `tests/` contains checks for the outputs.

I also created `common.py` to share functions between scripts. This helps avoid writing the same code again.

The `run_all.py` file runs the main scripts in order.

## 2. How the Code Works

I followed five main steps.

1. **Read:** Open the original CSV or Excel file.
2. **Inspect:** Check dates, categories, data types and missing values.
3. **Clean:** Rename columns, organize the data and change its structure when needed.
4. **Validate:** Check for duplicates, missing values and other possible problems.
5. **Export:** Save the cleaned data and quality reports.

I kept the original data unchanged. Missing values were not replaced with zero.

## 3. Python Knowledge I Used

I used `pandas` to work with tables, `csv` to read files and `pathlib` to manage file paths.

I also worked with functions, loops, dictionaries and conditional statements.

Functions helped me separate different tasks. Loops helped process repeated records. Dictionaries helped connect data codes to their descriptions.

I used validation checks to catch problems before exporting the final data.

## 4. Example: Bank of Canada Data

One example is the financial well-being dataset.

The original CSV contains two important sections called `SERIES` and `OBSERVATIONS`.

I used Python to read these sections and match the data codes with their descriptions.

Then I changed the data from a wide table into a long table for Tableau.

I also checked the age groups, missing values and duplicate records.

This helped me understand how to work with datasets that have more complicated structures.

## 5. How to Run

Open the project folder in VS Code and put the original data files in `data_raw/`.

If you downloaded the whole GitHub repository, first open the inner project folder:

```bash
cd Money-and-Life-Data-Pipeline
```

Then run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/run_all.py
```

To run the output checks:

```bash
python -m unittest discover -s tests -v
```

The cleaned CSV files will be saved in `data_clean/`.

## 6. What I Learned

This project helped me connect my programming knowledge with data visualization.

I learned how to organize a larger set of data files, build reusable code and check the results before using them.

I also wanted to keep the code flexible so I can use the same framework with other datasets in the future.

## Data Sources

- [Statistics Canada](https://www.statcan.gc.ca/)
- [Bank of Canada](https://www.bankofcanada.ca/)

This repository contains the code and documentation for my class project.
