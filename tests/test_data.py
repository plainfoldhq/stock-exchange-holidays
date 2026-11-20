"""Check the CSVs against libraries other than the one they were exported from (exchange_calendars).

    pip install holidays pandas_market_calendars
    python -m unittest discover -s tests -v
"""
import csv
import os
import unittest
import warnings
from collections import defaultdict
from datetime import date

warnings.filterwarnings("ignore")
import holidays  # noqa: E402

DATA = os.path.join(os.path.dirname(__file__), "..", "data")
HCODE = {"XNYS": "XNYS", "XLON": "XLON", "XTSE": "XTSE", "XETR": "XETR", "XPAR": "XPAR", "XTKS": "XJPX",
         "XHKG": "XHKG", "XASX": "XASX", "XSWX": "XSWX"}
YEARS = (2026, 2027, 2028)


def load():
    with open(os.path.join(DATA, "exchange_holidays_2026_2028.csv"), newline="") as f:
        return list(csv.DictReader(f))


class Closures(unittest.TestCase):
    def test_closed_days_match_holidays_package(self):
        got = defaultdict(set)
        for r in load():
            if r["status"] == "closed":
                d = date.fromisoformat(r["date"])
                self.assertLess(d.weekday(), 5, r)
                got[(r["mic"], d.year)].add(d)
        for mic, h in HCODE.items():
            for y in YEARS:
                ref = {d for d in holidays.financial_holidays(h, years=y) if d.weekday() < 5}
                self.assertEqual(got[(mic, y)], ref, (mic, y))

    def test_early_closes_match_pandas_market_calendars(self):
        import pandas_market_calendars as pmc
        got = defaultdict(set)
        for r in load():
            if r["status"] == "early_close":
                got[(r["mic"], int(r["date"][:4]))].add((r["date"], r["close_local"]))
        for mic, name in {"XNYS": "NYSE", "XLON": "LSE", "XTSE": "TSX", "XASX": "ASX"}.items():
            c = pmc.get_calendar(name)
            for y in YEARS:
                s = c.schedule(f"{y}-01-01", f"{y}-12-31")
                ref = {(str(d.date()), t.tz_convert(c.tz).strftime("%H:%M")) for d, t in c.early_closes(s)["market_close"].items()}
                self.assertEqual(got[(mic, y)], ref, (mic, y))

    def test_trading_day_counts(self):
        closed = defaultdict(int)
        for r in load():
            if r["status"] == "closed":
                closed[(r["mic"], int(r["date"][:4]))] += 1
        with open(os.path.join(DATA, "trading_hours.csv"), newline="") as f:
            for r in csv.DictReader(f):
                for y in YEARS:
                    weekdays = sum(1 for o in range(366) if (d := date.fromordinal(date(y, 1, 1).toordinal() + o)).year == y
                                   and d.weekday() < 5)
                    self.assertEqual(int(r[f"trading_days_{y}"]), weekdays - closed[(r["mic"], y)], (r["mic"], y))


if __name__ == "__main__":
    unittest.main()
