from git import Repo
import json
from pathlib import Path
from typing import Dict, List
from openai import OpenAI
import os

class GitCommitManager:
    def __init__(self, repo_path: str):
        self.repo = Repo(repo_path)
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _get_staged_diffs(self) -> List[Dict]:
        staged_diffs = self.repo.index.diff("HEAD")
        return [self._parse_diff(d) for d in staged_diffs]

    def _parse_diff(self, diff) -> Dict:
        diff_text = self.repo.git.diff(
            diff.b_blob, diff.a_blob, 
            unified=True, 
            ignore_blank_lines=True,
            ignore_space_at_eol=True
        ) if diff.a_blob and diff.b_blob else ""
        
        return {"raw_diff": diff_text}

    def _analyze_diffs(self, diffs: List[Dict]):
        diffs_str = json.dumps(diffs, indent=2, ensure_ascii=False)
        commit_structure = """
            <type>(<scope>): <short description>
            (linha em branco)
            <longer description> (opcional – explique o quê e por quê)
            (linha em branco)
            BREAKING CHANGE: <descrição da quebra> (opcional)
            ISSUES CLOSED: #<número> (opcional)
        """
        prompt = "Based only on the git diff below, please propose a commit that follows conventional commit rules and the following structure. Return only the commit message, without any other comments. " + "Git Diff: " + diffs_str + "Use the following structure as reference: " + commit_structure
   
        response = self.client.chat.completions.create(
            model="o4-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def generate_new_commit(self):
        """Generate new commit from diffs without saving."""
        processed_diffs = self._get_staged_diffs()
        print("Analyzing Diffs")
        rules = self._analyze_diffs(processed_diffs)
        return rules
