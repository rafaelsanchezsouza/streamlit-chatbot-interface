from git import Repo
import json
from pathlib import Path
from typing import Dict, List
from openai import OpenAI
import os

class GitStyleGuideManager:
    def __init__(self, repo_path: str, styleguide_path: str):
        self.repo = Repo(repo_path)
        self.styleguide_path = Path(styleguide_path)
        self.styleguide = self._load_styleguide()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def _load_styleguide(self) -> Dict:
        try:
            with open(self.styleguide_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"layout_structure": [], "anti_patterns": []}

    def _save_styleguide(self):
        with open(self.styleguide_path, "w", encoding="utf-8") as f:
            json.dump(self.styleguide, f, indent=2)

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

    def update_styleguide(self):
        processed_diffs = self._get_staged_diffs()
        rules = self._analyze_diffs(processed_diffs)
        self._add_layout_rule(json.loads(rules))
        self._save_styleguide()
        return {"status": "success", "added": len(processed_diffs)}

    def _analyze_diffs(self, diffs: List[Dict]):
        diffs_str = json.dumps(diffs, indent=2, ensure_ascii=False)
        styleguide_str = json.dumps(self.styleguide, indent=2, ensure_ascii=False)
        prompt = "Based only on the git diff below and in the provided styleguide, return only a json with new rules for the styleguide. " + "Git Diff: " + diffs_str + "Styleguide: " + styleguide_str
        
        response = self.client.chat.completions.create(
            model="o4-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _add_layout_rule(self, rules: Dict):
        existing_rules = [r["rule"] for r in self.styleguide["layout_structure"]]
        for rule in rules["new_rules"]:
            if rule not in existing_rules:
                self.styleguide["layout_structure"].append(rule)