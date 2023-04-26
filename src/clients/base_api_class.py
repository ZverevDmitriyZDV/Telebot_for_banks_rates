from abc import ABC, abstractmethod


class BankAPI(ABC):
    url: str

    @abstractmethod
    def get_data(self, *args, **kwargs):
        pass
