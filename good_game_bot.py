import os
from dotenv import load_dotenv
import telebot
import logging
import random
import requests

# load API token
load_dotenv()
TOKEN = os.getenv('TOKEN')

# to receive user's fake balance
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

Кейс для Бояр (500 рублей):
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

START_COMMAND = 'start'
HOW_TO_COMMAND = 'how_to'
PRIZES_COMMAND = 'prizes'
OPEN_BOX_COMMAND = 'open_box'
INFO_COMMANDS = HOW_TO_COMMAND, PRIZES_COMMAND

HOW_TO_BUTTON = telebot.types.InlineKeyboardButton(text='Как открыть коробку?', callback_data=HOW_TO_COMMAND)
PRIZES_BUTTON = telebot.types.InlineKeyboardButton(text='Призы', callback_data=PRIZES_COMMAND)
OPEN_BOX_BUTTON = telebot.types.InlineKeyboardButton(text='Открыть коробку', callback_data=OPEN_BOX_COMMAND)

SINGLE_250 = 'Базовый Кейс'
DOUBLE_250 = '2 Базовых Кейса'
SINGLE_500 = 'Кейс для Бояр'
TRIPLE_250 = '3 Базовых Кейса'
DOUBLE_500 = '2 Кейса для Бояр'
SINGLE_1000 = 'Кейс для Вельмож'
TRIPLE_500 = '3 Кейса для Бояр'
DOUBLE_1000 = '2 Кейса для вельмож'
SINGLE_2000 = 'Кейс для Меценатов'
BOX_CHOICES = SINGLE_250, DOUBLE_250, SINGLE_500, TRIPLE_250, DOUBLE_500, SINGLE_1000, TRIPLE_500, DOUBLE_1000, SINGLE_2000

PRIZE_RECEIVED = False

bot = telebot.TeleBot(TOKEN, parse_mode=None)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=[START_COMMAND])
def start(message):
    text = 'Добро пожаловать! Здесь ты можешь получить классные коробки с призами от Good Game. Жми на кнопки, чтобы узнать больше!'
    markup = configure_keyboard(START_COMMAND)
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in INFO_COMMANDS)
def info_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    if call.data == HOW_TO_COMMAND:
        text = HOW_TO_TEXT
    elif call.data == PRIZES_COMMAND:
        text = PRIZES_TEXT

    markup = configure_keyboard(call.data)
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == OPEN_BOX_COMMAND)
def open_box_handler(call):
    global PRIZE_RECEIVED

    bot.answer_callback_query(callback_query_id=call.id)
    markup = configure_keyboard(command=call.data)
    if PRIZE_RECEIVED:
        bot.send_message(call.message.chat.id, 'Вы уже получили свой приз. Пополните счёт, чтобы получить новые призы.', reply_markup=markup)
        PRIZE_RECEIVED = False
        return

    balance = get_balance()
    balance_text = f'За последние 24 часа вы пополнили баланс на {balance} рублей. '

    if balance >= 250 and balance < 500:
        text = f'Поздравляем, вы получаете {SINGLE_250}!'
        PRIZE_RECEIVED = True
    elif balance >= 500:
        text = 'У вас доступно несколько коробок:'
        if balance < 1000:
            button1 = telebot.types.InlineKeyboardButton(text='2 коробки за 250', callback_data=DOUBLE_250)
            button2 = telebot.types.InlineKeyboardButton(text='1 коробка за 500', callback_data=SINGLE_500)
            markup = configure_keyboard(buttons=(button1, button2))
        elif balance >= 1000 and balance < 2000:
            button1 = telebot.types.InlineKeyboardButton(text='3 коробки за 250', callback_data=TRIPLE_250)
            button2 = telebot.types.InlineKeyboardButton(text='2 коробки за 500', callback_data=DOUBLE_500)
            button3 = telebot.types.InlineKeyboardButton(text='1 коробка за 1000', callback_data=SINGLE_1000)
            markup = configure_keyboard(buttons=(button1, button2, button3))
        elif balance >= 2000:
            button1 = telebot.types.InlineKeyboardButton(text='3 коробки за 250', callback_data=TRIPLE_250)
            button2 = telebot.types.InlineKeyboardButton(text='3 коробки за 500', callback_data=TRIPLE_500)
            button3 = telebot.types.InlineKeyboardButton(text='2 коробки за 1000', callback_data=DOUBLE_1000)
            button4 = telebot.types.InlineKeyboardButton(text='1 коробка за 2000', callback_data=SINGLE_2000)
            markup = configure_keyboard(buttons=(button1, button2, button3, button4))
    else:
        text = 'Нужно пополнить счёт не менее, чем на 250 рублей, чтобы получить подарок 😢'

    text = ' '.join((balance_text, text))
    bot.send_message(call.message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in BOX_CHOICES)
def box_choices_handler(call):
    global PRIZE_RECEIVED

    bot.answer_callback_query(callback_query_id=call.id)
    text = call.data
    final_text = f'Поздравляем, вы получаете {text}!'
    markup = configure_keyboard(START_COMMAND)
    bot.send_message(call.message.chat.id, final_text, reply_markup=markup)
    PRIZE_RECEIVED = True


def configure_keyboard(command=None, buttons=None):
    markup = telebot.types.InlineKeyboardMarkup()
    if buttons:
        markup.add(*buttons)
    elif command == START_COMMAND or command == OPEN_BOX_COMMAND:
        markup.add(OPEN_BOX_BUTTON)
        markup.add(PRIZES_BUTTON, HOW_TO_BUTTON)
    elif command == HOW_TO_COMMAND:
        markup.add(OPEN_BOX_BUTTON, PRIZES_BUTTON)
    elif command == PRIZES_COMMAND:
        markup.add(OPEN_BOX_BUTTON, HOW_TO_BUTTON)
    return markup


def get_balance():
    # pretend to get user's balance data
    user_id = random.randint(1, 5)
    users = requests.get(MONEY_URL).json()
    user_balance = users[str(user_id)]
    return user_balance


bot.polling()
