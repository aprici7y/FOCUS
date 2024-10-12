from abc import ABC, abstractmethod


class AIProviderStrategy(ABC):
    @abstractmethod
    def process(self, prompt):
        pass
