"""Small reproducibility checks after running `python scripts/run_all.py`.

Run: python -m unittest discover -s tests -v
"""
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data_clean"


class PipelineOutputTests(unittest.TestCase):
    @unittest.skipUnless((CLEAN / "04C_C15_2019Q1_2026Q3.csv").exists(), "Run the pipeline first")
    def test_c15_age_and_uniqueness(self):
        df = pd.read_csv(CLEAN / "04C_C15_2019Q1_2026Q3.csv")
        age = df[df["Segment_Type"] == "Age group"]
        self.assertEqual(age["Series_ID"].nunique(), 6)
        self.assertEqual(int(age["Age_Group"].isna().sum()), 0)
        self.assertEqual(int(df.duplicated(["Quarter", "Series_ID"]).sum()), 0)
        self.assertIn("25-54", set(age["Age_Group"].dropna()))
        self.assertNotIn("25-34", set(age["Age_Group"].dropna()))

    @unittest.skipUnless((CLEAN / "03_Rent_Tableau.csv").exists(), "Run the pipeline first")
    def test_rent_keeps_quality_flags(self):
        df = pd.read_csv(CLEAN / "03_Rent_Tableau.csv", keep_default_na=False)
        self.assertIn("Status", df.columns)
        self.assertIn("E", set(df["Status"]))
        self.assertEqual(int(df.duplicated(["REF_DATE", "GEO", "Rental_Unit_Type", "Rent_Measure"]).sum()), 0)

    @unittest.skipUnless((CLEAN / "04E_1_Housing_Tableau.csv").exists(), "Run the pipeline first")
    def test_housing_suppression_kept(self):
        df = pd.read_csv(CLEAN / "04E_1_Housing_Tableau.csv", keep_default_na=False)
        suppressed = df[df["Status"].str.lower().eq("x")]
        self.assertGreater(len(suppressed), 0)
        self.assertTrue(suppressed["Value"].astype(str).eq("").all())

    @unittest.skipUnless((CLEAN / "04D_All_Three_Charts_Tableau.csv").exists(), "Run the pipeline first")
    def test_chart_dimensions_remain_separate(self):
        df = pd.read_csv(CLEAN / "04D_All_Three_Charts_Tableau.csv")
        self.assertEqual(set(df["Dimension_Type"]), {"Income quintile", "Age group", "Living arrangement"})
        self.assertTrue(df["Value_Pct"].between(0, 100).all())


if __name__ == "__main__":
    unittest.main()
