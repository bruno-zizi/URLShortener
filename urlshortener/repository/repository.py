from abc import ABCMeta, abstractmethod


class URLRepository(metaclass=ABCMeta):

    @abstractmethod
    def save_url_mapping(self, original_url: str, short_url: str, algorithm: str):
        raise NotImplementedError

    @abstractmethod
    def get_short_url(self, original_url: str, algorithm: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def get_original_url(self, short_url: str, algorithm: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def reset(self):
        raise NotImplementedError
