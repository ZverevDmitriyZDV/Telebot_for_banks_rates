import os
import re
from dotenv import load_dotenv

import telebot
from flask import Flask, request

from convertor import ExchangeConvertor
from units import buy_rub_knowing_thb, buy_rub_knowing_rub


class TelegramBotClient:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token=token)
        self.bot_bank_connect = ExchangeConvertor()

        @self.bot.message_handler(commands=["info"])
        def _send_all_info(message):
            self.send_all_info(message)

        @self.bot.message_handler(commands=['test'])
        def _send_test_message(message):
            self.send_test_message(message)

        @self.bot.message_handler(commands=['usd'])
        def _send_usd_rate(message):
            self.send_usd_rate(message)

        @self.bot.message_handler(commands=['thb'])
        def _send_thb_rate(message):
            self.send_thb_rate(message)

        @self.bot.message_handler(commands=['%'])
        def _send_commission_only(message):
            self.send_commission_only(message)

        @self.bot.message_handler(commands=['ex', 'exchange', 'money'])
        def _handle_rate_message(message):
            self.bot.send_message(message.from_user.id, f'!!!!!!Enter yor rate or skip!!!!!!!')
            self.bot.register_next_step_handler(message, self.handle_message)

    def send_all_info(self, message):
        rate, message_out = self.bot_bank_connect.get_exchange_message_rub_thb()
        self.bot.send_message(message.from_user.id,
                              self.bot_bank_connect.tink_rates.message +
                              self.bot_bank_connect.thb_rates.message +
                              message_out)

    def send_test_message(self, message):
        self.bot.send_message(message.from_user.id, 'test_response')

    def send_usd_rate(self, message):
        self.bot_bank_connect.get_usd_rub_data()
        usd_rate, message_in = self.bot_bank_connect.tink_rates.rate, self.bot_bank_connect.tink_rates.message
        self.bot.send_message(message.from_user.id, message_in)

    def send_thb_rate(self, message):
        self.bot_bank_connect.get_usd_thb_data()
        thb_rate, message_in = self.bot_bank_connect.thb_rates.rate, self.bot_bank_connect.thb_rates.message
        self.bot.send_message(message.from_user.id, message_in)

    def send_commission_only(self, message):
        rate, message_in_out = self.bot_bank_connect.get_exchange_message_rub_thb()
        self.bot.send_message(message.from_user.id, message_in_out)

    def handle_rate_message(self, message):
        self.bot.send_message(message.from_user.id, f'!!!!!!Enter yor rate or skip!!!!!!!')
        self.bot.register_next_step_handler(message, handle_message)

    def handle_message(self, message):
        global rate
        try:
            value_rate = message.text.upper()
            value_rate = re.search(r"\d+\.?\d*", value_rate)
            rate = float(value_rate.group(0))
        except:
            rate, message_out = ExchangeConvertor().get_exchange_message_rub_thb()
        self.bot.send_message(message.from_user.id, f'Ready to convert with rate {rate}\n'
                                                    f'Enter amount of money with THB to RUB in the end')
        self.bot.register_next_step_handler(message, self.get_money_value)

    def get_money_value(self, message):
        value = message.text
        if value.upper() == "END":
            self.bot.send_message(message.from_user.id, f'Exchange operation have been done')
            self.bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
            return

        input_value = re.search(r"^(?P<value>\d+)(?P<name>(THB|RUB|))$", value.upper())

        if input_value is None:
            self.bot.send_message(message.from_user.id, f'Incorrect Input')
            self.bot.register_next_step_handler(message, self.get_money_value)
            return

        value_money = input_value.group('value')
        name_money = input_value.group('name')

        value_money = 0 if value_money is None else int(value_money)

        if name_money == 'RUB' or name_money == '':
            message_out = f"I will convert RUB to THB\n" \
                          f"{value_money}RUB = {buy_rub_knowing_rub(value=value_money, rate=rate)}THB"
        else:
            message_out = f"I will convert THB to RUB\n" \
                          f"{value_money}THB = {buy_rub_knowing_thb(value=value_money, rate=rate)}RUB"

        self.bot.send_message(message.from_user.id, message_out)

        self.bot.register_next_step_handler(message, self.get_money_value)

    def run_infinity_poll(self):
        self.bot.delete_webhook()
        self.bot.infinity_polling()

    def run_heroku_server(self):
        server = Flask(__name__)

        @server.route('/' + TOKEN, methods=['POST'])
        def getMessage():
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            self.bot.process_new_updates([update])
            return "!", 200

        @server.route("/")
        def webhook():
            self.bot.remove_webhook()
            self.bot.set_webhook(url=f"{os.environ.get['URL_HEROKU']}/" + TOKEN)
            return "!", 200

        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


if __name__ == "__main__":
    load_dotenv(os.path.abspath('.env'))
    TOKEN = os.environ.get('TELEBOT')
    tel = TelegramBotClient(TOKEN)
    tel.run_infinity_poll()
