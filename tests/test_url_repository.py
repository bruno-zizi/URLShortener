from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest
from freezegun import freeze_time

from urlshortener.repository.mongo_repository import MongoURLRepository
from urlshortener.settings import ShortenerSettings


class TestURLRepository:

    @freeze_time("2024-01-01")
    @patch("pymongo.MongoClient")
    def test_can_save_url_mapping(self, _):
        settings = ShortenerSettings()

        with MongoURLRepository(settings) as repository:
            mock_collection = MagicMock()
            repository._url_collection = mock_collection
            original_url = "https://www.example.com"
            short_url = "abc123"
            algorithm = "BASE64"

            repository.save_url_mapping(original_url, short_url, algorithm)

            mock_collection.update_one.assert_called_once_with(
                filter={
                    "algorithm": "BASE64",
                    "original_url": "https://www.example.com",
                },
                update={
                    "$set": {
                        "algorithm": "BASE64",
                        "original_url": "https://www.example.com",
                        "short_url": "abc123",
                        "expiration_time": int(
                            datetime.utcnow().timestamp() + settings.expiration_offset
                        ),
                        "creation_time": int(datetime.utcnow().timestamp()),
                    }
                },
                upsert=True,
            )

    @patch("pymongo.MongoClient")
    def test_init_on_missing_collection(self, mock_client):
        mock_client.return_value = MagicMock()
        settings = ShortenerSettings()
        collection_name = settings.mongo_url_collection
        mock_collection = MagicMock()
        mock_collection.create_index.return_value = False
        mock_db = MagicMock()
        mock_db.list_collection_names.return_value = []
        mock_db.create_collection.return_value = mock_collection
        mock_db.__getitem__.return_value = mock_collection
        mock_client.return_value.__getitem__.return_value = mock_db

        with MongoURLRepository(settings):
            mock_db.create_collection.assert_called_once_with(collection_name)
            mock_collection.create_index.assert_called_with(["algorithm", "short_url"])

    @freeze_time("2024-01-01")
    @patch("pymongo.MongoClient")
    def test_can_handle_missing_url_mapping(self, _):
        settings = ShortenerSettings()
        mock_collection = MagicMock()
        with MongoURLRepository(settings) as repository:
            repository._url_collection = mock_collection
            original_url = "https://www.example.com"
            algorithm = "BASE64"
            mock_collection.find_one.return_value = None

            short_url = repository.get_short_url(original_url, algorithm)

            mock_collection.find_one.assert_called_once_with(
                {
                    "original_url": original_url,
                    "expiration_time": {"$gt": int(datetime.utcnow().timestamp())},
                    "algorithm": algorithm,
                }
            )
            assert short_url is None

    @patch("pymongo.MongoClient")
    def test_can_retrieve_short_url(self, _):
        settings = ShortenerSettings()

        with MongoURLRepository(settings) as repository:
            mock_collection = MagicMock()
            repository._url_collection = mock_collection
            original_url = "https://www.example.com"
            short_url = "abc123"
            algorithm = "BASE64"

            mock_collection.find_one.return_value = {
                "original_url": original_url,
                "short_url": short_url,
                "expiration_time": int(datetime.utcnow().timestamp())
                + settings.expiration_offset,
                "algorithm": algorithm,
            }

            result = repository.get_short_url(original_url, algorithm)
            assert result == short_url

    @patch("pymongo.MongoClient")
    def test_can_retrieve_original_url(self, _):
        settings = ShortenerSettings()

        with MongoURLRepository(settings) as repository:
            mock_collection = MagicMock()
            repository._url_collection = mock_collection
            original_url = "https://www.example.com"
            short_url = "abc123"
            algorithm = "BASE64"

            mock_collection.find_one.return_value = {
                "original_url": original_url,
                "short_url": short_url,
                "expiration_time": int(datetime.utcnow().timestamp())
                + settings.expiration_offset,
                "algorithm": algorithm,
            }

            result = repository.get_original_url(short_url, algorithm)

            assert result == original_url

    @patch("pymongo.MongoClient")
    def test_repo_not_initialized_raises_an_error(self, _):
        settings = ShortenerSettings()

        with pytest.raises(Exception):
            MongoURLRepository(settings).get_short_url(
                original_url="http://www.example.com/lorem/ipsum", algorithm="BASE64"
            )
