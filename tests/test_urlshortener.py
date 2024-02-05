from unittest.mock import Mock

import pytest

from urlshortener.algorithms.shortening_algorithm import ShorteningAlgorithmType
from urlshortener.url_shortener import URLShortener


class TestURLShortener:

    def test_minify_url_not_minified(self):
        url_to_minify = "https://www.example.com/test?q=123"
        algorithm = Mock()
        algorithm.type.return_value = ShorteningAlgorithmType.BASE64
        algorithm.shorten.return_value = "shorten_part"
        repository = Mock()
        repository.get_short_url.return_value = None
        short_url = "https://www.example.com/shorten_part"
        repository.save_url_mapping.return_value = None
        url_shortener = URLShortener(repository)

        result = url_shortener.minify(url_to_minify, algorithm)

        repository.get_short_url.assert_called_once_with(
            original_url=url_to_minify, algorithm=ShorteningAlgorithmType.BASE64.value
        )
        algorithm.shorten.assert_called_once_with(url=url_to_minify)
        repository.save_url_mapping.assert_called_once_with(
            original_url=url_to_minify,
            short_url=short_url,
            algorithm="base-64",
        )
        assert result == short_url

    def test_minify_url_already_minified(self):
        url = "https://www.example.com/test?q=123"
        algorithm = Mock()
        algorithm.type.return_value = ShorteningAlgorithmType.BASE64
        repository = Mock()
        repository.get_short_url.return_value = "https://example.com/Hs2s1aD"
        url_shortener = URLShortener(repository)

        result = url_shortener.minify(url, algorithm)

        repository.get_short_url.assert_called_once_with(
            original_url=url, algorithm="base-64"
        )
        algorithm.shorten.assert_not_called()
        repository.save_url_mapping.assert_not_called()
        assert result == "https://example.com/Hs2s1aD"

    def test_expand_existing_short_url(self):
        short_url = "https://example.com/Hs2s1aD"
        algorithm = Mock()
        algorithm.type.return_value = ShorteningAlgorithmType.BASE64
        repository = Mock()
        repository.get_original_url.return_value = "https://www.example.com/test?q=123"
        url_shortener = URLShortener(repository)

        result = url_shortener.expand(short_url, algorithm)

        repository.get_original_url.assert_called_once_with(
            short_url=short_url, algorithm="base-64"
        )
        assert result == "https://www.example.com/test?q=123"

    def test_minify_url_invalid_algorithm(self):
        url = "https://www.example.com/test?q=123"
        algorithm = None
        repository = Mock()
        repository.get_short_url.return_value = None
        url_shortener = URLShortener(repository)

        with pytest.raises(ValueError):
            url_shortener.minify(url, algorithm)

        repository.get_short_url.assert_not_called()
        repository.save_url_mapping.assert_not_called()

    def test_minify_url_empty_string(self):
        url = ""
        algorithm = Mock()
        algorithm.type.return_value = ShorteningAlgorithmType.BASE64
        repository = Mock()
        repository.get_short_url.return_value = None
        url_shortener = URLShortener(repository)

        with pytest.raises(ValueError):
            url_shortener.minify(url, algorithm)

        repository.get_short_url.assert_not_called()
        algorithm.shorten.assert_not_called()
        repository.save_url_mapping.assert_not_called()

    def test_minify_url_no_domain(self):
        url = "https://"
        algorithm = Mock()
        algorithm.type.return_value = ShorteningAlgorithmType.BASE64
        repository = Mock()
        repository.get_short_url.return_value = None
        url_shortener = URLShortener(repository)

        with pytest.raises(ValueError):
            url_shortener.minify(url, algorithm)

        repository.get_short_url.assert_called_once_with(
            original_url=url, algorithm="base-64"
        )
        algorithm.shorten.assert_not_called()
        repository.save_url_mapping.assert_not_called()
