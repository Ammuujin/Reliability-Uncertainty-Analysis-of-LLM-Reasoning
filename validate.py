"""Quick validation script for the dataset and Python source modules."""

import json
import sys
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent

# 1. Validate dataset
print("=== Dataset Validation ===")
dataset_path = root / "data" / "processed" / "questions.jsonl"
with open(dataset_path) as f:
    lines = [json.loads(l) for l in f if l.strip()]

print(f"Total questions: {len(lines)}")
cats = Counter(q["category"] for q in lines)
diffs = Counter(q["difficulty"] for q in lines)
types = Counter(q["answer_type"] for q in lines)
print(f"Categories:  {dict(cats)}")
print(f"Difficulties: {dict(diffs)}")
print(f"Answer types: {dict(types)}")
ids = [q["id"] for q in lines]
print(f"IDs unique: {len(set(ids)) == len(ids)}")

required = {"id", "category", "question", "answer", "answer_type", "difficulty"}
errors = 0
for q in lines:
    missing = required - set(q.keys())
    if missing:
        print(f"  MISSING in {q['id']}: {missing}")
        errors += 1
if errors == 0:
    print("All fields present ✓")

# 2. Validate Python imports
print("\n=== Module Import Validation ===")
sys.path.insert(0, str(root))
try:
    from src.utils import load_config, load_dataset, build_prompt, load_prompt_template

    print("src.utils ✓")
except Exception as e:
    print(f"src.utils FAILED: {e}")

try:
    from src.parsing import parse_answer, parse_confidence

    print("src.parsing ✓")
except Exception as e:
    print(f"src.parsing FAILED: {e}")

try:
    from src.scoring import score_answer, normalize_numeric

    print("src.scoring ✓")
except Exception as e:
    print(f"src.scoring FAILED: {e}")

# 3. Test parser
print("\n=== Parser Tests ===")
test_cases = [
    ("CONFIDENCE: 85\nANSWER: 42", "42", 85),
    ("Let me think...\nStep 1: ...\nCONFIDENCE: 70\nANSWER: yes", "yes", 70),
    ("ANSWER: $5.50\nCONFIDENCE: 90", "5.50", 90),
    ("I don't know the answer.", None, None),
    ("CONFIDENCE: 30\nANSWER: UNKNOWN", "unknown", 30),
    ("CONFIDENCE: 95\nANSWER: 10,000", "10000", 95),
]

passed = 0
for raw, expected_ans, expected_conf in test_cases:
    ans = parse_answer(raw)
    conf = parse_confidence(raw)
    ok = ans == expected_ans and conf == expected_conf
    status = "✓" if ok else "✗"
    if not ok:
        print(f"  {status} Input: {raw!r}")
        print(f"       Expected: ans={expected_ans}, conf={expected_conf}")
        print(f"       Got:      ans={ans}, conf={conf}")
    else:
        passed += 1
print(f"Parser tests: {passed}/{len(test_cases)} passed")

# 4. Test scorer
print("\n=== Scorer Tests ===")
score_tests = [
    ("42", "42", "numeric", True),
    ("42.0", "42", "numeric", True),
    ("41.99", "42", "numeric", False),
    ("yes", "yes", "text", True),
    ("Yes", "yes", "text", True),
    ("unknown", "42", "numeric", False),  # is_unknown should be True
    (None, "42", "numeric", False),
]

passed = 0
for parsed, truth, atype, expected_correct in score_tests:
    result = score_answer(parsed, truth, atype)
    ok = result["is_correct"] == expected_correct
    if not ok:
        print(f"  ✗ parsed={parsed}, truth={truth}, type={atype}")
        print(f"    Expected correct={expected_correct}, got={result}")
    else:
        passed += 1
print(f"Scorer tests: {passed}/{len(score_tests)} passed")

# 5. Test prompt building
print("\n=== Prompt Build Test ===")
template = load_prompt_template(str(root / "prompts"), "direct")
prompt = build_prompt(template, "What is 2+2?")
has_question = "What is 2+2?" in prompt
has_confidence = "CONFIDENCE:" in prompt
has_answer = "ANSWER:" in prompt
print(
    f"Question substituted: {has_question} ✓" if has_question else "Question missing ✗"
)
print(
    f"CONFIDENCE suffix: {has_confidence} ✓"
    if has_confidence
    else "CONFIDENCE missing ✗"
)
print(f"ANSWER suffix: {has_answer} ✓" if has_answer else "ANSWER missing ✗")

# 6. Config validation
print("\n=== Config Validation ===")
config = load_config(str(root / "configs" / "experiment.yaml"))
print(f"Model: {config['model']}")
print(f"Prompts: {config['prompts']}")
print(f"Temperatures: {config['temperatures']}")
print(f"Runs: {config['num_runs']}")
total = (
    len(lines)
    * len(config["prompts"])
    * len(config["temperatures"])
    * config["num_runs"]
)
print(f"Total API calls: {total}")

print("\n=== All Validations Complete ===")
