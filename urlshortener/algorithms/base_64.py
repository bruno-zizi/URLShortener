import base64
import logging

from urlshortener.algorithms.shortening_algorithm import (
    ShorteningAlgorithmType,
    ShorteningAlgorithm,
)


class Base64ShorteningAlgorithm(ShorteningAlgorithm):

    def __init__(self):
        self._log = logging.getLogger(self.__class__.__name__)

    def type(self) -> ShorteningAlgorithmType:
        return ShorteningAlgorithmType.BASE64

    def shorten(self, url) -> str:
        self._log.debug(f"Shortening URL: {url}")
        return base64.b64encode(url.encode()).decode()[:8]
