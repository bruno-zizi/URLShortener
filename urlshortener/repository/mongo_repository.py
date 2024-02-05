import logging
from datetime import datetime

import pymongo

from urlshortener.repository.repository import URLRepository
from urlshortener.settings import ShortenerSettings


def _current_date_in_seconds() -> int:
    return int(datetime.utcnow().timestamp())


class MongoURLRepository(URLRepository):
    def __init__(self, settings: ShortenerSettings):
        self._settings = settings
        self._log = logging.getLogger(self.__class__.__name__)
        self._initialized = False
        self._expiration_offset = self._settings.expiration_offset

    def _init_collection(self, client: pymongo.MongoClient):
        self._log.debug("initializing url mongo collection")
        db = self._client[self._settings.database_name]
        if self._settings.mongo_url_collection not in db.list_collection_names():
            self._log.debug(
                f"creating collection '{self._settings.mongo_url_collection}'"
            )
            self._url_collection = db.create_collection(
                self._settings.mongo_url_collection
            )
            self._url_collection.create_index(["algorithm", "original_url"])
            self._url_collection.create_index(["algorithm", "short_url"])
        else:
            self._log.debug(
                f"collection '{self._settings.mongo_url_collection}' already exists"
            )
            self._url_collection = db[self._settings.mongo_url_collection]

    def initialize(self):
        self._log.debug("initializing MongoURLRepository")
        if self._initialized:
            self._log.debug("MongoURLRepository is already initialized")
            return
        self._log.debug("opening mongo connection")
        self._client = pymongo.MongoClient(self._settings.mongo_instance_url)
        self._init_collection(self._client)
        self._initialized = True
        return self

    def finalize(self):
        self._log.debug("closing mongo client")
        self._client.close()
        self._initialized = False

    def __enter__(self):
        return self.initialize()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finalize()

    def _check_initialization(func):
        # a decorator to enforce initialization in a pythonic way
        def wrap_check_initialization(self, *args, **kwargs):
            if not self._initialized:
                raise Exception("MongoURLRepository is not initialized")
            return func(self, *args, **kwargs)

        return wrap_check_initialization

    @_check_initialization
    def save_url_mapping(self, original_url: str, short_url: str, algorithm: str):
        current_time = _current_date_in_seconds()
        expiration_time = current_time + self._expiration_offset
        doc = {
            "algorithm": algorithm,
            "original_url": original_url,
            "short_url": short_url,
            "expiration_time": expiration_time,
            "creation_time": current_time,
        }
        self._log.debug(f"Storing {doc}")
        self._url_collection.update_one(
            filter={"algorithm": algorithm, "original_url": original_url},
            update={"$set": doc},
            upsert=True,
        )

    @_check_initialization
    def get_short_url(self, original_url: str, algorithm: str) -> str | None:
        self._log.debug(f"retrieving original url {original_url} ({algorithm})")
        existing_url = self._url_collection.find_one(
            {
                "original_url": original_url,
                "expiration_time": {"$gt": _current_date_in_seconds()},
                "algorithm": algorithm,
            }
        )
        if existing_url:
            return existing_url["short_url"]

        self._log.debug(f"url {original_url} ({algorithm}) not found or expired")
        return None

    @_check_initialization
    def get_original_url(self, short_url: str, algorithm: str) -> str | None:
        self._log.debug(f"retrieving short url {short_url} ({algorithm})")
        existing_url = self._url_collection.find_one(
            {
                "short_url": short_url,
                "expiration_time": {"$gt": _current_date_in_seconds()},
                "algorithm": algorithm,
            }
        )
        if existing_url:
            return existing_url["original_url"]

        self._log.debug(f"url {short_url} ({algorithm}) not found or expired")
        return None

    @_check_initialization
    def reset(self):
        self._log.debug(f"resetting repository")
        self._url_collection.delete_many({})
