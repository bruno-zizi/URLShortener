from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from urlshortener.algorithms.shortening_algorithm import ShorteningAlgorithmType


class ShortenerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="urlshortener_"
    )
    mongo_instance_url: str = Field(default="mongodb://localhost:27017/")
    database_name: str = Field(default="urlshortener")
    expiration_offset: int = Field(default=3600, gt=0)  # 1 hour by default
    mongo_url_collection: str = Field(default="urls")
    shortening_algorithm: ShorteningAlgorithmType = Field(
        default=ShorteningAlgorithmType.BASE64
    )
    fixed_domain: Optional[str] = Field(default=None)
