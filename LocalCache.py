# Copyright (c) 2023.
# -*-coding:utf-8 -*-
"""
@file: LocalCache.py
@author: Jerry(Ruihuang)Yang
@email: rxy216@case.edu
@time: 4/23/23 20:21
"""
import json


class LocalCache:

    def __init__(self, file_name):
        self.cache_path = file_name
        self.cached_data = self.initiate_local_cache()

    def initiate_local_cache(self):
        """
        initiate cached data from local file
        :return: dict of cached data
        """
        # open json file and load data, if file not exist, create one
        try:
            with open(self.cache_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            with open(self.cache_path, 'w') as file:
                data = {}
                json.dump(data, file)
        return data

    def is_in_cache(self, key):
        """
        check if data is cached
        :param key: cache key
        :return: True if cached, False if not
        """
        return key in self.cached_data

    def get_local_cache(self, key):
        """
        get cached data for a key from local file
        :param key: cache key
        :return: cache value
        """
        return self.cached_data[key]

    def set_local_cache(self, key, value):
        """
        set cached data to local file
        :param key:
        :param value:
        """
        # update RAM cache
        self.cached_data[key] = value
        # update local cache
        with open(self.cache_path, 'w') as file:
            file.write(json.dumps(self.cached_data, indent=2))
