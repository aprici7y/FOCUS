from abc import ABC, abstractmethod


class CreationStrategy(ABC):
    @abstractmethod
    def create(self, playlist_title, video_summaries):
        pass

    @abstractmethod
    def create_or_update_transcript_overview(self, playlist_title, video_summaries):
        pass
