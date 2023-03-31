from typing import Callable

import requests
from requests import Response


def check_status(msg: str = "default"):
    def decorator(f: Callable[..., Response]):
        def wrapper(*args, **kwargs):
            resp = f(*args, **kwargs)
            if resp.status_code == 200:
                print("all ok")
            else:
                print(msg)
        return wrapper
    return decorator


class MyClass:
    def __init__(self, url):
        self.url = url

    def get(self, url_keyword: str) -> Response:
        return requests.get(self.url + '/' + url_keyword)

    @check_status(msg='HUI')
    def get_hui(self):
        return self.get("hui")

    @check_status(msg='PIZDA')
    def get_pizda(self):
        return self.get("pizda")

    @check_status()
    def get_default(self):
        return self.get("default")

    @check_status()
    def get_ok(self):
        return self.get("")


m = MyClass("http://ya.ru")
m.get_hui()
m.get_pizda()
m.get_default()
m.get_ok()