from mistralai import Mistral
from openai import OpenAI
from ai_provider_strategy import AIProviderStrategy


class MistralStrategy(AIProviderStrategy):
    def __init__(self, api_key, model):
        self.client = Mistral(api_key=api_key)
        self.model = model

    def process(self, prompt):
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ]
            )
            return response  # You can refine this response as needed
        except Exception as e:
            return {"error": f"Failed to process with Mistral: {e}"}


class ChatGPTStrategy(AIProviderStrategy):
    def __init__(self, api_key, model):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def process(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            return {"error": f"Failed to process with ChatGPT: {e}"}


class AIProcessor:
    def __init__(self, strategy: AIProviderStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: AIProviderStrategy):
        self._strategy = strategy

    def process(self, prompt):
        return self._strategy.process(prompt)
