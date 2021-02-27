import os
from dotenv import load_dotenv
import telebot
import logging
import random
import requests

# load API token
load_dotenv()
TOKEN = os.getenv('API_TOKEN')
# to receive user's balance status
MONEY_URL = 'https://api.jsonbin.io/b/5f8daafdadfa7a7bbea58fad/2'

HOW_TO_TEXT = '''
Всего три простых шага!

1️) Пополни свой аккаунт Good Game в любом из наших киберспортивных клубов от 250 ₽ за 24 часа суммарно
2️) Нажми на кнопку «Открыть коробку»
3️) Выигрывай призы!

Все призы можно получить у администратора.

Подробнее о всех призах в разделе «Призы»
'''

PRIZES_TEXT = '''
Призы из Кейсов можно забрать сразу у администратора. Для этого необходимо подойти к администратору и, открыв вкладку «Мои подарки», показать список призов, которые у тебя сейчас есть.

Базовый Кейс (250 рублей):
• 1 час игры за ПК
• Полчаса игры за PS

Кейс для бояр (500 рублей):
• Батончик
• 1.5 часа за ПК
• Кола (0.5)
• Пакет в зал Стандарт (ночной)

Кейс для Вельмож (1000 рублей):
• Пакет в зал VIP (утренний)
• Кола и батончик
• 3 часа за PS

Кейс для Меценатов (2000 рублей):
• Абонемент на посещение клуба (на все выходные)
• Кальян
• Пакет в зал VIP (ночной)
'''

HOW_TO_BUTTON = telebot.types.InlineKeyboardButton(text='Как открыть коробку?', callback_data='how_to')
PRIZES_BUTTON = telebot.types.InlineKeyboardButton(text='Призы', callback_data='prizes')
OPEN_BOX_BUTTON = telebot.types.InlineKeyboardButton(text='Открыть коробку', callback_data='open_box')

bot = telebot.TeleBot(TOKEN, parse_mode=None)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start'])
def start(message):
    text = 'Добро пожаловать! У тебя есть шанс получить классные коробки с призами от Good Game. Жми на кнопки, чтобы узнать больше!'
    markup = configure_keyboard('start')
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    text = ' '
    if call.data == 'how_to':
        text = HOW_TO_TEXT
    elif call.data == 'prizes':
        text = PRIZES_TEXT
    elif call.data == 'open_box':
        text = define_prize()

    markup = configure_keyboard(call.data)
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


def define_prize():
    text = ' '
    balance = get_balance()
    balance_text = f'За последние 24 часа вы пополнили баланс на {balance} рублей. '
    if balance >= 250:
        text = 'Поздравляем, вы получаете Базовый кейс!'
    else:
        text = 'Нужно пополнить счёт не менее, чем на 250 рублей, чтобы получить подарок 😢'
    return balance_text + text


def configure_keyboard(command):
    markup = telebot.types.InlineKeyboardMarkup()
    if command == 'start' or command == 'open_box':
        markup.add(OPEN_BOX_BUTTON)
        markup.add(PRIZES_BUTTON, HOW_TO_BUTTON)
    elif command == 'how_to':
        markup.add(OPEN_BOX_BUTTON, PRIZES_BUTTON)
    elif command == 'prizes':
        markup.add(OPEN_BOX_BUTTON, HOW_TO_BUTTON)
    return markup


def get_balance():
    # pretend to get user's balance data
    user_id = random.randint(1, 5)
    users = requests.get(MONEY_URL).json()
    user_balance = users[str(user_id)]
    return user_balance


bot.polling()
