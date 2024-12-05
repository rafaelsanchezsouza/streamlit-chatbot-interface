from openai import AzureOpenAI
from config import environment
from chatbot.interfaces import LLMService

class OpenAILLMService(LLMService):
    def __init__(self, api_key, endpoint):
        self.client = AzureOpenAI(api_key=api_key, api_version="2024-06-01", azure_endpoint=endpoint)

    def query(self, messages):
        for response in self.client.chat.completions.create(model="gpt-4o-Global-Standard", messages=messages, stream=True):
            yield response
