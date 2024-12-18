from pathlib import Path
import toml
from typing import Any
from pydantic import BaseModel, model_validator, Field

CONFIG_PATH = Path(__file__).parent / 'config.toml'

class TelegramConfig(BaseModel):
    API_ID: str
    API_HASH: str
    PHONE: str

class VkConfig(BaseModel):
    API_VERSION: str
    AUTH_URL: str
    LOGIN: str
    PWD: str

class Neo4jConfig(BaseModel):
    USERNAME: str
    PASSWORD: str
    URI: str
    DB_NAME: str


class Config(BaseModel):
    config_path: Path | str
    telegram: TelegramConfig
    vkontakte: VkConfig
    neo4j: Neo4jConfig

    @model_validator(mode='before')
    @classmethod
    def load_toml(cls, data: Any) -> Any:
        path = data['config_path']
        if not isinstance(path, Path):
            path = Path(path)

        try:
            # Load the TOML file
            config = toml.load(path)
            config['config_path'] = path
            return config
        except FileNotFoundError:
            print(f"Error: File not found at {path}")
        except Exception as e:
            print(f"Error: {e}")


setting = Config(config_path=CONFIG_PATH)