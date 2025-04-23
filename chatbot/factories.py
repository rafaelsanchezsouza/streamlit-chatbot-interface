from chatbot.services.file_service import LocalFileSystem
from chatbot.services.database_service import ShelveDatabaseService
from chatbot.services.llm_service import OpenAILLMService
from chatbot.interfaces import LLMService, DatabaseService
import os

class LLMFactory:
    @staticmethod
    def get_llm_service(model: str) -> LLMService:
        if model == "o4-mini":
            return OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model=model)
        if model == "gpt-4.1":
            return OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"), model=model)
        # Add more LLM services as needed

class DatabaseFactory:
    @staticmethod
    def get_database_service(db_type: str) -> DatabaseService:
        if db_type == "shelve":
            return ShelveDatabaseService()
        # Add more database services as needed

class FileSystemFactory:
    @staticmethod
    def get_file_system(file_system_type: str):
        if file_system_type == "local":
            return LocalFileSystem()
        # Add other implementations as needed
