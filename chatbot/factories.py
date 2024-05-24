from chatbot.services.file_service import LocalFileSystem
from chatbot.services.database_service import ShelveDatabaseService
from chatbot.services.llm_service import OpenAILLMService
from chatbot.interfaces import LLMService, DatabaseService
from config import environment

class LLMFactory:
    @staticmethod
    def get_llm_service(api_type: str) -> LLMService:
        if api_type == "openai":
            return OpenAILLMService(api_key=environment.settings.AZURE_OPENAI_API_KEY, endpoint=environment.settings.AZURE_OPENAI_ENDPOINT)
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
