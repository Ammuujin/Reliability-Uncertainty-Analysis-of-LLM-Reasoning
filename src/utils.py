"""
Utility helpers for the experiment pipeline.
"""

import json
import os
import time
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


def load_config(config_path: str) -> dict:
    """Load YAML configuration file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def load_dataset(path: str) -> list[dict]:
    """Load a JSONL dataset into a list of dicts."""
    items = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def load_prompt_template(prompts_dir: str, prompt_name: str) -> str:
    """Load a prompt template file and return its text."""
    path = os.path.join(prompts_dir, f"{prompt_name}.txt")
    with open(path, "r") as f:
        return f.read()


def build_prompt(template: str, question: str) -> str:
    """Substitute {{QUESTION}} in template and append the answer format suffix."""
    suffix = (
        "\n\nRespond in EXACTLY this format:\n"
        "CONFIDENCE: <0-100>\n"
        "ANSWER: <your answer here>"
    )
    return template.replace("{{QUESTION}}", question) + suffix


def append_jsonl(path: str, record: dict) -> None:
    """Append a single JSON record to a JSONL file (crash-safe)."""
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


def load_jsonl(path: str) -> list[dict]:
    """Load all records from a JSONL file."""
    if not os.path.exists(path):
        return []
    records = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def get_completed_keys(output_path: str) -> set[tuple]:
    """
    Scan existing output JSONL for already-completed runs.
    Returns a set of (question_id, prompt_name, temperature, run_index) tuples.
    """
    completed = set()
    for rec in load_jsonl(output_path):
        key = (
            rec["question_id"],
            rec["prompt_name"],
            rec["temperature"],
            rec["run_index"],
        )
        completed.add(key)
    return completed


def project_root() -> Path:
    """Return the project root directory (parent of src/)."""
    return Path(__file__).resolve().parent.parent


def ensure_dir(path: str) -> None:
    """Create directory if it doesn't exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
