from pydantic import Field

from src.config.base_configurator import BaseConfiguration


class BKKBConfiguration(BaseConfiguration):
    token: str = Field(default='', env='TOKEN_BANGKOK')


class TinkBankConfiguration(BaseConfiguration):
    token: str = Field(default='', env='TOKEN_TINK')


class TelegramConfiguration(BaseConfiguration):
    token: str = Field(default='', env='TELEBOT')


class HerokuConfiguration(BaseConfiguration):
    url: str = Field(default='', env='URL_HEROKU')
    port: int = Field(default=5000, env='HEROKU_PORT')
