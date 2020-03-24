import time

import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from tqdm import tqdm


def get_fundamentals(req_interval_sec=1):
    """Gets today's fundamentals from Naver Finance.

    Args:
        req_interval_sec (int): interval for requesting.

    Returns:
        pd.DataFrame, a table that contains stock fundamentals.
    """

    def _get_options():
        url = "http://finance.naver.com/sise/sise_market_sum.nhn"

        resp = requests.get(url)
        page = bs(resp.text, 'html.parser')
        checkers = page.select(".subcnt_sise_item_top table input")
        options = []
        for checker in checkers:
            options.append(checker['value'])
        return options

    def _make_naver_fin_url(page,
                            options):
        url_template = "https://finance.naver.com/sise/field_submit.nhn?" \
                       "menu=market_sum&returnUrl=http://finance.naver.com/sise/sise_market_sum.nhn?" \
                       "page={page}&{options}"

        key_vals = []
        for op in options:
            key_vals.append(f"fieldIds={op}")
        url = url_template.format(page=page, options='&'.join(key_vals))
        return url

    table_agg = []

    n_large_enough = 100
    for i in range(1, n_large_enough, 1):
        options = _get_options()
        url = _make_naver_fin_url(page=i, options=options)
        resp = requests.get(url)
        tables = pd.read_html(resp.text)
        table = tables[1]
        table = table[~table.N.isna()]
        if len(table) == 0:
            break
        table_agg.append(table)
        time.sleep(req_interval_sec)

    return pd.concat(table_agg)


def get_performances_by_sector():
    """Gets today's performances by sector from Naver Finance.

    Returns:
        pd.DataFrame, a table that contains performances by sector.
    """
    sector_url = "https://finance.naver.com/sise/sise_group.nhn?type=upjong"

    resp = requests.get(sector_url)
    tables = pd.read_html(resp.text)
    table = tables[0]  # sector is located at 0 idx
    table.columns = ["업종명",
                     "전일대비",
                     "전일대비 등락현황 전체",
                     "전일대비 등락현황 상승",
                     "전일대비 등락현황 보합",
                     "전일대비 등락현황 하락",
                     "등락그래프"]
    return table


def get_companies_by_sector():
    """Gets today's companies by sector from Naver Finance.

    Returns:
        dict, dictionary of 'sector <-> list of company'.
    """
    naver_fin_base_url = "https://finance.naver.com"
    sector_base_url = "https://finance.naver.com/sise/sise_group.nhn?type=upjong"

    resp = requests.get(sector_base_url)
    page = bs(resp.text, 'html.parser')
    sector_urls = page.select("#contentarea_left td a")

    sector_com_dict = {}
    for sector_url in tqdm(sector_urls):
        target_sector_url = naver_fin_base_url + sector_url['href']
        resp = requests.get(target_sector_url)

        coms = pd.read_html(resp.text)[2]
        coms = coms[~coms['종목명'].isna()]['종목명'].tolist()

        sector_com_dict[sector_url.contents[0]] = coms
        time.sleep(1)
    return sector_com_dict
