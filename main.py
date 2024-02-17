import os

import telebot

from dotenv import load_dotenv

from telebot.types import ReplyKeyboardMarkup

from dadata import Dadata

from extensions import Converter, APIException

load_dotenv()
token = os.getenv('TOKEN')
da_data_token = os.getenv('DA_DATA_TOKEN')
api_layer_token = os.getenv('API_LAYER_TOKEN')
bot = telebot.TeleBot(token)

COMMANDS_BUTTONS = ReplyKeyboardMarkup(resize_keyboard=True)
COMMANDS_BUTTONS.add('/convert', '/help', '/currency')


@bot.message_handler(commands=['start'])
def start(message):
    text = f'Добрый день @{message.chat.username}.\n\n'
    text += 'Нажмите /help, если нужны инструкции.\n'
    text += 'Нажмите /convert для конвертации.\n'
    text += 'Нажимаем команду /currency, чтобы получить обозначение валют на рынке.\n'
    reply_markup = COMMANDS_BUTTONS
    bot.send_message(message.chat.id, text=text, reply_markup=reply_markup)


@bot.message_handler(commands=['help'])
def help(message):
    text = 'Инструкции.\n\n'
    text += 'Нажимаем команду /convert.\n'
    text += 'Выбираем валюту из которой конвертируем.\n'
    text += 'Выбираем валюту в которую конвертируем.\n'
    text += 'Вводим количество первой валюты.\n\n'
    text += 'Нажимаем команду /currency.\n'
    text += ('Напишите интересующую вас валюту на русском языке или '
             'английском языке и получите ее обозначение на рынке.\n')
    reply_markup = COMMANDS_BUTTONS
    bot.send_message(message.chat.id, text=text, reply_markup=reply_markup)


@bot.message_handler(commands=['currency'])
def currency(message):
    reply_markup = COMMANDS_BUTTONS
    bot.send_message(message.chat.id, "Какая валюта вас интеерсует?", reply_markup=reply_markup)
    bot.register_next_step_handler(message, currency_withdrawal)


def currency_withdrawal(message):
    try:
        dadata = Dadata(da_data_token)
        data = message.text.strip()
        result = dadata.suggest('currency', data)
        res = ""
        for i in result:
            res += f"{i['value']}: {i['data']['strcode']}\n"
        reply_markup = COMMANDS_BUTTONS
        bot.send_message(message.chat.id, res, reply_markup=reply_markup)
    except:
        reply_markup = COMMANDS_BUTTONS
        bot.send_message(message.chat.id, "Неверный формат данных!", reply_markup=reply_markup)


@bot.message_handler(commands=['convert'])
def convert(message):
    text = 'Выберете валюту из которой конвертировать:'
    reply_markup = COMMANDS_BUTTONS
    bot.send_message(message.chat.id, text, reply_markup=reply_markup)
    bot.register_next_step_handler(message, from_handler)


def from_handler(message):
    curr_from = message.text
    text = 'Выберете валюту в которую конвертировать:'
    reply_markup = COMMANDS_BUTTONS
    bot.send_message(message.chat.id, text, reply_markup=reply_markup)
    bot.register_next_step_handler(message, to_handler, curr_from)


def to_handler(message, curr_from):
    curr_to = message.text
    text = 'Напишите количество конвертируемой валюты:'
    bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(message, amount_handler, curr_from, curr_to)


def amount_handler(message, curr_from, curr_to):
    amount = message.text
    try:
        conv = Converter.get_convert(curr_from, curr_to, amount)
    except APIException as e:
        bot.send_message(message.chat.id, f'Ошибка в конвертации:\n{e}')
    else:
        answer_text = f'Стоимость {amount} едениц валюты {curr_from.upper()} в валюте {curr_to.upper()}: {conv}\n\n'
        answer_text += f"{amount} {curr_from.upper()} = {conv} {curr_to.upper()}"
        bot.send_message(message.chat.id, answer_text, reply_markup=COMMANDS_BUTTONS)


if __name__ == '__main__':
    bot.infinity_polling()