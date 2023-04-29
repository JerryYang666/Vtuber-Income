# Copyright (c) 2023.
# -*-coding:utf-8 -*-
"""
@file: ChatDownload.py
@author: Jerry(Ruihuang)Yang
@email: rxy216@case.edu
@time: 4/23/23 17:50
"""
import json
import time
import backoff
import chat_downloader.errors
import pytube
from chat_downloader import ChatDownloader
from pytube import YouTube

from LocalCache import LocalCache


def get_month(period_txt):
    """
    give a text description of period, return the number of months
    :param period_txt:
    :return: number of months
    """
    if "month" in period_txt:
        return int(period_txt[:period_txt.find(" ")])
    elif "year" in period_txt:
        return int(period_txt[:period_txt.find(" ")]) * 12


class ChatDownload:
    VTUBER_NAME = 'voxakuma'
    URL_LIST_NAME = f'all_videos_{VTUBER_NAME}.txt'
    METADATA_NAME = f'all_metadata_{VTUBER_NAME}.txt'
    BASE_URL = 'https://www.youtube.com/watch?v='
    METADATA_CACHE = f'metadata_cache_{VTUBER_NAME}.json'
    MEMBER_MASTER_LIST = 'member_list.json'

    def __init__(self):
        self.metadata_cache = LocalCache(self.METADATA_CACHE)
        self.chat = None
        self.urls = self.get_url_list()
        self.ids = self.get_vid_list()

    def get_url_list(self):
        url_list = []
        with open(self.URL_LIST_NAME, 'r') as f:
            for line in f.readlines():
                url_list.append(self.BASE_URL + line.strip('\n'))
        return url_list

    def get_vid_list(self):
        id_list = []
        with open(self.URL_LIST_NAME, 'r') as f:
            for line in f.readlines():
                id_list.append(line.strip('\n'))
        return id_list

    @backoff.on_exception(backoff.expo, (pytube.exceptions.PytubeError, ValueError), max_time=60)
    def get_metadata(self):
        """
        get metadata for all videos
        :return:
        """
        metadata_all = {}
        for url in self.urls:
            if self.metadata_cache.is_in_cache(url):
                metadata_all[url] = self.metadata_cache.get_local_cache(url)
            else:
                yt = YouTube(url)
                metadata = {
                    'title': yt.title,
                    'publish_date': yt.publish_date.strftime('%Y-%m-%d'),
                    'views': yt.views,
                    'duration': yt.length
                }
                self.metadata_cache.set_local_cache(url, metadata)
                metadata_all[url] = metadata
                time.sleep(3)
        with open(self.METADATA_NAME, 'w') as f:
            json.dump(metadata_all, f)

    def get_all_chat(self):
        """
        get chat for all videos
        :return:
        """
        count = 0
        for url in self.urls:
            try:
                self.get_chat(url)
                count += 1
                print(f'{count} videos done, UID {url[-11:]}')
            except chat_downloader.errors.ChatDownloaderError:
                count += 1
                print(f'{count} videos skipped, URL {url}')
                continue

    def get_chat(self, url):
        """
        get chat obj for a single video
        :param url: url of the video
        :return:
        """
        self.chat = ChatDownloader().get_chat(url, message_types=['text_message',
                                                                  'membership_item',
                                                                  'paid_message',
                                                                  'paid_sticker',
                                                                  'sponsorships_gift_purchase_announcement',
                                                                  'ticker_paid_sticker_item',
                                                                  'ticker_paid_message_item',
                                                                  'ticker_sponsor_item',
                                                                  'banner',
                                                                  'banner_header',
                                                                  'donation_announcement'])
        #self.record_paid_chat(url)  # do not need to run again
        self.record_membership()

    def record_paid_chat(self, url):
        msg_counter = 0
        chat_dict = {}
        last_msg_id = ''
        for message in self.chat:  # iterate over messages
            if message['message_id'] != last_msg_id:  # remove duplicate messages
                last_msg_id = message['message_id']
                if 'money' in message:  # remove non-money messages
                    period = 0
                    if 'badges' in message['author'] and "ember" in message['author']['badges'][0]['title']:
                        #  check if the message is from a member
                        title = message['author']['badges'][0]['title']
                        #  calculate the membership period in months
                        if 'New' in title:
                            period = 1  # default new member to 1 month
                        else:
                            period = get_month(title[title.find("(") + 1:title.find(")")])
                    #  add message to the chat dictionary
                    chat_dict[msg_counter] = {"time": message['time_in_seconds'],
                                              "money": message['money'],
                                              "msg": message['message'],
                                              "membership": period}
                    msg_counter += 1
        chat_dict['metadata'] = {**self.metadata_cache.get_local_cache(url), "msg_count": msg_counter}
        with open(f'chats/{url[-11:]}.json', 'w') as f:
            f.write(json.dumps(chat_dict, indent=2))

    def record_membership(self):
        member_dict_for_vid = {}
        last_msg_id = ''
        for message in self.chat:  # iterate over messages
            if message['message_id'] != last_msg_id:  # remove duplicate messages
                last_msg_id = message['message_id']
                if 'id' in message['author'] and 'badges' in message['author'] and "ember" in message['author']['badges'][0]['title']:
                    #  check if the message is from a member
                    period = 0  # default period to 0 months
                    user_id = message['author']['id']
                    title = message['author']['badges'][0]['title']
                    #  calculate the membership period in months
                    if 'New' in title:
                        period = 1  # default new member to 1 month
                    else:
                        period = get_month(title[title.find("(") + 1:title.find(")")])
                    #  update the membership period for this video
                    if user_id not in member_dict_for_vid:
                        member_dict_for_vid[user_id] = period
                    else:
                        if period > member_dict_for_vid[user_id]:
                            member_dict_for_vid[user_id] = period
        #  update the membership period for all videos
        all_member = self.read_member_master_list()
        #  update the member period
        for member in member_dict_for_vid:
            if member not in all_member:
                all_member[member] = member_dict_for_vid[member]
            elif member_dict_for_vid[member] > all_member[member]:
                all_member[member] = member_dict_for_vid[member]
        self.write_member_master_list(all_member)

    def read_member_master_list(self):
        try:
            with open(f'membership/{self.MEMBER_MASTER_LIST}', 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            with open(f'membership/{self.MEMBER_MASTER_LIST}', 'w') as file:
                data = {}
                json.dump(data, file)
        return data

    def write_member_master_list(self, data):
        with open(f'membership/{self.MEMBER_MASTER_LIST}', 'w') as file:
            file.write(json.dumps(data, indent=2))







down = ChatDownload()
down.get_all_chat()
