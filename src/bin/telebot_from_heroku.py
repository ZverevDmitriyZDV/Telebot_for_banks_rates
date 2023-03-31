import os
from dotenv import load_dotenv

from src.listener.telebot_listener import TelegramBotClient

if __name__ == "__main__":
    load_dotenv(os.path.abspath('../../.env'))
    TOKEN = os.environ.get('TELEBOT')
    bot = TelegramBotClient(TOKEN)
    bot.run_heroku_server()
