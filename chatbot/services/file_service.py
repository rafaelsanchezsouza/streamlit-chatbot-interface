import os
import json
import time
from chatbot.interfaces import FileSystem
from typing import List
from fnmatch import fnmatch

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