# Copyright (c) 2023.
# -*-coding:utf-8 -*-
"""
@file: CurrencyExchange.py
@author: Jerry(Ruihuang)Yang
@email: rxy216@case.edu
@time: 4/23/23 16:49
"""
import json
from datetime import date
import requests
from LocalCache import LocalCache


def date_to_string(date_obj):
    """
    convert date to string
    :param date_obj:
    :return: string of date
    """
    return date_obj.strftime("%Y-%m-%d")


def string_to_date(string):
    """
    convert string to date
    :param string:
    :return: date of string
    """
    return date.fromisoformat(string)


class CurrencyExchange:
    """
    Currency Exchange class, have a cache system to reduce API calls
    """
    LOCAL_CACHE = 'cached_exchange_data.json'
    URL = 'https://api.exchangerate.host/convert?from='

    def __init__(self):
        self.cache = LocalCache(self.LOCAL_CACHE)

    def get_exchange_rate(self, from_currency, to_currency):
        """
        get exchange rate from local cache or API
        :param from_currency:
        :param to_currency:
        :return:exchange rate of two currencies
        """
        # check if data is cached
        cache_key = from_currency + "." + to_currency
        if self.cache.is_in_cache(cache_key) and string_to_date(
                self.cache.cached_data[cache_key]["date"]) == date.today():
            exchange_rate = self.cache.get_local_cache(cache_key)["rate"]
            # print(f'[local cache] {cache_key} = {exchange_rate}')
        else:
            exchange_rate = self.get_exchange_rate_from_api(from_currency, to_currency)
            print(f'[API] {cache_key} = {exchange_rate}')
            self.set_local_cache(cache_key, exchange_rate)
        return exchange_rate

    def get_exchange_rate_from_api(self, from_currency, to_currency):
        """
        get exchange rate from API and cache it to local file if it's not cached
        :param from_currency:
        :param to_currency:
        :return: exchange rate of two currencies
        """
        # get data from API
        response = requests.get(self.URL + from_currency + '&to=' + to_currency)
        data = response.json()
        # get exchange rate
        exchange_rate = data['info']['rate']
        return exchange_rate

    def set_local_cache(self, cache_key, exchange_rate):
        """
        set cached data to local file
        :param cache_key:
        :param exchange_rate:
        """
        self.cache.set_local_cache(cache_key, {"date": date_to_string(date.today()), "rate": exchange_rate})


"""
if __name__ == '__main__':
    currency_exchange = CurrencyExchange()
    print(currency_exchange.get_exchange_rate('CNY', 'USD'))
    print(currency_exchange.get_exchange_rate('GBP', 'CNY'))
    print(currency_exchange.get_exchange_rate('USD', 'GBP'))
    print(currency_exchange.get_exchange_rate('USD', 'JPY'))
    print(currency_exchange.get_exchange_rate('JPY', 'DKK'))
"""
