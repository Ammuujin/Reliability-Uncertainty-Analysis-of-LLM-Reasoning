# Reliability & Uncertainty Analysis of LLM Reasoning

**Short Report — Draft**

---

## Abstract

Large language models (LLMs) are increasingly deployed for reasoning tasks, yet their reliability under varying prompting strategies and decoding parameters remains poorly characterized. This study presents a controlled empirical analysis of an LLM's consistency, uncertainty expression, and failure modes across 100 structured reasoning problems spanning arithmetic, logic, and multi-step categories. Using three prompt types (direct, step-by-step, uncertainty-aware) at two temperature settings (0.0, 0.7) with five repetitions each, we measure accuracy, answer variance, calibration quality, and categorize failure modes. Our findings reveal [INSERT KEY FINDINGS].

---

## 1. Introduction

As LLMs are adopted in high-stakes applications, understanding their reliability is critical. Key concerns include:

- **Consistency**: Do LLMs give the same answer when asked the same question multiple times?
- **Calibration**: When LLMs express confidence, is it well-calibrated?
- **Failure modes**: When LLMs fail, how do they fail?

### Research Questions

- **RQ1**: How does prompting strategy affect accuracy on structured reasoning tasks?
- **RQ2**: How consistent are LLM answers across repeated runs under different decoding temperatures?
- **RQ3**: How well-calibrated is an LLM's expressed confidence relative to actual correctness?

---

## 2. Experimental Setup

### Dataset

100 self-curated problems with objective answers:

- **Arithmetic** (40): Multi-step word problems
- **Logic** (30): Deduction, syllogisms, puzzles
- **Multi-step** (30): Story problems requiring 3+ reasoning steps

Difficulty distribution: ~33% easy, ~34% medium, ~33% hard.

### Model

[MODEL NAME AND VERSION]

### Prompts

| Prompt                | Goal                            |
| --------------------- | ------------------------------- |
| **Direct**            | Baseline — answer only          |
| **Step-by-step**      | Chain-of-thought reasoning      |
| **Uncertainty-aware** | Explicit uncertainty expression |

All prompts include a structured suffix requiring `CONFIDENCE: <0-100>` and `ANSWER: <answer>`.

### Parameters

- Temperatures: 0.0 (deterministic), 0.7 (moderate sampling)
- Runs per condition: 5
- Total API calls: 3,000

---

## 3. Results

### 3.1 Accuracy

[INSERT ACCURACY TABLE AND PLOT]

### 3.2 Consistency / Variance

[INSERT DISAGREEMENT AND FLIP RATE TABLE]

### 3.3 Calibration

[INSERT CONFIDENCE VS CORRECTNESS, ECE]

### 3.4 UNKNOWN Usage

[INSERT UNKNOWN RATE ANALYSIS]

---

## 4. Failure Mode Taxonomy

| Failure Mode        | Count | %   | Example |
| ------------------- | ----- | --- | ------- |
| Arithmetic slip     |       |     |         |
| Logical fallacy     |       |     |         |
| Misread question    |       |     |         |
| Formatting failure  |       |     |         |
| Contradiction       |       |     |         |
| Hallucinated fact   |       |     |         |
| Premature UNKNOWN   |       |     |         |
| Overconfident wrong |       |     |         |

---

## 5. Limitations

- Single model studied — findings may not generalize
- Self-curated dataset — potential question design bias
- Limited temperature range (only 0.0 and 0.7)
- Confidence via prompting ≠ true model probability
- 5 runs may be insufficient for rare failure modes

---

## 6. Future Work

- Multi-model comparison (GPT-4, Claude, Gemini Pro)
- Self-consistency decoding (majority vote over k samples)
- Agentic verification pipelines
- Larger standardized benchmarks (GSM8K, ARC)
- Fine-grained calibration with logprob analysis

---

## References

[TO BE ADDED]
