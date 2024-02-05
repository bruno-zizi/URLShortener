from urlshortener.algorithms.base_64 import Base64ShorteningAlgorithm
from urlshortener.algorithms.sha256 import Sha256ShorteningAlgorithm

from urlshortener.algorithms.shortening_algorithm import (
    ShorteningAlgorithmType,
    ShorteningAlgorithm,
)

factory_config = {
    ShorteningAlgorithmType.BASE64: Base64ShorteningAlgorithm(),
    ShorteningAlgorithmType.SHA256: Sha256ShorteningAlgorithm(),
}


class ShorteningAlgorithmFactory:

    def get(self, algorithm_type: ShorteningAlgorithmType) -> ShorteningAlgorithm:
        if algorithm_type in factory_config:
            return factory_config[algorithm_type]
        else:
            raise NotImplementedError("Unknown shortening algorithm type")
