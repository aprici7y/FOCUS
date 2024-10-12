from abc import ABC, abstractmethod


class CreationStrategy(ABC):
    @abstractmethod
    def create(self, playlist_title, video_summaries):
        pass
