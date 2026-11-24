"""Stock exchange trading days, holidays and early closes for 9 exchanges, 2026-2028. Standard library only.

    >>> import exchange_trading_days as etd
    >>> etd.is_trading_day("XLON", "2026-12-28")       # Boxing Day (observed)
    False
    >>> etd.add_trading_days("XTKS", "2026-12-30", 1)  # Tokyo's year-end break
    datetime.date(2027, 1, 4)
    >>> etd.close_time("XNYS", "2026-11-27")          # day after Thanksgiving
    '13:00'

Exchanges (ISO 10383 MIC): XNYS (NYSE), XLON, XTSE, XETR, XPAR (Euronext Paris/Amsterdam/Brussels), XTKS, XHKG,
XASX, XSWX. Closures come from exchange_calendars and are checked against the independent `holidays` package;
early closes for NYSE, LSE, TSX and ASX against pandas_market_calendars. Outside 2026-2028 every function raises
NotCovered (it never guesses). Future dates follow standing rules: exchanges can add closures. Check the
exchange's notice before trading or settlement use. 24 exchanges 2000-2050: https://github.com/plainfoldhq/stock-exchange-holidays
"""
import csv
import os
from datetime import date, timedelta

__version__ = "0.1.0"
__all__ = ["EXCHANGES", "YEARS", "NotCovered", "is_trading_day", "next_trading_day", "previous_trading_day",
           "add_trading_days", "trading_days_between", "close_time", "holidays"]

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
YEARS = (2026, 2027, 2028)


class NotCovered(ValueError):
    """The exchange or year is not in the bundled data."""


def _load():
    closed, early, hours = {}, {}, {}
    with open(os.path.join(_DATA, "exchange_holidays_2026_2028.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            k = (r["mic"], date.fromisoformat(r["date"]))
            if r["status"] == "closed":
                closed[k] = r["holiday"]
            else:
                early[k] = r["close_local"]
    with open(os.path.join(_DATA, "trading_hours.csv"), newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            hours[r["mic"]] = r
    return closed, early, hours


_CLOSED, _EARLY, _HOURS = _load()
EXCHANGES = tuple(_HOURS)


def _d(x):
    return x if isinstance(x, date) else date.fromisoformat(str(x))


def _check(mic, d):
    if mic not in _HOURS:
        raise KeyError(f"unknown exchange {mic}; available: {', '.join(EXCHANGES)}")
    if d.year not in YEARS:
        raise NotCovered(f"{d.year} is not covered (bundled: 2026-2028)")


def is_trading_day(mic, d):
    mic, d = mic.upper(), _d(d)
    _check(mic, d)
    return d.weekday() < 5 and (mic, d) not in _CLOSED


def _step(mic, d, step):
    d = _d(d) + timedelta(days=step)
    while not is_trading_day(mic, d):
        d += timedelta(days=step)
    return d


def next_trading_day(mic, d):
    return _step(mic, d, 1)


def previous_trading_day(mic, d):
    return _step(mic, d, -1)


def add_trading_days(mic, d, n):
    """n trading days after d (before d when n < 0); n = 0 returns d if it trades, else the next trading day."""
    d = _d(d)
    if n == 0:
        return d if is_trading_day(mic, d) else next_trading_day(mic, d)
    for _ in range(abs(n)):
        d = _step(mic, d, 1 if n > 0 else -1)
    return d


def trading_days_between(mic, start, end):
    """Trading days with start <= day <= end (0 when start > end)."""
    s, e = _d(start), _d(end)
    n, d = 0, s
    while d <= e:
        n += is_trading_day(mic, d)
        d += timedelta(days=1)
    return n


def close_time(mic, d):
    """Local closing time 'HH:MM' on a trading day (early closes included); None when closed."""
    mic, d = mic.upper(), _d(d)
    if not is_trading_day(mic, d):
        return None
    return _EARLY.get((mic, d), _HOURS[mic]["close_local"])


def holidays(mic, year):
    """[(date, name)] weekday closures of `mic` in `year`."""
    mic = mic.upper()
    _check(mic, date(year, 1, 1))
    return sorted((d, n) for (m, d), n in _CLOSED.items() if m == mic and d.year == year)


def cli(argv=None):
    import sys
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 2:
        print("usage: exchange-trading-days XLON 2026-12-24")
        return 2
    try:
        c = close_time(argv[0], argv[1])
        print(f"trading, closes {c} local" if c else "closed")
    except (NotCovered, KeyError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0
