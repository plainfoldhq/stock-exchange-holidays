# Stock exchange holidays and trading days in Python

This guide shows how to check whether a stock exchange is open on a date, find the next or previous trading day, add N trading days, count trading days between two dates and read early-close times, using the free `exchange-trading-days` package. It uses only the standard library and covers nine exchanges for 2026-2028.

```
pip install exchange-trading-days
```

All output below was produced with `exchange-trading-days` 0.1.1 and `exchange_calendars` 4.13.3 on 2026-11-28.

## Is the exchange open on this date?

Exchanges are named by ISO 10383 MIC: XNYS (NYSE), XLON (London), XTSE (Toronto), XETR (Xetra/Frankfurt), XPAR (Euronext Paris, Amsterdam, Brussels), XTKS (Tokyo), XHKG (Hong Kong), XASX (Australia), XSWX (SIX Swiss).

```python
import exchange_trading_days as etd

print(etd.EXCHANGES)
print(etd.YEARS)
print(etd.is_trading_day("XNYS", "2026-11-26"))
print(etd.is_trading_day("XLON", "2026-12-28"))
print(etd.is_trading_day("XNYS", "2026-11-28"))
```

```
('XNYS', 'XLON', 'XTSE', 'XETR', 'XPAR', 'XTKS', 'XHKG', 'XASX', 'XSWX')
(2026, 2027, 2028)
False
False
False
```

Dates can be `datetime.date` objects or ISO strings. The three checks are Thanksgiving, Boxing Day (observed on a Monday) and a Saturday.

## Next, previous, and add N trading days

```python
import exchange_trading_days as etd

print(etd.next_trading_day("XNYS", "2026-11-25"))
print(etd.previous_trading_day("XNYS", "2026-11-30"))
print(etd.add_trading_days("XTKS", "2026-12-30", 1))
print(etd.add_trading_days("XNYS", "2026-11-28", 0))
```

```
2026-11-27
2026-11-27
2027-01-04
2026-11-30
```

Thanksgiving is skipped, and so is Tokyo's closure on Dec 31 and Jan 1 (Jan 2-3 2027 is a weekend). A negative `n` moves backwards. With `n = 0`, a non-trading day rolls forward (Saturday Nov 28 becomes Monday Nov 30).

## Count trading days between two dates

```python
import exchange_trading_days as etd

print(etd.trading_days_between("XNYS", "2026-11-01", "2026-11-30"))
print(etd.trading_days_between("XNYS", "2026-11-30", "2026-11-01"))
print(etd.trading_days_between("XNYS", "2026-01-01", "2026-12-31"))
print(etd.trading_days_between("XLON", "2026-12-21", "2026-12-31"))
```

```
20
0
251
7
```

Both ends are included (`start <= day <= end`). If the end is before the start the result is 0, not negative. The last two lines are NYSE's 251 days in 2026 and London's 7 days in the Christmas week.

## Early closes and holiday lists

```python
import exchange_trading_days as etd

print(etd.close_time("XNYS", "2026-11-27"))
print(etd.close_time("XNYS", "2026-11-26"))
print(etd.close_time("XLON", "2026-12-24"))
print(etd.holidays("XLON", 2026)[-2:])
```

```
13:00
None
12:30
[(datetime.date(2026, 12, 25), 'Christmas Day'), (datetime.date(2026, 12, 28), 'Boxing Day (observed)')]
```

`close_time` returns the local close as `HH:MM`, early closes included, and `None` on a closed day. `holidays(mic, year)` lists weekday closures only; holidays on a weekend are not listed. The command line does the same check: `python -m exchange_trading_days XLON 2026-12-24` prints `trading, closes 12:30 local`.

## Compare: exchange_calendars and a naive weekday count

`exchange_calendars` is the larger open-source library (it needs pandas) that this package's data is exported from; it covers more exchanges and gives session times in UTC. `numpy.busday_count` without a holiday list is the naive weekday count.

