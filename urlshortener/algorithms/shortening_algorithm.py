from abc import ABCMeta, abstractmethod
from enum import Enum


class ShorteningAlgorithmType(Enum):
    BASE64 = "base-64"
    SHA256 = "sha256"

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self):
        return str(self.value)


class ShorteningAlgorithm(metaclass=ABCMeta):

    @abstractmethod
    def shorten(self, url) -> str:
        raise NotImplementedError

    @abstractmethod
    def type(self) -> ShorteningAlgorithmType:
        raise NotImplementedError

    def __str__(self) -> str:
        return str(self.type())

    def __repr__(self):
        return str(self.type())
