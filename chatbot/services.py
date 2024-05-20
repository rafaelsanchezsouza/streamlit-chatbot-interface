import shelve
import os
import uuid
from openai import AzureOpenAI
from chatbot.interfaces import LLMService, DatabaseService, FileSystem
from config import environment


class OpenAILLMService(LLMService):
    def __init__(self, api_key, endpoint):
        self.client = AzureOpenAI(api_key=api_key, api_version="2024-02-01", azure_endpoint=endpoint)

    def query(self, messages):
        for response in self.client.chat.completions.create(model=environment.settings.AZURE_OPENAI_MODEL, messages=messages, stream=True):
            yield response

class ShelveDatabaseService(DatabaseService):
    def load_chat_history(self, session_id):
        if session_id:  
            with shelve.open("chat_history") as db:  
                return db.get(session_id, [])  
        return []  

    def save_chat_history(self, session_id, messages):
        if session_id:  
            with shelve.open("chat_history") as db:  
                db[session_id] = messages  

    def new_chat_session(self):
        session_id = str(uuid.uuid4())
        with shelve.open("chat_history") as db:
            db[session_id] = []
        return session_id

    def delete_chat_history(self, session_id):
        with shelve.open("chat_history") as db:
            del db[session_id]

    def get_all_session_ids(self):
        with shelve.open("chat_history") as db:
            return list(db.keys())
        
    def change_session_id(self, old_session_id, new_session_id):  
        with shelve.open("chat_history") as db:  
            # Ensure the old session exists  
            if old_session_id in db:  
                # Copy the data to a new session ID  
                db[new_session_id] = db[old_session_id]  
                # Delete the old session  
                del db[old_session_id]  
            else:  
                print("Session not found.")  
        
        return new_session_id
    
class LocalFileSystem(FileSystem):
    def read_directory_structure(self, path: str) -> dict:
        directory_structure = {}
        for root, dirs, files in os.walk(path):
            # Split the root into parts to create a nested dictionary
            parts = root.split(os.sep)
            current_level = directory_structure
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            for file in files:
                current_level[file] = None
        return directory_structure

