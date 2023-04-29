# Copyright (c) 2023.
# -*-coding:utf-8 -*-
"""
@file: ChatAnalysis.py
@author: Jerry(Ruihuang)Yang
@email: rxy216@case.edu
@time: 4/23/23 17:48
"""
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud

from CurrencyExchange import CurrencyExchange


class ChatAnalysis:
    MEMBERSHIP_PRICE = 4.99

    def __init__(self, chat_path='chats/', membership_file='membership/member_list.json'):
        """
        initialize the chat analysis class
        :param chat_path: path to the chat folder where all the chat files are stored
        :param membership_file: path to the membership file
        """
        self.all_prints = []
        self.total_membership_revenue = None
        self.temp_video_list_seq_count = {}
        self.word_cloud_data = None
        self.income_usd_by_currency = {}
        self.total_income_in_usd = None
        self.income_by_video = None
        self.income_by_month = {}
        self.membership = None
        self.chat_path = chat_path
        self.currency_exchange = CurrencyExchange()
        file_list = os.listdir(chat_path)
        self.video_list = []
        for video in file_list:
            if 'json' in video:
                self.video_list.append(video)
        self.load_membership(membership_file)
        print(f'Total number of videos: {len(self.video_list)}')
        self.load_paid_message()

    def get_video_sequence_id(self, video_date):
        """
        get the sequence id of video that will be used in income_by_video
        :return: a list of video sequence
        """
        year, month, day = video_date.split('-')
        year_month = year + month
        if year_month not in self.temp_video_list_seq_count:
            self.temp_video_list_seq_count[year_month] = 100
            return year_month + '100'
        else:
            self.temp_video_list_seq_count[year_month] += 1
            return year_month + str(self.temp_video_list_seq_count[year_month])

    def get_amount_in_usd(self, amount, currency):
        """
        convert the amount to usd
        :param amount: amount of money
        :param currency: currency symbol
        :return: amount in usd
        """
        if currency == '₫':
            currency = 'VND'
        currency = currency.upper()
        if currency == 'USD':
            return amount
        else:
            return amount * self.currency_exchange.get_exchange_rate(currency, 'USD')

    def set_income_usd_by_currency(self, currency, usd_amount):
        """
        count the income by currency in usd
        :param currency: currency symbol
        :param usd_amount: amount in usd
        :return:
        """
        if currency in self.income_usd_by_currency:
            self.income_usd_by_currency[currency] += usd_amount
        else:
            self.income_usd_by_currency[currency] = usd_amount

    def set_income_by_month(self, month, usd_amount):
        """
        count the income by month
        :param month: YYYYMM
        :param usd_amount: amount in usd
        :return:
        """
        if month in self.income_by_month:
            self.income_by_month[month] += usd_amount
        else:
            self.income_by_month[month] = usd_amount

    def load_membership(self, membership_file):
        with open(membership_file, 'r') as f:
            membership = json.load(f)
        self.membership = np.array([])
        for member in membership:
            self.membership = np.append(self.membership, membership[member])

    def load_paid_message(self):
        """
        load all the paid message from the chat file
        self.all_chat_data is a dictionary with key as date-No.xxx and value as a chat data dictionary
        :return:
        """
        self.income_by_video = {}
        self.total_income_in_usd = 0
        self.word_cloud_data = ""
        processed_video_count = 0
        for video in self.video_list:
            with open(self.chat_path + video, 'r') as f:
                chat_data = json.load(f)
            vid_seq = self.get_video_sequence_id(chat_data['metadata']['publish_date'])
            del chat_data['metadata']
            video_total_income = 0
            for msg_data in chat_data.items():
                msg_data = msg_data[1]
                # store data for word cloud
                if msg_data['msg'] is not None:
                    self.word_cloud_data += msg_data['msg']
                # convert the amount to usd
                usd_amount = self.get_amount_in_usd(msg_data['money']['amount'], msg_data['money']['currency'])
                # store data for total income
                self.total_income_in_usd += usd_amount
                # store data for income by currency
                self.set_income_usd_by_currency(msg_data['money']['currency'], usd_amount)
                # store data for income by video
                video_total_income += usd_amount
            self.income_by_video[vid_seq] = video_total_income
            self.set_income_by_month(vid_seq[:6], video_total_income)
            processed_video_count += 1
            print('\r', 'Processing: ', processed_video_count, '/', len(self.video_list), end='')
            # print(f'No.{processed_video_count} Video {video} total income: {video_total_income} USD')
        print('')

    def analysis_all(self):
        """
        analysis and plot all the data
        :return:
        """
        self.all_prints.append(' ')
        print('Paid message plots:')
        self.analysis_paid_message()
        print('Membership plots:')
        self.analysis_membership()
        self.all_prints.append(' ')
        self.all_prints.append(f'Total income on Youtube: {round(self.total_income_in_usd + self.total_membership_revenue, 2)} USD')
        for print_data in self.all_prints:
            print(print_data)

    def analysis_paid_message(self):
        """
        analysis and plot the paid message data
        :return:
        """
        self.all_prints.append(f'Total paid message revenue: {round(self.total_income_in_usd, 2)} USD')
        print('Income by currency:')
        self.plot_income_by_currency()
        print('Income by month:')
        self.plot_income_by_month()
        print('Income by video:')
        self.plot_income_by_video()
        print('Key word cloud from all paid messages:')
        self.plot_word_cloud()

    def plot_income_by_video(self):
        """
        plot the income by video
        :return:
        """
        sorted_data = {k: v for k, v in sorted(self.income_by_video.items())}
        plt.figure(figsize=(18, 11))
        plt.plot(sorted_data.keys(), sorted_data.values(), 'o-', color='#960019')
        plt.xticks([])
        plt.yticks(size=16)
        plt.title('Income by video in USD', size=24)
        plt.xlabel('Video', size=20)
        plt.ylabel('Income in USD', size=20)
        plt.show()

    def plot_income_by_month(self):
        """
        plot the income by month
        :return:
        """
        sorted_data = {k: v for k, v in sorted(self.income_by_month.items())}
        plt.figure(figsize=(16, 11))
        plt.plot(sorted_data.keys(), sorted_data.values(), 's-', color='#960019')
        plt.xticks(rotation=45, size=16)
        plt.yticks(size=16)
        plt.title('Income by month in USD', size=24)
        plt.xlabel('Month', size=20)
        plt.ylabel('Income in USD', size=20)
        plt.show()

    def plot_income_by_currency(self):
        """
        plot the income by currency
        :return:
        """
        sorted_data = {k: v for k, v in sorted(self.income_usd_by_currency.items(), key=lambda x: x[1], reverse=True)}
        plt.figure(figsize=(16, 11))
        plt.bar(sorted_data.keys(), sorted_data.values(), color='#960019')
        plt.xticks(rotation=45, size=12)
        plt.yticks(size=16)
        plt.title('Income by currency in USD', size=24)
        plt.xlabel('Currency', size=20)
        plt.ylabel('Income in USD', size=20)
        plt.show()

    def plot_word_cloud(self):
        """
        plot the word cloud of the chat
        :return:
        """
        # Create the word cloud
        wordcloud = WordCloud(width=1600, height=800, background_color='white').generate(self.word_cloud_data)
        # Display the word cloud
        plt.figure(figsize=(16, 9))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()

    def analysis_membership(self):
        """
        analysis the membership of the channel, plot a bar plot of the membership length
        """
        self.total_membership_revenue = np.sum(self.membership) * self.MEMBERSHIP_PRICE
        total_num_of_members = len(self.membership)
        average_membership_length = np.mean(self.membership)
        self.all_prints.append(f'Total number of unique members: {total_num_of_members}')
        self.all_prints.append(f'Total membership revenue: ${self.total_membership_revenue:.2f}')
        self.all_prints.append(f'Average membership length: {average_membership_length:.4f} months')
        # generate bar plot data
        unique_arr = np.unique(self.membership)
        distro_arr = np.empty((0, 2))
        for i in unique_arr:
            distro_arr = np.append(distro_arr, np.array([[i, np.count_nonzero(self.membership == i)]]), axis=0)
        plt.bar(distro_arr[:, 0].astype(int).astype(str), distro_arr[:, 1], color='#960019')  # plot bar plot
        # add bar height to the bar plot
        for i, v in enumerate(distro_arr[:, 1]):
            plt.text(i, v + 0.5, str(v.astype(int)), ha='center', fontweight='bold')
        plt.xlabel('Membership Length (Months)')
        plt.ylabel('Number of Members')
        plt.title('Membership Length Distribution')
        plt.show()


ca = ChatAnalysis()
ca.analysis_all()
