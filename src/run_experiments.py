"""
Experiment runner — orchestrates the full generation loop.

Loads config, dataset, and prompt templates, then iterates over
all (question × prompt × temperature × run) combinations,
calling the LLM and storing raw outputs to JSONL.

Supports resume: skips already-completed runs found in the output file.
"""

import argparse
import logging
import os
import sys
from datetime import datetime, timezone

from tqdm import tqdm

from src.llm_client import LLMClient
from src.utils import (
    load_config,
    load_dataset,
    load_prompt_template,
    build_prompt,
    append_jsonl,
    get_completed_keys,
    ensure_dir,
    project_root,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def run_experiments(config_path: str) -> None:
    """Execute the full experiment grid."""
    root = project_root()
    config = load_config(os.path.join(root, config_path))

    # Paths
    dataset_path = os.path.join(root, config["dataset_path"])
    output_path = os.path.join(root, config["output_path"])
    prompts_dir = os.path.join(root, "prompts")

    ensure_dir(output_path)

    # Load data
    dataset = load_dataset(dataset_path)
    logger.info("Loaded %d questions from %s", len(dataset), dataset_path)

    # Load prompt templates
    prompt_names = config["prompts"]
    templates = {}
    for name in prompt_names:
        templates[name] = load_prompt_template(prompts_dir, name)
    logger.info("Loaded %d prompt templates: %s", len(templates), prompt_names)

    # Settings
    temperatures = config["temperatures"]
    num_runs = config["num_runs"]
    model_name = config["model"]
    max_tokens = config.get("max_output_tokens", 1024)

    # Resume support
    completed = get_completed_keys(output_path)
    logger.info("Found %d completed runs (will skip)", len(completed))

    # Build work list
    work = []
    for question in dataset:
        for prompt_name in prompt_names:
            for temp in temperatures:
                for run_idx in range(1, num_runs + 1):
                    key = (question["id"], prompt_name, temp, run_idx)
                    if key not in completed:
                        work.append((question, prompt_name, temp, run_idx))

    total_remaining = len(work)
    total_possible = len(dataset) * len(prompt_names) * len(temperatures) * num_runs
    logger.info(
        "Work items: %d remaining out of %d total", total_remaining, total_possible
    )

    if total_remaining == 0:
        logger.info("All runs already completed. Nothing to do.")
        return

    # Initialize LLM client
    client = LLMClient(
        model=model_name,
        rate_limit_rpm=config.get("rate_limit_rpm", 15),
        retry_max=config.get("retry_max", 3),
        retry_backoff_seconds=config.get("retry_backoff_seconds", 5),
    )
    logger.info("LLM client ready (model=%s)", model_name)

    # Main loop
    errors = 0
    for question, prompt_name, temp, run_idx in tqdm(
        work, desc="Running experiments", unit="call"
    ):
        template = templates[prompt_name]
        full_prompt = build_prompt(template, question["question"])

        try:
            raw_output = client.generate(
                prompt=full_prompt,
                temperature=temp,
                max_output_tokens=max_tokens,
            )
        except Exception as e:
            logger.error(
                "Fatal error on %s/%s/t=%.1f/run=%d: %s",
                question["id"],
                prompt_name,
                temp,
                run_idx,
                str(e),
            )
            raw_output = f"ERROR: {str(e)}"
            errors += 1

        record = {
            "question_id": question["id"],
            "prompt_name": prompt_name,
            "temperature": temp,
            "run_index": run_idx,
            "model": model_name,
            "prompt_text": full_prompt,
            "raw_output": raw_output,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        append_jsonl(output_path, record)

    logger.info(
        "Experiment complete. %d calls made, %d errors. Output: %s",
        total_remaining,
        errors,
        output_path,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Run LLM reasoning reliability experiments"
    )
    parser.add_argument(
        "--config",
        default="configs/experiment.yaml",
        help="Path to experiment config YAML",
    )
    args = parser.parse_args()
    run_experiments(args.config)


if __name__ == "__main__":
    main()
