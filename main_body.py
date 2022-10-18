import os
import re
from flask import Flask, request
from bangkok_request import get_bangkok_usd_rate_inner
from tinkoff_request import get_rate_usd
import telebot

TOKEN = os.environ["TELEBOT"]
bot = telebot.TeleBot(token=TOKEN)
server = Flask(__name__)


def get_exchange_rub_thb(all: object = True):
    usd_rate, message_in = get_usd_rub()
    thb_rate, message_in_2 = get_thb_usd()
    rub_thb, rub_thb_zdv = get_thb_rub_rate(usd_rate, thb_rate)
    message_in_out = f"RUB / THB   : {rub_thb}\n" \
                     f"RUB / THB*  : {rub_thb_zdv}" \
                     f"\n"

    message_in_out = message_in + message_in_2 + message_in_out if all else message_in_out

    return rub_thb_zdv, message_in_out


def get_thb_rub_rate(usd_rate, thb_usd_rate, swift=3.0, thb_exange=0.21, raif_exgande=2.257):
    thb_rub = float(thb_usd_rate) / float(usd_rate) * (1 - raif_exgande / 100) * (1 - swift / 100) * (
            1 - thb_exange / 100)
    rub_thb = round(1 / thb_rub, 2)
    rub_thb_zdv = round(rub_thb * 1.02, 2)
    return rub_thb, rub_thb_zdv


def get_usd_rub():
    data_message = get_rate_usd()
    usd_rate = data_message.get("max_rate_with_ema")
    message_in = f"USD   : {data_message.get('max_rate')}\n" \
                 f"USD ema: {usd_rate}\n" \
                 f"Update : {data_message.get('time')}\n" \
                 f"\n"
    return usd_rate, message_in


def get_thb_usd():
    thb_rate = get_bangkok_usd_rate_inner()
    message_in = f"THB         : {thb_rate.get('tt_rate')}\n" \
                 f"Update: {thb_rate.get('time')} {thb_rate.get('date')}\n" \
                 f"\n"
    return thb_rate.get('tt_rate'), message_in


def buy_rub_knowing_rub(value, rate):
    return value / rate


def buy_rub_knowing_thb(value, rate):
    return value * rate


@bot.message_handler(commands=['info'])
def send_all_info(message):
    rate, message_out = get_exchange_rub_thb(all=True)
    bot.send_message(message.from_user.id, message_out)


@bot.message_handler(commands=['test'])
def send_all_info(message):
    bot.send_message(message.from_user.id, 'test2')


@bot.message_handler(commands=['usd'])
def send_usd_rate(message):
    usd_rate, message_in = get_usd_rub()
    bot.send_message(message.from_user.id, message_in)


@bot.message_handler(commands=['thb'])
def send_thb_rate(message):
    thb_rate, message_in = get_thb_usd()
    bot.send_message(message.from_user.id, message_in)


@bot.message_handler(commands=['%'])
def send_commission_only(message):
    rate, message_in_out = get_exchange_rub_thb(all=False)
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
        rate, message_out = get_exchange_rub_thb(all=False)
    bot.send_message(message.from_user.id, f'Ready to convert with rate {rate}\n'
                                           f'Enter amount of money with THB ot RUB in the end')
    bot.register_next_step_handler(message, get_money_value)


def get_money_value(message):
    value = message.text.upper()
    if value == "END":
        bot.send_message(message.from_user.id, f'Я сделяль')
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        return

    input_value = re.search(r"^(?P<value>\d+)(?P<name>(THB|RUB|))$", value)

    if input_value is None:
        bot.send_message(message.from_user.id, f'Некорректный ввод')
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


@server.route('/' + TOKEN, methods=['POST'])
async def getMessage():
    json_string = await request.get_data().decode('utf-8')
    update = await telebot.types.Update.de_json(json_string)
    await bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://testbotherokuzdv.herokuapp.com/' + TOKEN)
    return "!", 200

# if __name__ == "__main__":
#     server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
