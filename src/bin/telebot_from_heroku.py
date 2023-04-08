from src.config.configurator import AppConfiguration
from src.listener.telebot_listener import TelegramBotClient

if __name__ == "__main__":
    conf = AppConfiguration()
    bot = TelegramBotClient(conf)
    bot.run_heroku_server()
