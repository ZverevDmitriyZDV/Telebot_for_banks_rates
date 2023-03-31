from src.listener.telebot_listener import TelegramBotClient

if __name__ == "__main__":
    tel = TelegramBotClient()
    tel.run_infinity_poll()
