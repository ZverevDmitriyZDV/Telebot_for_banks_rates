from src.config.configurator import AppConfiguration
from src.listener.telebot_listener import TelegramBotClient

if __name__ == "__main__":
    conf = AppConfiguration()
    tel = TelegramBotClient(conf)
    tel.run_infinity_poll()
