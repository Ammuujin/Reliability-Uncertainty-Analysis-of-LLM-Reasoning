# Reliability & Uncertainty Analysis of LLM Reasoning

A controlled empirical study of consistency, uncertainty expression, and failure modes of LLMs on structured reasoning tasks under different prompting and decoding settings.

---

## Overview

This project investigates three fundamental questions about LLM reliability:

1. **Accuracy**: How does prompting strategy affect correctness on structured reasoning?
2. **Consistency**: How stable are answers across repeated runs under different temperatures?
3. **Calibration**: When models express confidence, is it well-calibrated?

We test these using **100 curated reasoning problems** (arithmetic, logic, multi-step) across **3 prompt types** × **2 temperatures** × **5 runs** = **3,000 total API calls**, with confidence scoring and a failure-mode taxonomy.

## Research Questions

- **RQ1**: Does chain-of-thought prompting improve accuracy over direct prompting?
- **RQ2**: How much does answer variance increase with higher temperature?
- **RQ3**: How well-calibrated is an LLM's self-reported confidence?
- **RQ4**: What systematic failure modes emerge, and how frequent are they?

## Project Structure

```
├── README.md
├── LICENSE
├── requirements.txt
├── .env.example
├── configs/
│   └── experiment.yaml          # Full experiment configuration
├── data/
│   ├── processed/
│   │   └── questions.jsonl      # 100 curated reasoning problems
│   └── README_DATA.md           # Dataset documentation
├── prompts/
│   ├── direct.txt               # Baseline prompt
│   ├── step_by_step.txt         # Chain-of-thought prompt
│   └── uncertainty_aware.txt    # Uncertainty-aware prompt
├── src/
│   ├── run_experiments.py       # Main experiment runner
│   ├── llm_client.py            # Gemini API wrapper
│   ├── parsing.py               # Output parser (ANSWER + CONFIDENCE)
│   ├── scoring.py               # Correctness scoring
│   └── utils.py                 # Shared utilities
├── results/                     # Generated outputs (gitignored)
├── analysis/
│   └── analysis.ipynb           # Metrics computation & plots
└── report/
    └── short_report.md          # Research report template
```

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API key

```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 3. Run experiments

```bash
python -m src.run_experiments --config configs/experiment.yaml
```

The runner supports **resume** — if interrupted, re-run the same command and it will skip completed calls.

### 4. Parse outputs

```bash
python -m src.parsing --config configs/experiment.yaml
```

### 5. Score results

```bash
python -m src.scoring --config configs/experiment.yaml
```

### 6. Analyze

Open `analysis/analysis.ipynb` in Jupyter to compute metrics and generate plots.

## Methodology

### Dataset

100 self-curated problems with verifiable answers:

| Category   | Count | Examples                                    |
| ---------- | ----- | ------------------------------------------- |
| Arithmetic | 40    | Word problems, percentages, rates           |
| Logic      | 30    | Deduction, knights & knaves, syllogisms     |
| Multi-step | 30    | Story problems, unit conversion, scheduling |

Difficulty: ~1/3 easy, ~1/3 medium, ~1/3 hard per category.

### Prompts

| Prompt                | Purpose                           |
| --------------------- | --------------------------------- |
| **Direct**            | Baseline accuracy — answer only   |
| **Step-by-step**      | Chain-of-thought — show reasoning |
| **Uncertainty-aware** | Encourage UNKNOWN when uncertain  |

All prompts enforce structured output: `CONFIDENCE: <0-100>` and `ANSWER: <value>`.

### Metrics

| Metric                  | Description                                          |
| ----------------------- | ---------------------------------------------------- |
| **Accuracy**            | % correct per (prompt, temperature) with 95% CI      |
| **Disagreement rate**   | % of questions with >1 unique answer across runs     |
| **Flip rate**           | % of questions correct in some runs, wrong in others |
| **ECE**                 | Expected Calibration Error from reliability diagram  |
| **Overconfidence rate** | % of high-confidence (≥80) wrong answers             |

### Failure Mode Taxonomy

Incorrect responses are manually labeled into categories:
arithmetic slip, logical fallacy, misread question, formatting failure,
contradiction, hallucinated fact, premature UNKNOWN, overconfident wrong.

## Key Findings

_[To be populated after experiments run]_

## Limitations

- Single model studied — findings may not generalize across models
- Self-curated dataset — potential question design bias
- Confidence via prompting ≠ true model probability (logprobs)
- 5 repetitions may be insufficient for rare failure modes

## Future Work

- Multi-model comparison (GPT-4o, Claude, Gemini Pro)
- Self-consistency decoding (majority vote over k samples)
- Agentic verification pipelines
- Larger standardized benchmarks (GSM8K, ARC, LogiQA)
- Logprob-based calibration analysis

## License

MIT
