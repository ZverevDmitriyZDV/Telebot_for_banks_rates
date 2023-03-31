from pydantic import BaseSettings, Field
from functools import cached_property

__DEFAULT_ENVIRONMENTS_PATH__ = 'environments'


class BaseSettingsConfig(BaseSettings.Config):
    env_file_encoding = 'utf-8'


class Environment(BaseSettings):
    path: str = Field(default=__DEFAULT_ENVIRONMENTS_PATH__, env='YENV_PATH')

    class Config(BaseSettingsConfig):
        pass


class BaseConfiguration(BaseSettings):
    def __init__(self, *args, **kwargs):
        super(BaseConfiguration, self).__init__(*args, **kwargs)

    class Config(BaseSettingsConfig):
        env: Environment = Environment()
        env_file = f'{env.path}/.env'
        keep_untouched = (cached_property,)

