from unittest.mock import patch, MagicMock

import pytest
import typer

from urlshortener.algorithms.sha256 import Sha256ShorteningAlgorithm
from urlshortener.cli import main
from urlshortener.repository.mongo_repository import MongoURLRepository


@pytest.fixture()
def mock_mongo_repository(monkeypatch):
    repo_mock = MagicMock()

    def mock_method(*args, **kwargs):
        return repo_mock

    monkeypatch.setattr(MongoURLRepository, "initialize", mock_method)
    monkeypatch.setattr(MongoURLRepository, "finalize", mock_method)
    yield repo_mock


@pytest.fixture(scope="function")
def mock_url_shortener():
    fake_shortener = MagicMock()
    with patch("urlshortener.cli.URLShortener") as url_shortener_mock:
        url_shortener_mock.return_value = fake_shortener
        yield fake_shortener


@pytest.fixture()
def mock_algorithm_factory():
    fake_factory = MagicMock()
    with patch("urlshortener.cli.ShorteningAlgorithmFactory") as algorithm_factory_mock:
        algorithm_factory_mock.return_value = fake_factory
        fake_factory.get.return_value = Sha256ShorteningAlgorithm()
        yield fake_factory


class TestCLI:

    def test_no_options_are_provided(self):
        url_to_minify = None
        url_to_expand = None

        with pytest.raises(typer.BadParameter) as exc_info:
            main(url_to_minify, url_to_expand)

        assert (
            str(exc_info.value) == "Please specify either --minify or --expand option"
        )

    def test_invalid_minify_option_is_provided(self):
        url_to_minify = "https://"
        url_to_expand = None

        with pytest.raises(typer.BadParameter) as exc_info:
            main(url_to_minify, url_to_expand)

        assert str(exc_info.value) == f"'{url_to_minify}' is not a valid URL"

    def test_invalid_expand_option_is_provided(self):
        url_to_minify = None
        url_to_expand = "test.com"

        with pytest.raises(typer.BadParameter) as exc_info:
            main(url_to_minify, url_to_expand)

        assert str(exc_info.value) == f"'{url_to_expand}' is not a valid URL"

    def test_shortener_minify_is_invoked(
        self, mock_mongo_repository, mock_url_shortener, mock_algorithm_factory
    ):
        the_algorithm = Sha256ShorteningAlgorithm()
        mock_algorithm_factory.get.return_value = the_algorithm

        main(url_to_minify="https://www.example.com/lorem/ipsum")

        mock_url_shortener.minify.assert_called_once_with(
            url="https://www.example.com/lorem/ipsum", algorithm=the_algorithm
        )
        mock_url_shortener.expand.assert_not_called()

    def test_shortener_expand_is_invoked(
        self, mock_mongo_repository, mock_url_shortener, mock_algorithm_factory
    ):
        the_algorithm = Sha256ShorteningAlgorithm()
        mock_algorithm_factory.get.return_value = the_algorithm

        main(url_to_expand="https://www.example.com/a1RRsfs")

        mock_url_shortener.expand.assert_called_once_with(
            short_url="https://www.example.com/a1RRsfs", algorithm=the_algorithm
        )
        mock_url_shortener.minify.assert_not_called()
