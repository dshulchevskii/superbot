import logging
import requests
import json
import os
from itertools import permutations



DICT_URL = 'https://raw.githubusercontent.com/solovets/russian-words/master/words.json'
TOKEN = os.getenv('BOT_TOKEN')
logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)


def load_dict(url):
    req = requests.get(url)
    js_data = json.loads(req.text)
    return set(js_data)


def get_all_subwords(word, dictionary):
    """
    >>> list(get_all_subwords('победа', {'обед', 'еда', 'да', 'звезда'}))
    ['да', 'еда', 'обед']
    """
    subwords = set()

    for n_chars in range(len(word)):
        for subword_chars in permutations(word, n_chars):
            subword = ''.join(subword_chars)
            if subword in dictionary and subword not in subwords:
                yield subword
                subwords.add(subword)


def get_main_word(text):
    """
    >>> get_main_word("Текст с большим количеством слов")
    'текст'
    >>> get_main_word("english")

    >>> get_main_word("йцукенгшщзфывапролджячсмитьбюапр")

    """
    russian_chars = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    word = text.lower().split()[0]
    if 0 < len(word) < 20 and all(c in russian_chars for c in word):
        return word


def main():
    import telebot
    logging.info('Start app')
    DICTIONARY = load_dict(DICT_URL)
    logging.info('Load dictionary')
    bot = telebot.TeleBot(TOKEN)
    logging.info('Start bot')

    @bot.message_handler(commands=['start', 'go'])
    def start_handler(message):
        bot.send_message(
            message.chat.id,
            'Привет, пришли слово и я верну все "слова в слове"'
        )

    @bot.message_handler(content_types=['text'])
    def process(message):
        text = message.text.lower()
        chat_id = message.chat.id
        word = get_main_word(text)
        if not word:
            bot.send_message(chat_id, 'отправьте одно слово на русском языке не длиннее 20 символов')
            logging.info('invalid text %s', text)
        else:
            bot.send_message(chat_id, 'для слова: %s' % word)
            logging.info('get word %s', word)
            bot.send_message(chat_id, '🚀')
            for sub_word in get_all_subwords(word, DICTIONARY):
                logging.info('return %s', sub_word)
                bot.send_message(chat_id, sub_word)

            bot.send_message(chat_id, '🏁')
            logging.info('finish with word %s', word)

    bot.polling()


if __name__ == '__main__':
    main()
