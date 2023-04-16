from typing import Callable

from tinkoff.invest import RequestError, Client

from src.config.configurator import TinkLogerConfiguration
from src.logger.logger import Zlogger
from src.utils.bad_auth_exception import BadAuthException


conf = TinkLogerConfiguration()
logger_tinkoff_logs = Zlogger(conf=conf)


def check_status_client() -> Callable:
    def decorator(f: Callable[..., Client]):

        def wrapper(*args, **kwargs) -> Client:
            try:
                with f(*args, **kwargs) as client:
                    client.users.get_accounts()
            except RequestError as e:
                error_message = e.metadata.message
                logger_tinkoff_logs.error(error_message)
                raise BadAuthException(error_message)
            return f(*args, **kwargs)

        return wrapper

    return decorator
