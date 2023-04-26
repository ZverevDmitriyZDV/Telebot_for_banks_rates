from src.config.configurator import BkkBLogerConfiguration
from src.logger.logger import Zlogger

from typing import Callable

from requests import Response

from src.utils.bad_auth_exception import BadAuthException


conf = BkkBLogerConfiguration()
logger_bkkbanks_logs = Zlogger(conf)


def check_status(msg: str = "default") -> Callable:
    def decorator(f: Callable[..., Response]):
        def wrapper(*args, **kwargs) -> Response:
            resp = f(*args, **kwargs)
            if resp.status_code == 401:
                logger_bkkbanks_logs.error(f'{msg} %s', resp.reason)
                raise BadAuthException(resp.reason)
            return resp

        return wrapper

    return decorator
