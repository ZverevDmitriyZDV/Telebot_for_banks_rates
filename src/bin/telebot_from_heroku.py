from src.listener.telebot_listener import TelegramBotClient

if __name__ == "__main__":
    bot = TelegramBotClient()
    bot.run_heroku_server()
