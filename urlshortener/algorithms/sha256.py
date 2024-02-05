import hashlib
import logging

from urlshortener.algorithms.shortening_algorithm import (
    ShorteningAlgorithmType,
    ShorteningAlgorithm,
)


class Sha256ShorteningAlgorithm(ShorteningAlgorithm):

    def __init__(self):
        self._log = logging.getLogger(self.__class__.__name__)

    def type(self) -> ShorteningAlgorithmType:
        return ShorteningAlgorithmType.SHA256

    def shorten(self, url) -> str:
        self._log.debug(f"Shortening URL: {url}")
        return hashlib.sha256(url.encode()).hexdigest()[:8]
