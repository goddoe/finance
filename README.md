# Finance

Toolset for analyzing the stock market.

- features
  - crawls market data from either [NAVER finance](https://finance.naver.com/) or [KRX](http://marketdata.krx.co.kr/).



## Quick Start

```python
import finance.naver as naver

today_fundamental = naver.get_fundamentals()
today_performances_by_sector = naver.get_performances_by_sector()
companies_by_sector = naver.get_companies_by_sector()


import finance.krx as krx

fundamental = krx.get_fundamentals(2020, 3, 24)
fundamental_of_thoseday = krx.get_fundamentals_from_to(2020, 3, 17,
                                                       2020, 3, 18)
```
