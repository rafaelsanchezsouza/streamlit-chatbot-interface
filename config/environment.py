import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    WEST_AZURE_OPENAI_API_KEY = os.getenv('WEST_AZURE_OPENAI_API_KEY')
    WEST_AZURE_OPENAI_ENDPOINT = os.getenv('WEST_AZURE_OPENAI_ENDPOINT')
    WEST_AZURE_MODEL = os.getenv('WEST_AZURE_OPENAI_MODEL')
    WEST_AZURE_API_VERSION = os.getenv('WEST_AZURE_OPENAI_API_VERSION')
    EAST_AZURE_OPENAI_API_KEY = os.getenv('EAST_AZURE_OPENAI_API_KEY')
    EAST_AZURE_OPENAI_ENDPOINT = os.getenv('EAST_AZURE_OPENAI_ENDPOINT')
    DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'shelve')

settings = Settings()