import shelve
import os
import uuid
import json
import time
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
        # Check if '.git' is part of the path, effectively ignoring it and its contents  
        if '.git' in path.split(os.sep):  
            return True  
  
        relative_path = os.path.relpath(path, root)  
        path_parts = relative_path.split(os.sep)  
  
        # Check each part of the path against the ignore patterns  
        # This helps in effectively ignoring directories like 'chats-bkp'  
        for part in path_parts:  
            for pattern in ignore_patterns:  
                if fnmatch(part, pattern):  
                    return True  
  
        # Also check the entire relative path against the ignore patterns  
        for pattern in ignore_patterns:  
            if fnmatch(relative_path, pattern):  
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
        
        return json.dumps(directory_structure, ensure_ascii=True, indent=5, sort_keys=True)
    
    def get_files_modified_in_last_24_hours(self, directory: str) -> List[str]:
        now = time.time()
        cutoff_time = now - 24 * 60 * 60  # 24 hours in seconds
        ignore_patterns = self.read_gitignore(directory)
        ignore_patterns.append('.git')  # Always ignore .git directory

        changed_files = []

        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                if self.is_ignored(relative_path, ignore_patterns, directory):
                    continue
                file_mtime = os.path.getmtime(file_path)
                if file_mtime > cutoff_time:
                    changed_files.append(file_path)

        return changed_files
    
    def read_file_content(self, file_path: str) -> str:  
        """Reads and returns the content of the specified file."""  
        try:  
            with open(file_path, 'r', encoding='utf-8') as file:  
                return file.read()  
        except Exception as e:  
            # Handle exceptions if you can't read the file  
            return f"Error reading file {file_path}: {e}"  
        
    def get_all_files(self, directory: str) -> List[str]:  
        """Get all files in the directory that are not ignored by .gitignore."""  
        ignore_patterns = self.read_gitignore(directory)  
        ignore_patterns.append('.git')  # Always ignore .git directory  
  
        all_files = []  
  
        for root, _, files in os.walk(directory):  
            for file in files:  
                file_path = os.path.join(root, file)  
                relative_path = os.path.relpath(file_path, directory)  
                if self.is_ignored(relative_path, ignore_patterns, directory):  
                    continue  
                all_files.append(file_path)  
  
        return all_files  