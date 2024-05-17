import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_MODEL = os.getenv('AZURE_OPENAI_MODEL')
    LLM_API_TYPE = os.getenv('LLM_API_TYPE', 'openai')
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'shelve')

settings = Settings()