```python
import numpy as np
import exchange_calendars as xcals
import exchange_trading_days as etd

xnys = xcals.get_calendar("XNYS", end="2028-12-31")
xlon = xcals.get_calendar("XLON", end="2028-12-31")
xtks = xcals.get_calendar("XTKS", end="2028-12-31")

# 1. Trading days in November 2026 (NYSE)
print(len(xnys.sessions_in_range("2026-11-01", "2026-11-30")),
      etd.trading_days_between("XNYS", "2026-11-01", "2026-11-30"),
      np.busday_count("2026-11-01", "2026-12-01"))

# 2. London, 21-31 Dec 2026
print(len(xlon.sessions_in_range("2026-12-21", "2026-12-31")),
      etd.trading_days_between("XLON", "2026-12-21", "2026-12-31"),
      np.busday_count("2026-12-21", "2027-01-01"))

# 3. Next Tokyo session after 30 Dec 2026
print(xtks.date_to_session("2026-12-31", direction="next").date(),
      etd.next_trading_day("XTKS", "2026-12-30"))

# 4. Early close (exchange_calendars gives UTC; convert to local time)
print(xnys.session_close("2026-11-27").tz_convert("America/New_York").strftime("%H:%M"),
      etd.close_time("XNYS", "2026-11-27"))
```

```
20 20 21
7 7 9
2027-01-04 2027-01-04
13:00 13:00
```

The four lines are: NYSE trading days in November 2026 (`exchange_calendars`, this package, naive weekdays); London, Dec 21-31 2026; the next Tokyo session after Dec 30 (a naive "next weekday" gives Dec 31, which is closed); and the NYSE close the day after Thanksgiving. The naive count is off by one in November (Thanksgiving) and by two in the London week (Christmas Day and Boxing Day).

To compare every day of the bundled range for all nine exchanges:

```python
from datetime import date, timedelta
import exchange_calendars as xcals
import exchange_trading_days as etd

checked = diffs = 0
for mic in etd.EXCHANGES:
    cal = xcals.get_calendar(mic, end="2028-12-31")
    sessions = {s.date() for s in cal.sessions_in_range("2026-01-01", cal.last_session)}
    d = date(2026, 1, 1)
    while d <= date(2028, 12, 31):
        checked += 1
        diffs += etd.is_trading_day(mic, d) != (d in sessions)
        d += timedelta(days=1)
print(checked, "exchange-days checked,", diffs, "differences")
```

```
9864 exchange-days checked, 0 differences
```

`exchange_calendars` builds a calendar only up to a limit that defaults to about a year ahead, so pass `end=` for later years.

## Limits

- Covered years are 2026, 2027 and 2028. Any other year raises `NotCovered` (a `ValueError` subclass); the package does not guess. An unknown exchange raises `KeyError`.

```python
import exchange_trading_days as etd

for mic, d in (("XNYS", "2029-01-02"), ("XBOM", "2026-11-26")):
    try:
        etd.is_trading_day(mic, d)
    except Exception as e:
        print(type(e).__name__, "-", e)
```

```
NotCovered - 2029 is not covered (bundled: 2026-2028)
KeyError - 'unknown exchange XBOM; available: XNYS, XLON, XTSE, XETR, XPAR, XTKS, XHKG, XASX, XSWX'
```

- Future dates follow each exchange's standing rules. Exchanges publish an official schedule each year and can add closures (weather, typhoon signals, days of mourning). Check the exchange's notice before trading or settlement use.
- Settlement and clearing holidays can differ from trading holidays. Regular hours exclude pre-opening and closing auctions.

## Full pack: 24 exchanges, 2000-2050

The [World Stock Exchange Holidays + Trading Hours pack](https://buy.polar.sh/polar_cl_8VwWMpQhsLCYXsPRdkmYGjbJzuzlHQB9Ul3GC3dlJW7?utm_source=github&utm_medium=readme&utm_campaign=G&utm_content=stock-exchange-holidays) ($15, one-time; Polar is the merchant of record and handles sales tax) covers 24 exchanges. It adds Mexico, B3, Euronext Dublin/Lisbon/Oslo, Borsa Italiana, Frankfurt, Madrid, Warsaw, Istanbul, Johannesburg, Korea (2001-2025 only) and NZX, and gives Euronext Amsterdam and Brussels their own calendars. It covers every year 2000-2050 in which `exchange_calendars` and `holidays` agree on every weekday (930 exchange-years; the rest are listed as not covered, with the reason). It includes:

- every trading session with local and UTC open/close, early closes and late opens
- SQLite, JSON, .ics files and a tested PostgreSQL loader
- a standard-library trading-day helper

It is also in the [All-Access yearly plan](https://buy.polar.sh/polar_cl_xydfuofU72fdp6xSOHFtihAuniUFagYOwR9zf2M03Gl?utm_source=github&utm_medium=readme&utm_campaign=ALLACCESS&utm_content=stock-exchange-holidays) with every Plainfold data pack. Details: [README](../README.md#full-pack-24-exchanges-2000-2050).

---

Made by Plainfold. Written with AI assistance. Not investment advice; check the exchange's official notices.
