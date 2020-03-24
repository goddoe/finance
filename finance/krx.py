import io
import time
from datetime import timedelta, date

import requests
import pandas as pd
from tqdm import tqdm


def get_fundamentals(year, month, day):
    """Gets fundamentals from a specific date from KRX.

    Args:
        year (int): year.
        month (int): month.
        day (int): day.

    Returns:
        pd.DataFrame, a table that contains stock fundamentals.
    """

    def _get_otp(year, month, day):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
        otp_url = "http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx?" \
                  "name=fileDown&filetype=csv&url=MKD/13/1302/13020401/mkd13020401&" \
                  "market_gubun=ALL&gubun=1&isu_cdnm=A005930/삼성전자&isu_cd=KR7005930003&isu_nm=삼성전자&isu_srt_cd=A005930&" \
                  "schdate={schdate}&pagePath=/contents/MKD/13/1302/13020401/MKD13020401.jsp".format(schdate=date(year, month, day).strftime("%Y%m%d"))
        otp = requests.get(otp_url, headers=headers).text
        return otp

    def _download_csv(otp):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Referer': 'http://marketdata.krx.co.kr/mdi'}
        download_url = "http://file.krx.co.kr/download.jspx"
        result = requests.post(download_url, data=[("code", otp)], headers=headers)
        return pd.read_csv(io.BytesIO(result.content))

    otp = _get_otp(year, month, day)
    data = _download_csv(otp)
    return data


def get_fundamentals_from_to(from_year, from_month, from_day,
                             to_year, to_month, to_day,
                             req_interval_sec=2):
    """Gets fundamentals of a specific period from KRX.

    Args:
        from_year (int): from year.
        from_month (int): from month.
        from_day (int): from day.
        to_year (int): to year.
        to_month (int): to month.
        to_day (int): to day.
        req_interval_sec (int): interval between requests.

    Returns:
        pd.DataFrame, a table that contains stock fundamentals.
    """

    def date_range(from_date, to_date):
        for i in range(int((to_date - from_date).days)+1):
            yield from_date + timedelta(i)

    from_date = date(from_year, from_month, from_day)
    to_date = date(to_year, to_month, to_day)

    fundamentals_list = []
    for curr_date in tqdm(date_range(from_date, to_date)):
        sample = get_fundamentals(curr_date.year,
                                  curr_date.month,
                                  curr_date.day)
        if len(sample) > 0:
            fundamentals_list.append(sample)
        time.sleep(req_interval_sec)

    fundamentals_df = pd.concat(fundamentals_list)
    return fundamentals_df
