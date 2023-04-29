import chat_downloader.errors
from chat_downloader import ChatDownloader
from CurrencyExchange import CurrencyExchange


def get_chat():
    url = 'https://www.youtube.com/watch?v=wPt5vEHEJkA'
    chat = ChatDownloader().get_chat(url, message_types=['text_message',
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
    # chat = ChatDownloader().get_chat(url, message_types=['paid_message','paid_sticker','ticker_paid_sticker_item',
    # 'ticker_paid_message_item',]) for message in chat: chat.print_formatted(message) print(message)
    last = ''
    for message in chat:
        # print(message['message_id'])
        if message['message_id'] != last:
            last = message['message_id']
            if 'id' in message['author'] and 'badges' in message['author']:
                print(message['author']['id'])
                print(message['author']['badges'][0]['title'])
            # print(message['time_in_seconds'], message['money'])  # print the message


try:
    get_chat()
except chat_downloader.errors.ChatDownloaderError:
    print("1111222")
