import shelve
import os
import uuid
from openai import AzureOpenAI
from chatbot.interfaces import LLMService, DatabaseService, FileSystem
from config import environment
from typing import List
from fnmatch import fnmatch

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
    def read_gitignore(self, path: str) -> List[str]:
        gitignore_path = os.path.join(path, '.gitignore')
        if not os.path.exists(gitignore_path):
            return []
        
        with open(gitignore_path, 'r') as file:
            lines = file.readlines()
        
        ignore_patterns = []
        for line in lines:
            # Remove comments and trim whitespace
            clean_line = line.split('#')[0].strip()
            if clean_line:
                ignore_patterns.append(clean_line)
        
        return ignore_patterns

    def is_ignored(self, path: str, ignore_patterns: List[str], root: str) -> bool:
        relative_path = os.path.relpath(path, root)
        for pattern in ignore_patterns:
            if fnmatch(relative_path, pattern) or fnmatch(path, pattern):
                return True
        return False

    def read_directory_structure(self, path: str) -> dict:
        directory_structure = {}
        ignore_patterns = self.read_gitignore(path)
        ignore_patterns.append('.git')  
        
        for root, dirs, files in os.walk(path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not self.is_ignored(os.path.join(root, d), ignore_patterns, path)]
            # Skip ignored files
            files = [f for f in files if not self.is_ignored(os.path.join(root, f), ignore_patterns, path)]

            # Split the root into parts to create a nested dictionary
            parts = os.path.relpath(root, path).split(os.sep)
            current_level = directory_structure
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
            for file in files:
                current_level[file] = None
        
        return directory_structure