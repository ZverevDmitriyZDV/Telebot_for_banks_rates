import os
from abc import ABC, abstractmethod

from dotenv import load_dotenv


class BankAPI(ABC):
    url: str

    @abstractmethod
    def get_data(self):
        pass

    def get_token(self, token_name: str):
        """
        получение сохраненного токена из файл .env или окружения HEROKU / GIT в зависимости от ресурса на котором
        будет произведено развертывание проекта.
        :return: токен доступа для подключения к клиенту
        """
        load_dotenv(os.path.abspath('.env'))
        return os.environ.get(token_name)