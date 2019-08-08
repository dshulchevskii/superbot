import logging
import requests
import json
import os
from itertools import combinations
import telebot


logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def load_dict(url):
    req = requests.get(url)
    js_data = json.loads(req.text)
    return set(js_data)


DICT_URL = 'https://raw.githubusercontent.com/solovets/russian-words/master/words.json'
DICTIONARY = load_dict(DICT_URL)

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)


def get_all_subwords(word, dictionary):
    """
    >>> list(get_all_subwords('победа', {'обед', 'еда', 'да', 'звезда'}))
    ['да', 'еда', 'обед']
    """
    subwords = set()

    for n_chars in range(len(word)):
        for subword_chars in combinations(word, n_chars):
            subword = ''.join(subword_chars)
            if subword in dictionary and subword not in subwords:
                yield subword
                subwords.add(subword)


@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        'Привет, пришли слово и я верну все "слова в слове"'
    )


@bot.message_handler(content_types=['text'])
def process(message):
    word = message.text.lower()
    chat_id = message.chat.id
    logging.info('get word %s', word)
    bot.send_message(chat_id, '🚀')
    for sub_word in get_all_subwords(word, DICTIONARY):
        logging.info('return %s', sub_word)
        bot.send_message(chat_id, sub_word)

    bot.send_message(chat_id, '🏁')
    logging.info('finish with word %s', word)


bot.polling()
