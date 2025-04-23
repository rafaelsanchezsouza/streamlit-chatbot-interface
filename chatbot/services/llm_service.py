from openai import OpenAI
from config import environment
from chatbot.interfaces import LLMService

class OpenAILLMService(LLMService):
    def __init__(self, api_key, model):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def query(self, messages):
        for response in self.client.chat.completions.create(model=self.model, messages=messages, stream=True):
            yield response
