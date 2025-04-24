import os
import time
from typing import List
from pathspec import PathSpec
from chatbot.interfaces import FileSystem

class LocalFileSystem(FileSystem):

    def load_gitignore(self, directory: str) -> PathSpec:
        """Load .gitignore in `directory` (if it exists) and build a PathSpec."""
        gitignore = os.path.join(directory, '.gitignore')
        if os.path.exists(gitignore):
            with open(gitignore, 'r') as f:
                # 'gitwildmatch' is the same syntax Git uses internally
                return PathSpec.from_lines('gitwildmatch', f)
        # no .gitignore → empty spec
        return PathSpec.from_lines('gitwildmatch', [])

    def is_ignored_by_spec(self, spec: PathSpec, relpath: str) -> bool:
        """
        Returns True if the given relpath (always with forward‐slashes)
        is matched by either a .gitignore pattern or is the .git folder.
        """
        # always ignore anything under a .git directory
        if relpath.split('/')[0] == '.git':
            return True

        # PathSpec wants forward-slashes, so ensure we normalize
        norm = relpath.replace(os.sep, '/')
        return spec.match_file(norm)

    def get_files_modified_in_last_24_hours(self, directory: str) -> List[str]:
        now = time.time()
        cutoff_time = now - 24 * 60 * 60
        spec = self.load_gitignore(directory)

        changed_files: List[str] = []
        for root, dirs, files in os.walk(directory):
            # prune ignored dirs so we never even walk into them
            rel_root = os.path.relpath(root, directory).replace(os.sep, '/')
            dirs[:] = [
                d for d in dirs
                if not self.is_ignored_by_spec(spec, f"{rel_root}/{d}" if rel_root != '.' else d)
            ]

            for fn in files:
                # compute relative path from project root
                rel = os.path.relpath(os.path.join(root, fn), directory)
                # normalize separators
                rel = rel.replace(os.sep, '/')
                if self.is_ignored_by_spec(spec, rel):
                    continue
                full = os.path.join(root, fn)
                if os.path.getmtime(full) > cutoff_time:
                    changed_files.append(full)

        return changed_files

    def read_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file {file_path}: {e}"

    def get_all_files(self, directory: str) -> List[str]:
        """
        Walks the directory, returns all files not ignored
        according to .gitignore.
        """
        spec = self.load_gitignore(directory)
        all_files: List[str] = []

        for root, dirs, files in os.walk(directory):
            # prune ignored dirs
            rel_root = os.path.relpath(root, directory).replace(os.sep, '/')
            dirs[:] = [
                d for d in dirs
                if not self.is_ignored_by_spec(spec, f"{rel_root}/{d}" if rel_root != '.' else d)
            ]

            for fn in files:
                rel = os.path.relpath(os.path.join(root, fn), directory)
                rel = rel.replace(os.sep, '/')
                if self.is_ignored_by_spec(spec, rel):
                    continue
                all_files.append(os.path.join(root, fn))

        return all_files