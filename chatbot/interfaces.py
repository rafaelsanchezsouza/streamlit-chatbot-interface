from abc import ABC, abstractmethod

class LLMService(ABC):
    @abstractmethod
    def query(self, messages, model):
        pass

class DatabaseService(ABC):
    @abstractmethod
    def load_chat_history(self, session_id):
        pass

    @abstractmethod
    def save_chat_history(self, session_id, messages):
        pass

    @abstractmethod
    def new_chat_session(self):
        pass

    @abstractmethod
    def delete_chat_history(self, session_id):
        pass

    @abstractmethod
    def get_all_session_ids(self):
        pass

    @abstractmethod
    def change_session_id(self, old_session_id, new_session_id):
        pass

class FileSystem(ABC):
    @abstractmethod
    def get_all_files(self, path: str) -> dict:
        pass