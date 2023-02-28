import os
import re

from dotenv import load_dotenv
from flask import Flask, request
from bangkok_request import LastUSDToTHBRates
from tinkoff_request import LastUSDToRUBRates
import telebot
from bangkok_request import BankAPI


# class ZDVTelebot(BankAPI):
#     def __init__(self, token_name):
#         self.token = token_name
#
#     def get_token(self):
#         load_dotenv(os.path.abspath('.env'))
#         return os.environ.get(self.token_name)
#
#     def get(self):
#         bot = telebot.TeleBot(token=self.get_token())


class ExchangeConvertor:
    """
    класс для определения конверсии из RUB в THB с учетом и без учета комиссии
    """

    def __init__(self):
        """
        метод инициализации, в котором определяем текущие котировки валют
        """
        self.usd_rub = 0
        self.usd_rub_message = ''
        self.usd_thb = 0
        self.usd_thb_message = ''

    def get_usd_rub_data(self):
        """
        метод определения курса обмена покупка USD за RUB, через Тинькофф банк
        и получение текстового сообщения о дополнительных деталях
        :return: -> float() , str() значение курса, строку с дополнительной информацией
        """
        if self.usd_rub != 0:
            return True
        self.usd_rub, self.usd_rub_message = LastUSDToRUBRates().get_usd_last_rate()
        return True

    def get_usd_thb_data(self):
        """
        метод обмена валюты продажа USD за THB, через  Bangkok Bank
        И получечние текстового сообщения о дополнительной информации
        :return: -> float() , str() значение курса, строку с дополнительной информацией
        """
        if self.usd_thb != 0 and self.usd_thb_message != '':
            return True
        self.usd_thb, self.usd_thb_message = LastUSDToTHBRates().get_usd_to_thb_rates()
        return True

    def get_thb_rub_rate(self, swift=3.0, thb_exange=0.21, raif_exgande=2.257):
        """
        метод определения обмена валюты RUB в THB
        :param swift: -> float() комиссия банка Райфайзен за Swift перевод
        :param thb_exange: -> float() комиссия банка BangkokBank за прием Swfit перевода и операции пополнения счета
        :param raif_exgande: -> float() комиссия броке Райфайзен банка за совершение брокерской операции
        :return: -> float() , float() значение курса, значение курса с комиссией
        """
        # проверка ненулевых значений котировок, для просчета курса обмена
        if self.usd_thb == 0:
            self.get_usd_thb_data()
        if self.usd_rub == 0:
            self.get_usd_rub_data()
        # формула расчета конверсии 1 RUB в THB
        thb_rub = float(self.usd_thb) / float(self.usd_rub) * (1 - raif_exgande / 100) * (1 - swift / 100) * (
                1 - thb_exange / 100)
        # формула обмена 1 THB к RUB
        rub_thb = round(1 / thb_rub, 2)
        rub_thb_zdv = round(rub_thb * 1.02, 2)
        return rub_thb, rub_thb_zdv

    def get_exchange_message_rub_thb(self):
        """
        метод определяющий финальное сообщение значения обмена 1 THB к RUB
        :return: -> float() , str() значение курса, строку с дополнительной информацией
        """
        rub_thb, rub_thb_zdv = self.get_thb_rub_rate()
        message_out = f"RUB / THB   : {rub_thb}\n" \
                      f"RUB / THB*  : {rub_thb_zdv}" \
                      f"\n"
        return rub_thb_zdv, message_out


def buy_rub_knowing_rub(value, rate):
    return value / rate


def buy_rub_knowing_thb(value, rate):
    return value * rate


load_dotenv(os.path.abspath('.env'))
TOKEN = os.environ.get('TELEBOT')
bot = telebot.TeleBot(token=TOKEN)
server = Flask(__name__)

bot_bank_connect = ExchangeConvertor()


@bot.message_handler(commands=['info'])
def send_all_info(message):
    rate, message_out = bot_bank_connect.get_exchange_message_rub_thb()
    bot.send_message(message.from_user.id,
                     bot_bank_connect.usd_rub_message + bot_bank_connect.usd_thb_message + message_out)


@bot.message_handler(commands=['test'])
def send_test_message(message):
    bot.send_message(message.from_user.id, 'test_response')


@bot.message_handler(commands=['usd'])
def send_usd_rate(message):
    bot_bank_connect.get_usd_rub_data()
    usd_rate, message_in = bot_bank_connect.usd_rub, bot_bank_connect.usd_rub_message
    bot.send_message(message.from_user.id, message_in)


@bot.message_handler(commands=['thb'])
def send_thb_rate(message):
    bot_bank_connect.get_usd_thb_data()
    thb_rate, message_in = bot_bank_connect.usd_thb, bot_bank_connect.usd_thb_message
    bot.send_message(message.from_user.id, message_in)


@bot.message_handler(commands=['%'])
def send_commission_only(message):
    rate, message_in_out = bot_bank_connect.get_exchange_message_rub_thb()
    bot.send_message(message.from_user.id, message_in_out)


@bot.message_handler(commands=['ex', 'exchange', 'money'])
def handle_rate_message(message):
    bot.send_message(message.from_user.id, f'!!!!!!Enter yor rate or skip!!!!!!!')
    bot.register_next_step_handler(message, handle_message)


def handle_message(message):
    global rate
    try:
        value_rate = message.text.upper()
        value_rate = re.search(r"\d+\.?\d*", value_rate)
        rate = float(value_rate.group(0))
    except:
        rate, message_out = ExchangeConvertor().get_exchange_message_rub_thb()
    bot.send_message(message.from_user.id, f'Ready to convert with rate {rate}\n'
                                           f'Enter amount of money with THB to RUB in the end')
    bot.register_next_step_handler(message, get_money_value)


def get_money_value(message):
    value = message.text
    if value.upper() == "END":
        bot.send_message(message.from_user.id, f'Exchange operation have been done')
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        return

    input_value = re.search(r"^(?P<value>\d+)(?P<name>(THB|RUB|))$", value.upper())

    if input_value is None:
        bot.send_message(message.from_user.id, f'Incorrect Input')
        bot.register_next_step_handler(message, get_money_value)
        return

    value_money = input_value.group('value')
    name_money = input_value.group('name')

    value_money = 0 if value_money is None else int(value_money)

    if name_money == 'RUB' or name_money == '':
        message_out = f"I will convert RUB to THB\n" \
                      f"{value_money}RUB = {round(value_money / rate, 2)}THB"
    else:
        message_out = f"I will convert THB to RUB\n" \
                      f"{value_money}THB = {round(value_money * rate, 2)}RUB"

    bot.send_message(message.from_user.id, message_out)

    bot.register_next_step_handler(message, get_money_value)


bot.delete_webhook()


# bot.infinity_polling()

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{os.environ.get['URL_HEROKU']}/" + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
