"""The package (src/exchange_trading_days) against the CSVs in data/. Standard library only.

    python -m unittest tests.test_package -v
"""
import csv
import os
import sys
import unittest
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import exchange_trading_days as etd  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


class Package(unittest.TestCase):
    def test_counts_match_trading_hours(self):
        with open(os.path.join(DATA, "trading_hours.csv"), newline="") as f:
            for r in csv.DictReader(f):
                for y in etd.YEARS:
                    self.assertEqual(etd.trading_days_between(r["mic"], f"{y}-01-01", f"{y}-12-31"),
                                     int(r[f"trading_days_{y}"]), (r["mic"], y))

    def test_rows(self):
        with open(os.path.join(DATA, "exchange_holidays_2026_2028.csv"), newline="") as f:
            for r in csv.DictReader(f):
                if r["status"] == "closed":
                    self.assertFalse(etd.is_trading_day(r["mic"], r["date"]))
                    self.assertIsNone(etd.close_time(r["mic"], r["date"]))
                else:
                    self.assertEqual(etd.close_time(r["mic"], r["date"]), r["close_local"])

    def test_examples(self):
        self.assertFalse(etd.is_trading_day("XLON", "2026-12-28"))
        self.assertEqual(etd.add_trading_days("XTKS", "2026-12-30", 1), date(2027, 1, 4))
        self.assertEqual(etd.close_time("xnys", "2026-11-27"), "13:00")
        self.assertEqual(etd.previous_trading_day("XNYS", "2026-07-06"), date(2026, 7, 2))
        self.assertIn((date(2026, 12, 25), "Christmas Day"), etd.holidays("XLON", 2026))
        with self.assertRaises(etd.NotCovered):
            etd.is_trading_day("XLON", "2029-01-02")
        with self.assertRaises(KeyError):
            etd.is_trading_day("XXXX", "2026-01-02")
        self.assertEqual(etd.cli(["XLON", "2030-01-02"]), 1)


if __name__ == "__main__":
    unittest.main()
