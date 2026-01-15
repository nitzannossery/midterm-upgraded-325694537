# Financial Analysis Multi-Agent System - Evaluation Report

**Generated:** {{ timestamp }}

---

## Executive Summary

This report presents the comprehensive evaluation results for the Financial Analysis Multi-Agent System, including hard (deterministic) tests, LLM-based evaluations, and human grader assessments.

---

## Evaluation Methodology

### Hard Evaluations
- **Type**: Deterministic tests with exact or tolerance-based expected outputs
- **Purpose**: Verify correctness of calculations, data retrieval, and error handling
- **Pass Criteria**: 90% of tests must pass for each agent

### LLM Evaluations
- **Type**: Model-as-Judge evaluations using GPT-4
- **Dimensions**: Correctness, Completeness, Faithfulness, Clarity
- **Pass Criteria**: 80% pass rate with minimum 3.0/5.0 per dimension

### Human Evaluations
- **Type**: Expert human grader assessments
- **Dimensions**: Usefulness, Trustworthiness, Reasoning Quality, Decision Confidence
- **Pass Criteria**: 75% pass rate with minimum 3.0/5.0 per dimension

---

## Results

{{ results_content }}

---

## Failure Analysis

{{ failure_analysis }}

---

## Recommendations

{{ recommendations }}

---

## Appendix

### Configuration
- Evaluation config: `evaluation/configs/eval_config.yaml`
- Test cases: `evaluation/hard/`, `evaluation/datasets/`
- Reports: `evaluation/reports/`

### Reproducibility
All evaluations are reproducible. To rerun:
```bash
python evaluation/runners/run_all_evals.py
```
