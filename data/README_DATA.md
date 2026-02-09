# Dataset Documentation

## Overview

This dataset contains **100 structured reasoning problems** curated specifically
for this study. All questions have objective, verifiable answers.

## Categories

| Category     | Count | Description                                                                             |
| ------------ | ----- | --------------------------------------------------------------------------------------- |
| `arithmetic` | 40    | Multi-step word problems (addition, subtraction, multiplication, division, percentages) |
| `logic`      | 30    | Deduction puzzles, truth-teller/liar, set membership, syllogisms                        |
| `multi_step` | 30    | Story problems requiring 3+ reasoning steps, unit conversions, scheduling               |

## Difficulty Distribution

Each category targets approximately:

- **Easy** (~33%): single operation or straightforward deduction
- **Medium** (~34%): 2–3 steps, moderate complexity
- **Hard** (~33%): 3+ steps, distractors, or non-obvious reasoning

## Format

Each line of `processed/questions.jsonl` is a JSON object:

```json
{
  "id": "Q001",
  "category": "arithmetic",
  "difficulty": "easy",
  "question": "A store sells apples for $2 each. If you buy 5 apples, how much do you pay?",
  "answer": "10",
  "answer_type": "numeric"
}
```

### Fields

| Field         | Type   | Description                            |
| ------------- | ------ | -------------------------------------- |
| `id`          | string | Unique identifier (Q001–Q100)          |
| `category`    | string | `arithmetic`, `logic`, or `multi_step` |
| `difficulty`  | string | `easy`, `medium`, or `hard`            |
| `question`    | string | The problem statement                  |
| `answer`      | string | The correct answer                     |
| `answer_type` | string | `numeric` or `text`                    |

## Sourcing

All 100 questions were **authored by the researcher** for this study.
No external datasets or benchmarks were used.

## License

This dataset is released under the same MIT license as the rest of this repository.
