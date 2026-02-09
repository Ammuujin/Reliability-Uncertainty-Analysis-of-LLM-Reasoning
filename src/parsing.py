"""
Parsing module — extract structured fields (ANSWER, CONFIDENCE)
from raw LLM outputs.
"""

import re
import json
from typing import Optional

from src.utils import load_jsonl, append_jsonl, ensure_dir


def parse_answer(raw_output: str) -> Optional[str]:
    """
    Extract the final answer from raw model output.
    Looks for the last occurrence of 'ANSWER:' and captures everything after it.
    Returns normalized text (stripped, lowercased, commas removed).
    """
    if not raw_output:
        return None

    # Find all ANSWER: occurrences — take the last one
    matches = re.findall(r"ANSWER:\s*(.+)", raw_output, re.IGNORECASE)
    if not matches:
        return None

    answer = matches[-1].strip()
    # Normalize: lowercase, remove commas, strip surrounding quotes/whitespace
    answer = answer.lower().strip().replace(",", "").strip("\"'` ")

    # Remove trailing period if present
    if answer.endswith("."):
        answer = answer[:-1].strip()

    # Remove dollar sign prefix for numeric answers
    if answer.startswith("$"):
        answer = answer[1:].strip()

    # Remove trailing units (e.g., "180 miles" → "180", "25 liters" → "25")
    unit_pattern = r"^([\d.\/\-]+)\s+(miles|mph|km|km\/h|meters|m|cm|feet|ft|inches|in|liters|gallons|gal|hours|hrs|minutes|mins|seconds|secs|days|weeks|months|years|dollars|cents|percent|%|kg|lbs|pounds|ounces|oz|cups|degrees|packs|boxes|slices|cookies|stickers|pencils|widgets|muffins|roses|desks|apples|bananas|tickets|crayons|shirts|employees|games|arrangements|weighings|pourings|switches)\.?$"
    unit_match = re.match(unit_pattern, answer, re.IGNORECASE)
    if unit_match:
        answer = unit_match.group(1).strip()

    return answer if answer else None


def parse_confidence(raw_output: str) -> Optional[int]:
    """
    Extract the confidence score (0–100) from raw model output.
    Looks for the last occurrence of 'CONFIDENCE:' followed by a number.
    Returns an integer clamped to [0, 100], or None if not found.
    """
    if not raw_output:
        return None

    matches = re.findall(r"CONFIDENCE:\s*(\d+)", raw_output, re.IGNORECASE)
    if not matches:
        return None

    value = int(matches[-1])
    return max(0, min(100, value))


def parse_all_outputs(
    generations_path: str,
    output_path: str,
) -> list[dict]:
    """
    Parse all raw generation records and write parsed outputs to JSONL.
    Returns the list of parsed records.
    """
    records = load_jsonl(generations_path)
    if not records:
        print(f"No records found in {generations_path}")
        return []

    ensure_dir(output_path)
    parsed = []

    # Clear output file (re-parse from scratch each time)
    with open(output_path, "w") as f:
        pass

    for rec in records:
        raw = rec.get("raw_output", "")
        answer = parse_answer(raw)
        confidence = parse_confidence(raw)

        parsed_rec = {
            "question_id": rec["question_id"],
            "prompt_name": rec["prompt_name"],
            "temperature": rec["temperature"],
            "run_index": rec["run_index"],
            "model": rec.get("model", ""),
            "raw_output": raw,
            "parsed_answer": answer,
            "parsed_confidence": confidence,
            "parse_success": answer is not None,
        }
        parsed.append(parsed_rec)
        append_jsonl(output_path, parsed_rec)

    success_count = sum(1 for p in parsed if p["parse_success"])
    print(
        f"Parsed {len(parsed)} records: "
        f"{success_count} successful, {len(parsed) - success_count} failed"
    )
    return parsed


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse raw LLM outputs")
    parser.add_argument(
        "--config",
        default="configs/experiment.yaml",
        help="Path to experiment config",
    )
    args = parser.parse_args()

    from src.utils import load_config, project_root
    import os

    root = project_root()
    config = load_config(os.path.join(root, args.config))

    generations_path = os.path.join(root, config["output_path"])
    parsed_output_path = os.path.join(root, config["parsed_output_path"])

    parse_all_outputs(generations_path, parsed_output_path)
