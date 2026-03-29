from abc import ABC, abstractmethod


class VideoSourceAdapter(ABC):
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def fetch_metadata(self, url: str) -> dict:
        raise NotImplementedError
