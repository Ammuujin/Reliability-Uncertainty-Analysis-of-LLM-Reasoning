"""
Scoring module — compare parsed answers against ground truth
and produce a scored CSV for analysis.
"""

import os
import re
import csv
from typing import Optional

from src.utils import load_config, load_dataset, load_jsonl, project_root


def normalize_numeric(value: str) -> Optional[float]:
    """Try to parse a string as a float. Return None on failure."""
    try:
        # Remove common non-numeric characters
        cleaned = value.strip().replace(",", "").replace("$", "").replace("%", "")
        # Handle fractions like "3/4"
        if "/" in cleaned and cleaned.count("/") == 1:
            num, den = cleaned.split("/")
            return float(num.strip()) / float(den.strip())
        return float(cleaned)
    except (ValueError, ZeroDivisionError):
        return None


def normalize_text(value: str) -> str:
    """Normalize text for comparison: lowercase, strip, remove punctuation."""
    text = value.lower().strip()
    # Remove trailing/leading punctuation
    text = re.sub(r"[^\w\s/:]", "", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def score_answer(
    parsed_answer: Optional[str],
    ground_truth: str,
    answer_type: str,
) -> dict:
    """
    Compare a parsed answer to the ground truth.
    Returns a dict with scoring fields.
    """
    if parsed_answer is None:
        return {
            "is_correct": False,
            "is_unknown": False,
            "match_type": "parse_failure",
        }

    normalized = parsed_answer.strip().lower()

    # Check for UNKNOWN
    if normalized in ("unknown", "i don't know", "cannot determine"):
        return {
            "is_correct": False,
            "is_unknown": True,
            "match_type": "unknown",
        }

    if answer_type == "numeric":
        parsed_num = normalize_numeric(parsed_answer)
        truth_num = normalize_numeric(ground_truth)

        if parsed_num is not None and truth_num is not None:
            # Tolerance for floating-point comparison
            is_correct = abs(parsed_num - truth_num) < 0.005
            return {
                "is_correct": is_correct,
                "is_unknown": False,
                "match_type": "numeric",
            }
        else:
            # Fall back to text comparison if numeric parsing fails
            is_correct = normalize_text(parsed_answer) == normalize_text(ground_truth)
            return {
                "is_correct": is_correct,
                "is_unknown": False,
                "match_type": "text_fallback",
            }
    else:
        # Text comparison
        is_correct = normalize_text(parsed_answer) == normalize_text(ground_truth)
        return {
            "is_correct": is_correct,
            "is_unknown": False,
            "match_type": "text",
        }


def score_all(config_path: str = "configs/experiment.yaml") -> str:
    """
    Load parsed outputs and ground truth, compute scores,
    and write results/scores.csv. Returns the output path.
    """
    root = project_root()
    config = load_config(os.path.join(root, config_path))

    # Load data
    dataset = load_dataset(os.path.join(root, config["dataset_path"]))
    parsed = load_jsonl(os.path.join(root, config["parsed_output_path"]))

    if not parsed:
        print("No parsed outputs found. Run parsing first.")
        return ""

    # Build ground-truth lookup
    gt_lookup = {}
    for q in dataset:
        gt_lookup[q["id"]] = {
            "answer": q["answer"],
            "answer_type": q["answer_type"],
            "category": q["category"],
            "difficulty": q["difficulty"],
        }

    # Score each parsed record
    scores_path = os.path.join(root, config["scores_path"])
    os.makedirs(os.path.dirname(scores_path), exist_ok=True)

    fieldnames = [
        "question_id",
        "category",
        "difficulty",
        "prompt_name",
        "temperature",
        "run_index",
        "parsed_answer",
        "ground_truth",
        "is_correct",
        "is_unknown",
        "confidence",
        "parse_success",
        "match_type",
    ]

    rows = []
    for rec in parsed:
        qid = rec["question_id"]
        gt = gt_lookup.get(qid, {})

        result = score_answer(
            rec.get("parsed_answer"),
            gt.get("answer", ""),
            gt.get("answer_type", "text"),
        )

        row = {
            "question_id": qid,
            "category": gt.get("category", ""),
            "difficulty": gt.get("difficulty", ""),
            "prompt_name": rec["prompt_name"],
            "temperature": rec["temperature"],
            "run_index": rec["run_index"],
            "parsed_answer": rec.get("parsed_answer", ""),
            "ground_truth": gt.get("answer", ""),
            "is_correct": result["is_correct"],
            "is_unknown": result["is_unknown"],
            "confidence": rec.get("parsed_confidence", ""),
            "parse_success": rec.get("parse_success", False),
            "match_type": result["match_type"],
        }
        rows.append(row)

    with open(scores_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Summary
    total = len(rows)
    correct = sum(1 for r in rows if r["is_correct"])
    unknown = sum(1 for r in rows if r["is_unknown"])
    parse_fail = sum(1 for r in rows if not r["parse_success"])

    print(f"\nScoring complete: {scores_path}")
    print(f"  Total:        {total}")
    print(f"  Correct:      {correct} ({100 * correct / total:.1f}%)")
    print(f"  Unknown:      {unknown} ({100 * unknown / total:.1f}%)")
    print(f"  Parse fails:  {parse_fail} ({100 * parse_fail / total:.1f}%)")

    return scores_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Score parsed LLM outputs")
    parser.add_argument(
        "--config",
        default="configs/experiment.yaml",
        help="Path to experiment config",
    )
    args = parser.parse_args()
    score_all(args.config)
