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
        # Initialize default structure
        default_styleguide = {
            "layout_structure": [],
            "anti_patterns": []
        }
        
        try:
            with open(self.styleguide_path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                
                # Merge with defaults to preserve existing data
                return {
                    **default_styleguide,
                    **loaded_data
                }
                
        except (FileNotFoundError, json.JSONDecodeError):
            # Return defaults if file is missing or invalid
            return default_styleguide

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

    def generate_styleguide_updates(self):
        """Generate new style rules from diffs without saving."""
        processed_diffs = self._get_staged_diffs()
        print("Analyzing Diffs")
        rules = self._analyze_diffs(processed_diffs)
        return rules

    def _analyze_diffs(self, diffs: List[Dict]):
        diffs_str = json.dumps(diffs, indent=2, ensure_ascii=False)
        styleguide_str = json.dumps(self.styleguide, indent=2, ensure_ascii=False)
        styleguide_structure = """
            {
                "layout_structure": [
                {
                    "rule": "rule title",
                    "description": "rule description",
                    "examples": [
                    "examples"
                    ]
                },
                {
                    "rule": "rule title",
                    "description": "rule description",
                    "examples": [
                    "examples"
                    ]
                }
                ],
                "anti_patterns": [
                {
                    "rule": "rule title",
                    "description": "rule description"
                },
                {
                    "rule": "rule title",
                    "description": "rule description"
                }
                ]
            }
        """
        prompt = "Based only on the git diff below and in the provided styleguide return a json with new rules for the styleguide. Format must be valid JSON only, without any wrapping text or code blocks. " + "Git Diff: " + diffs_str + "Styleguide: " + styleguide_str + "Use the following structure as reference: " + styleguide_structure
   
        response = self.client.chat.completions.create(
            model="o4-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def _add_layout_rule(self, rules: Dict):
        print("inside layout rules")
        for rule in rules["layout_structure"]:
                self.styleguide["layout_structure"].append(rule)
        
        for rule in rules["anti_patterns"]:
                self.styleguide["anti_patterns"].append(rule)
        