from abc import ABC, abstractmethod


class BankAPI(ABC):
    url: str

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def get_token(self):
        """
        получение сохраненного токена из файл .env или окружения HEROKU / GIT в зависимости от ресурса на котором
        будет произведено развертывание проекта.
        :return: токен доступа для подключения к клиенту
        """
        pass
