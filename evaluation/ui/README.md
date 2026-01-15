# Evaluation UI - Separation of Concerns

## ⚠️ Important: UI vs Evaluation Separation

This directory contains the **user-facing UI** for the Financial Multi-Agent System.

### ✅ UI Purpose (Inference Mode)
- **Accepts real user queries** (free-text financial questions)
- **Provides answers** from the multi-agent system
- **No test cases** or evaluation datasets
- **No ground truth** or expected answers

### ❌ What UI Does NOT Contain
- Test questions from evaluation datasets
- Hard test cases (YAML files)
- LLM test cases (JSONL files)
- Retrieval test cases
- Human evaluation prompts
- Expected outputs or ground truth
- Evaluation criteria or rubrics

### ✅ Evaluation Framework Location
All test cases and evaluation logic are in:
- `evaluation/hard/` - Hard/deterministic tests
- `evaluation/datasets/` - LLM, retrieval, human test cases
- `evaluation/runners/` - Evaluation execution scripts
- `evaluation/system/` - System-level tests

### 🔧 Running Evaluations
Evaluations are executed **offline** via:
```bash
# Run all evaluations
python evaluation/runners/run_all_evals.py

# Run specific evaluation types
python evaluation/runners/run_hard_evals.py
python evaluation/runners/run_llm_evals.py
python evaluation/runners/run_retrieval_evals.py
python evaluation/runners/run_system_tests.py
```

### 📋 Architecture Principle
**Clear separation between:**
- **Inference mode**: User → System → Answer (via UI)
- **Evaluation mode**: Dataset → System → Metrics (via runners)

This ensures:
- UI remains clean and user-focused
- Test suite maintains integrity
- No confusion between demo and production system
- Proper evaluation methodology

### 📝 Files in This Directory
- `dashboard.html` - Main user interface (inference only)
- `README.md` - This file (separation documentation)

### 🚫 Removed Files
- `test_queries.html` - **REMOVED** (test queries belong in evaluation framework, not UI)

---

**Note**: Test questions are part of the evaluation framework and are executed offline. The UI is strictly reserved for real user inference, ensuring a clean separation between usage and evaluation.
