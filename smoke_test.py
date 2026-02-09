"""
Quick smoke test — runs 3 questions through the full pipeline
to verify everything works end-to-end.
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Setup paths
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.llm_client import LLMClient
from src.utils import load_dataset, load_prompt_template, build_prompt
from src.parsing import parse_answer, parse_confidence
from src.scoring import score_answer

def main():
    print("=" * 50)
    print("SMOKE TEST — 3 questions, 1 prompt, 1 run")
    print("=" * 50)

    # 1. Load dataset (first 3 questions)
    dataset = load_dataset(str(ROOT / "data" / "processed" / "questions.jsonl"))[:3]
    print(f"\n✓ Loaded {len(dataset)} questions")
    for q in dataset:
        print(f"  {q['id']}: {q['question'][:60]}...")

    # 2. Load prompt
    template = load_prompt_template(str(ROOT / "prompts"), "direct")
    print(f"\n✓ Loaded prompt template (direct)")

    # 3. Init LLM client
    print(f"\n→ Connecting to Gemini API...")
    client = LLMClient(model="gemini-2.0-flash", rate_limit_rpm=30)
    print(f"✓ LLM client ready")

    # 4. Run 3 calls
    results = []
    for q in dataset:
        prompt = build_prompt(template, q["question"])
        print(f"\n→ Calling API for {q['id']}...")
        
        raw = client.generate(prompt=prompt, temperature=0.0)
        
        answer = parse_answer(raw)
        confidence = parse_confidence(raw)
        result = score_answer(answer, q["answer"], q["answer_type"])
        
        results.append({
            "id": q["id"],
            "question": q["question"][:50],
            "expected": q["answer"],
            "got": answer,
            "confidence": confidence,
            "correct": result["is_correct"],
        })
        
        print(f"  Raw output (first 200 chars): {raw[:200]}")
        print(f"  Parsed answer: {answer}")
        print(f"  Confidence: {confidence}")
        print(f"  Correct: {result['is_correct']}")

    # 5. Summary
    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    for r in results:
        status = "✓" if r["correct"] else "✗"
        print(f"  {status} {r['id']}: expected={r['expected']}, got={r['got']}, conf={r['confidence']}")
    
    correct = sum(1 for r in results if r["correct"])
    print(f"\n  Score: {correct}/{len(results)}")
    print(f"\n{'=' * 50}")
    print("SMOKE TEST COMPLETE — pipeline works end-to-end!")
    print(f"{'=' * 50}")
    print("\nTo run the full experiment:")
    print('  "/Users/amuujin/Desktop/Reliability & Uncertainty Analysis of LLM Reasoning/.venv/bin/python" -m src.run_experiments --config configs/experiment.yaml')

if __name__ == "__main__":
    main()
