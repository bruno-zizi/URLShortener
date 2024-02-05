import logging
from urllib.parse import urlparse

from urlshortener.algorithms.shortening_algorithm import ShorteningAlgorithm
from urlshortener.repository.repository import URLRepository


class URLShortener:
    def __init__(self, repository: URLRepository, fixed_domain: str = None):
        self._repository = repository
        self._fixed_domain = fixed_domain
        self._log = logging.getLogger(self.__class__.__name__)

    def minify(self, url: str, algorithm: ShorteningAlgorithm) -> str | None:
        if not algorithm:
            raise ValueError("No algorithm specified")
        if not url:
            raise ValueError("No URL specified")

        self._log.debug(f"Minifying URL {url} using algorithm '{algorithm}'")

        existing_url = self._get_shortened_url(url=url, algorithm=algorithm.type())
        if existing_url:
            self._log.debug(f"URL {url} already minified. Returning it.")
            return existing_url

        self._log.debug(f"URL {url} not minified yet.")
        return self._minify_save_url(url=url, algorithm=algorithm)

    def expand(self, short_url: str, algorithm: ShorteningAlgorithm) -> str | None:
        if not algorithm:
            raise ValueError("No algorithm specified")

        if not short_url:
            raise ValueError("No URL specified")

        # Check if the shortened URL is in the database and not expired
        existing_url = self._repository.get_original_url(
            short_url=short_url, algorithm=algorithm.type().value
        )
        if existing_url:
            return existing_url
        else:
            return f"not found or expired"

    def _get_shortened_url(
        self, url: str, algorithm: ShorteningAlgorithm
    ) -> str | None:
        # Check if the URL is already in the database
        existing_url = self._repository.get_short_url(
            original_url=url,
            algorithm=algorithm.value,
        )
        return existing_url

    def _minify_save_url(self, url: str, algorithm: ShorteningAlgorithm) -> str:
        url_domain = self._get_url_domain(url)
        url_hash = algorithm.shorten(url=url)
        short_url = f"{url_domain}{url_hash}"
        self._log.debug(f"URL {url} minified {short_url}. Storing it.")
        self._repository.save_url_mapping(
            original_url=url,
            short_url=short_url,
            algorithm=algorithm.type().value,
        )
        return short_url

    def _get_url_domain(self, url: str) -> str:
        if self._fixed_domain:
            return self._fixed_domain
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid url format")
        return f"{parsed.scheme}://{parsed.netloc}/"
