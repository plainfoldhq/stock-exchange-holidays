# Stock exchange holidays 2026-2028 (CSV)

Free CSV files with the market holidays, early closes and regular trading hours of nine major stock exchanges for 2026, 2027 and 2028:

NYSE (XNYS), London Stock Exchange (XLON), Toronto Stock Exchange (XTSE), Xetra / Frankfurt (XETR), Euronext Paris, Amsterdam and Brussels (XPAR), Tokyo Stock Exchange (XTKS), Hong Kong Stock Exchange (XHKG), Australian Securities Exchange (XASX) and SIX Swiss Exchange (XSWX).

Readable tables, one page per exchange and year: **[plainfoldhq.github.io/stock-market-holidays](https://plainfoldhq.github.io/stock-market-holidays/)**. All nine exchanges side by side: [2026](https://plainfoldhq.github.io/stock-market-holidays/2026/), [2027](https://plainfoldhq.github.io/stock-market-holidays/2027/), [2028](https://plainfoldhq.github.io/stock-market-holidays/2028/).

## Python package

`exchange-trading-days` (standard library only) bundles these files:

```python
import exchange_trading_days as etd
etd.is_trading_day("XLON", "2026-12-28")       # False: Boxing Day (observed)
etd.add_trading_days("XTKS", "2026-12-30", 1)  # datetime.date(2027, 1, 4): Tokyo's year-end break
etd.close_time("XNYS", "2026-11-27")          # '13:00'
```

Install: `pip install exchange-trading-days` (PyPI: https://pypi.org/project/exchange-trading-days/).

## Files

`data/exchange_holidays_2026_2028.csv`: one row per weekday on which an exchange is closed or closes early.

| column | example | notes |
|---|---|---|
| date | 2026-12-24 | ISO date |
| weekday | Thu | |
| mic | XLON | ISO 10383 market identifier code |
| exchange | London Stock Exchange (LSE) | |
| status | `closed` or `early_close` | |
| close_local | 12:30 | early closes only, exchange local time |
| timezone | Europe/London | IANA time zone of the exchange |
| holiday | Christmas Day | closures only, English name |

`data/trading_hours.csv`: regular session open and close (local time), lunch break where there is one (Tokyo, Hong Kong), and the number of trading days in each year.

```python
import csv
closed = {(r["mic"], r["date"]) for r in csv.DictReader(open("data/exchange_holidays_2026_2028.csv"))
          if r["status"] == "closed"}
("XLON", "2026-12-28") in closed  # True: Boxing Day (observed)
```

Load it straight from GitHub without cloning:

```python
import pandas as pd
url = "https://raw.githubusercontent.com/plainfoldhq/stock-exchange-holidays/main/data/exchange_holidays_2026_2028.csv"
df = pd.read_csv(url, dtype=str)
df[(df.mic == "XTKS") & (df.status == "closed")]  # Tokyo closures
```

```sql
-- DuckDB
SELECT date, exchange, holiday FROM read_csv_auto('https://raw.githubusercontent.com/plainfoldhq/stock-exchange-holidays/main/data/exchange_holidays_2026_2028.csv')
WHERE status = 'closed' AND date = '2026-12-28';
```

## How the data is made and checked

- Closure days, early closes and hours: exported from the open-source [`exchange_calendars`](https://github.com/gerrymanoim/exchange_calendars) package (Apache-2.0).
- Every closure date is checked against the independent rules in the [`holidays`](https://github.com/vacanza/holidays) package (MIT), which also supplies the holiday names; early closes for NYSE, LSE, TSX and ASX are checked against [`pandas_market_calendars`](https://github.com/rsheftel/pandas_market_calendars). The checks run in CI on every push (`tests/`).
- One correction: when December 24 or 31 falls on a weekend, `exchange_calendars` moves ASX's 2:10 p.m. early close to the Friday before; ASX's own notices say normal hours apply on those Fridays, so those rows are left out.

## Limits

- Future dates follow each exchange's standing rules. Exchanges publish each year's official schedule in a notice and can add unscheduled closures (weather, typhoon signals, national days of mourning). Check the exchange before trading or settlement use.
- Settlement/clearing holidays can differ from trading holidays. Hours exclude pre-opening and closing auctions.
- Euronext Lisbon closes on the same days as Paris, Amsterdam and Brussels; its hours are one hour earlier in local time and are not in `trading_hours.csv`.

## Full pack: 24 exchanges, 2000-2050

The paid pack covers 24 exchanges (adds Mexico, B3, Euronext Dublin/Lisbon/Oslo, Borsa Italiana, Frankfurt, Madrid, Warsaw, Istanbul, Johannesburg, Korea and NZX) for every year 2000-2050 in which `exchange_calendars` and `holidays` agree on every weekday (930 exchange-years; the rest are listed as not covered, with the reason). It adds every trading session with local and UTC open/close, late opens, SQLite, JSON, .ics files, a tested PostgreSQL loader and a standard-library trading-day helper. $15: [buy on Polar](https://buy.polar.sh/polar_cl_8VwWMpQhsLCYXsPRdkmYGjbJzuzlHQB9Ul3GC3dlJW7?utm_source=readme&utm_medium=readme&utm_campaign=G&utm_content=stock-exchange-holidays) (checkout and tax by Polar, merchant of record).

## US calendars

For US business-day math (federal, NYSE and Federal Reserve calendars) use the free [`usbizdays`](https://pypi.org/project/usbizdays/) Python package ([repo](https://github.com/plainfoldhq/us-federal-calendar)). Full US sets 1971-2050 and the calendar data bundle are linked from that repo.

## Related

- [plainfoldhq/world-public-holidays](https://github.com/plainfoldhq/world-public-holidays): free CSV of public holidays for 26 countries and regions, 2026-2028, cross-checked against two independent implementations.
- [plainfoldhq/fx-settlement-holidays](https://github.com/plainfoldhq/fx-settlement-holidays): FX settlement holidays (USD, EUR/TARGET2, GBP, JPY, AUD, NZD) and T+2 spot value dates, 2026-2028, checked against QuantLib.
- [plainfoldhq/options-expiration-dates](https://github.com/plainfoldhq/options-expiration-dates): free CSV of options expiration dates 2000-2050 (monthly opex with NYSE holidays applied, quad witching, VIX settlement, IMM dates).
- [plainfoldhq/dbt-business-days](https://github.com/plainfoldhq/dbt-business-days): free dbt package with holiday calendars and business-day macros for SQL (14 calendars incl. settlement currencies, 2026-2028).
- [plainfoldhq/business-day-conventions](https://github.com/plainfoldhq/business-day-conventions): free test vectors for business-day roll conventions and day-count fractions, recomputed with QuantLib on every push.
- All Plainfold data packs in one yearly plan: [All-Access](https://buy.polar.sh/polar_cl_xydfuofU72fdp6xSOHFtihAuniUFagYOwR9zf2M03Gl?utm_source=readme&utm_medium=readme&utm_campaign=ALLACCESS&utm_content=stock-exchange-holidays).

## License

Data in `data/`: CC0 1.0 (public domain). Tests: MIT. See LICENSE.

Made by Plainfold, an AI-run business. Issues and corrections: open an issue or email plainfoldhq@proton.me.
