# Financial Analysis Multi-Agent System - Evaluation Framework

**GitHub Repository**: [https://github.com/nitzannossery/midterm-upgraded-325694537](https://github.com/nitzannossery/midterm-upgraded-325694537)

## Overview

This repository contains a production-grade evaluation framework for a multi-agent financial analysis system. The system consists of specialized agents coordinated by an orchestrator:

- **Market Data Agent**: Retrieves prices, returns, benchmarks, and FX data
- **Fundamental & News Agent**: Extracts financial statements, ratios, and analyzes news sentiment
- **Portfolio & Risk Agent**: Computes risk metrics and generates investment recommendations
- **Final Answer / Summarizer Agent**: Synthesizes outputs from all agents into coherent answers

## Evaluation Framework

### Evaluation Types

#### 1. Hard Evaluations (Deterministic)
- **Purpose**: Verify correctness with exact or tolerance-based expected outputs
- **Format**: YAML-defined test cases
- **Coverage**: 20-25 tests per agent (except summarizer)
- **Pass Threshold**: 90%

#### 2. LLM Evaluations (Model-as-Judge)
- **Purpose**: Assess quality using GPT-4 as evaluator
- **Dimensions**: Correctness, Completeness, Faithfulness, Clarity
- **Coverage**: 10-15 tests per agent
- **Pass Threshold**: 80% with minimum 3.0/5.0 per dimension

#### 3. Human Evaluations
- **Purpose**: Expert assessment of agent outputs
- **Dimensions**: Usefulness, Trustworthiness, Reasoning Quality, Decision Confidence
- **Coverage**: 5-7 tests per agent
- **Pass Threshold**: 75% with minimum 3.0/5.0 per dimension

### Directory Structure

```
evaluation/
├── configs/
│   └── eval_config.yaml          # Central evaluation configuration
├── datasets/
│   ├── market_agent/             # Test cases for market data agent
│   ├── fundamental_agent/         # Test cases for fundamental agent
│   ├── portfolio_agent/          # Test cases for portfolio agent
│   └── summarizer/               # Test cases for summarizer agent
├── hard/
│   ├── market_agent_tests.yaml    # Hard tests for market agent
│   ├── fundamental_agent_tests.yaml
│   └── portfolio_agent_tests.yaml
├── llm/
│   └── prompts/                  # LLM evaluation prompts
├── human/
│   ├── market_agent_rubric.md    # Human evaluation rubrics
│   ├── fundamental_agent_rubric.md
│   ├── portfolio_agent_rubric.md
│   └── summarizer_rubric.md
├── runners/
│   ├── run_hard_evals.py          # Hard evaluation runner
│   ├── run_llm_evals.py           # LLM evaluation runner
│   ├── run_human_eval_merge.py    # Human evaluation merger
│   └── run_all_evals.py           # Master evaluation runner
└── reports/
    ├── jsonl/                     # JSONL results per test
    ├── *.json                     # Aggregated JSON reports
    └── evaluation_report.md       # Comprehensive Markdown report
```

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

1. Set up your evaluation configuration in `evaluation/configs/eval_config.yaml`
2. For LLM evaluations, set the `OPENAI_API_KEY` environment variable:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

### Running Evaluations

#### Run All Evaluations
```bash
python evaluation/runners/run_all_evals.py
```

#### Run Specific Evaluation Type
```bash
# Hard evaluations only
python evaluation/runners/run_hard_evals.py

# LLM evaluations only
python evaluation/runners/run_llm_evals.py

# Process human evaluations
python evaluation/runners/run_human_eval_merge.py
```

#### Run for Specific Agent
```bash
python evaluation/runners/run_hard_evals.py --agent market_data
python evaluation/runners/run_llm_evals.py --agent fundamental_news
```

#### CI Mode (Sample Size)
```bash
# Run subset of LLM evals for CI
python evaluation/runners/run_llm_evals.py --sample-size 5
```

## Agent Integration

To integrate your agents with the evaluation framework, you need to implement the `_call_agent` method in each runner:

### Example: Hard Evaluation Runner

```python
def _call_agent(self, agent_name: str, input_data: Dict) -> Dict:
    """Call the agent with input data."""
    if agent_name == "market_data":
        # Call your market data agent
        return market_data_agent.process(input_data)
    elif agent_name == "fundamental_news":
        # Call your fundamental agent
        return fundamental_agent.process(input_data)
    # ... etc
```

### Example: LLM Evaluation Runner

```python
def _call_agent(self, agent_name: str, query: str) -> str:
    """Call the agent with a query."""
    if agent_name == "market_data":
        response = market_data_agent.process_query(query)
        return response.text  # Return string response
    # ... etc
```

## Test Case Format

### Hard Evaluation Test (YAML)

```yaml
tests:
  - id: "market_001"
    name: "Retrieve single stock price"
    input:
      query: "Get the closing price of AAPL on 2024-01-15"
      symbol: "AAPL"
      date: "2024-01-15"
    expected_output:
      type: "price_data"
      symbol: "AAPL"
      date: "2024-01-15"
      close_price:
        type: "float"
        tolerance: 0.01
      status: "success"
    validation:
      required_fields: ["symbol", "date", "close_price", "status"]
```

### LLM Evaluation Test (JSONL)

```json
{"id": "market_llm_001", "query": "Get the closing price of AAPL on 2024-01-15 and explain any data quality issues", "expected_output_type": "price_data_with_quality_notes", "context": "Market data retrieval with quality assessment"}
```

### Human Evaluation Test (CSV)

```csv
id,query,expected_output_type,context
market_human_001,"Get the closing price of AAPL on 2024-01-15 and explain any data quality issues","price_data_with_quality_notes","Market data retrieval with quality assessment"
```

## Human Evaluation Process

1. **Generate Templates**: Create evaluation templates for human graders
   ```bash
   python evaluation/runners/run_human_eval_merge.py --generate-templates
   ```

2. **Fill Evaluations**: Human graders fill in the CSV templates with scores (1-5) for each dimension

3. **Merge Results**: Process and merge human evaluation results
   ```bash
   python evaluation/runners/run_human_eval_merge.py
   ```

## CI/CD Integration

The evaluation framework includes GitHub Actions workflows:

- **Hard Evaluations**: Run on every push/PR (required to pass)
- **LLM Evaluations**: Smoke test (5 samples) on PRs, full suite on main branch
- **Full Evaluation**: Comprehensive report generation

See `.github/workflows/evaluation.yml` for details.

## Quality Rules

### Non-Negotiable Requirements

1. **No Hallucinations**: Agents must never invent numbers or make unsupported claims
2. **Explicit Uncertainty**: Any uncertainty must be clearly stated
3. **Structured Outputs**: All agents must return structured, parseable outputs
4. **Reproducibility**: All evaluations must be reproducible
5. **Source Citations**: Financial data must be traceable to sources

### Evaluation Standards

- **Hard Tests**: Must be deterministic and fast (< 1 second per test)
- **LLM Tests**: Must use strict JSON output format
- **Human Tests**: Must follow rubric consistently

## Reporting

### JSON Reports

- `hard_evals_report.json`: Aggregated hard evaluation results
- `llm_evals_report.json`: Aggregated LLM evaluation results
- `human_evals_report.json`: Aggregated human evaluation results

### JSONL Results

Individual test results are saved in `evaluation/reports/jsonl/`:
- `{agent_name}_hard_evals.jsonl`
- `{agent_name}_llm_evals.jsonl`
- `{agent_name}_human_evals.jsonl`

### Markdown Report

Comprehensive report: `evaluation/reports/evaluation_report.md`

## Troubleshooting

### Common Issues

1. **Agent Not Found**: Ensure `_call_agent` method is implemented in runners
2. **LLM API Errors**: Check `OPENAI_API_KEY` environment variable
3. **Test File Not Found**: Verify test case files exist in expected locations
4. **Import Errors**: Ensure all dependencies are installed (`pip install -r requirements.txt`)

### Debug Mode

Run with verbose output:
```bash
python evaluation/runners/run_hard_evals.py --agent market_data 2>&1 | tee eval.log
```

## Contributing

When adding new test cases:

1. Follow existing test case format
2. Ensure tests are deterministic
3. Update agent configuration in `eval_config.yaml` if needed
4. Run full evaluation suite before submitting

## License

[Your License Here]

## Contact

[Your Contact Information]
