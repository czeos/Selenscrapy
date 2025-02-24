import configparser
from typing import Any, Dict

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._config = configparser.ConfigParser()
            cls._instance._config.read('telegram/config.ini')
        return cls._instance

    def get(self, section: str, option: str) -> Any:
        return self._instance._config.get(section, option)

    def get_all(self) -> Dict[str, Dict[str, Any]]:
        return {section: dict(self._instance._config.items(section)) for section in self._instance._config.sections()}
    
config = Config()