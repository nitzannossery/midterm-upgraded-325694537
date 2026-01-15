# Evaluation Framework - Implementation Guide

## Overview

This guide provides detailed instructions for implementing and using the evaluation framework for your financial analysis multi-agent system.

## Architecture

The evaluation framework is designed to test four agents:

1. **Market Data Agent** - 25 hard tests, 15 LLM tests, 7 human tests
2. **Fundamental & News Agent** - 25 hard tests, 15 LLM tests, 7 human tests
3. **Portfolio & Risk Agent** - 25 hard tests, 15 LLM tests, 7 human tests
4. **Summarizer Agent** - 0 hard tests, 15 LLM tests, 7 human tests

## Step-by-Step Implementation

### Step 1: Integrate Your Agents

You need to implement the `_call_agent` methods in each runner to connect to your actual agents.

#### For Hard Evaluations (`run_hard_evals.py`):

```python
def _call_agent(self, agent_name: str, input_data: Dict) -> Dict:
    """Call the agent with input data."""
    if agent_name == "market_data":
        # Example: Call your market data agent
        from your_project.agents.market_data import MarketDataAgent
        agent = MarketDataAgent()
        return agent.process(input_data)
    
    elif agent_name == "fundamental_news":
        from your_project.agents.fundamental import FundamentalAgent
        agent = FundamentalAgent()
        return agent.process(input_data)
    
    elif agent_name == "portfolio_risk":
        from your_project.agents.portfolio import PortfolioAgent
        agent = PortfolioAgent()
        return agent.process(input_data)
    
    else:
        return {"status": "error", "error": f"Unknown agent: {agent_name}"}
```

#### For LLM Evaluations (`run_llm_evals.py`):

```python
def _call_agent(self, agent_name: str, query: str) -> str:
    """Call the agent with a query."""
    if agent_name == "market_data":
        from your_project.agents.market_data import MarketDataAgent
        agent = MarketDataAgent()
        response = agent.process_query(query)
        return response.text  # Return string response
    
    # ... similar for other agents
```

### Step 2: Configure Your Environment

1. **Set API Keys**:
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Update Configuration** (if needed):
   - Edit `evaluation/configs/eval_config.yaml` to adjust thresholds
   - Modify test case files if your agent interfaces differ

### Step 3: Run Evaluations

#### Initial Testing

Start with hard evaluations (fastest, most deterministic):

```bash
# Test one agent
python evaluation/runners/run_hard_evals.py --agent market_data

# Test all agents
python evaluation/runners/run_hard_evals.py
```

#### Full Evaluation Suite

```bash
# Run everything
python evaluation/runners/run_all_evals.py

# Skip human evals (if not ready)
python evaluation/runners/run_all_evals.py --skip-human
```

#### CI/CD Testing

For continuous integration, use sample sizes:

```bash
# Quick LLM eval sample
python evaluation/runners/run_llm_evals.py --sample-size 5
```

### Step 4: Human Evaluation Process

1. **Generate Templates**:
   ```bash
   python evaluation/runners/run_human_eval_merge.py --generate-templates
   ```

2. **Distribute to Evaluators**:
   - CSV files will be created in `evaluation/reports/`
   - Each evaluator fills in scores (1-5) for each dimension
   - Save as `{agent_name}_human_evals.csv`

3. **Merge Results**:
   ```bash
   python evaluation/runners/run_human_eval_merge.py
   ```

## Test Case Customization

### Adding New Hard Tests

Edit the YAML files in `evaluation/hard/`:

```yaml
tests:
  - id: "market_026"
    name: "Your new test name"
    input:
      query: "Your test query"
      # ... other input fields
    expected_output:
      type: "your_output_type"
      # ... expected fields with validation
    validation:
      required_fields: ["field1", "field2"]
```

### Adding New LLM Tests

Add to JSONL files in `evaluation/datasets/{agent}/llm_test_cases.jsonl`:

```json
{"id": "market_llm_016", "query": "Your test query", "expected_output_type": "output_type", "context": "Test context"}
```

### Adding New Human Tests

Add to CSV files in `evaluation/datasets/{agent}/human_test_cases.csv`:

```csv
id,query,expected_output_type,context
market_human_008,"Your test query","output_type","Test context"
```

## Understanding Results

### Hard Evaluation Results

- **Pass/Fail**: Binary result per test
- **Errors**: Specific validation failures
- **Pass Rate**: Percentage of tests passing

### LLM Evaluation Results

- **Scores**: 1.0-5.0 for each dimension
- **Overall Score**: Average across dimensions
- **Issues**: List of problems identified
- **Pass**: True if all criteria met

### Human Evaluation Results

- **Scores**: 1-5 for each dimension per evaluator
- **Average Scores**: Aggregated across evaluators
- **Pass Rate**: Percentage meeting threshold

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure your agent modules are in Python path
   - Check `sys.path` modifications in runners

2. **Agent Response Format**:
   - Ensure agents return expected structure
   - Check validation rules in test cases

3. **LLM API Errors**:
   - Verify `OPENAI_API_KEY` is set
   - Check API rate limits
   - Ensure sufficient credits

4. **Test Failures**:
   - Review error messages in JSONL files
   - Check agent output format matches expected
   - Verify tolerance settings for numerical comparisons

### Debug Mode

Add debug prints in `_call_agent`:

```python
def _call_agent(self, agent_name: str, input_data: Dict) -> Dict:
    print(f"DEBUG: Calling {agent_name} with {input_data}")
    result = your_agent.process(input_data)
    print(f"DEBUG: Got result {result}")
    return result
```

## Best Practices

1. **Start Small**: Begin with one agent, one test type
2. **Iterate**: Fix issues incrementally
3. **Document**: Keep notes on agent behavior changes
4. **Version Control**: Commit test cases and results
5. **Automate**: Use CI/CD for continuous evaluation

## Advanced Usage

### Custom Validation Rules

Add custom validation in `_validate_output`:

```python
# In run_hard_evals.py
if "weights_sum_to_one" in validation and validation["weights_sum_to_one"]:
    weights = actual_output.get("weights", {})
    total = sum(weights.values())
    if abs(total - 1.0) > 0.001:
        result["passed"] = False
        result["errors"].append(f"Weights sum to {total}, expected 1.0")
```

### Custom LLM Prompts

Modify prompts in `evaluation/llm/prompts/`:
- `system_prompt.txt`: Overall evaluation instructions
- `evaluation_prompt.txt`: Per-test evaluation template

### Custom Reporting

Extend `generate_markdown_report` in `run_all_evals.py` to add custom sections.

## Performance Considerations

- **Hard Tests**: Should complete in < 1 second each
- **LLM Tests**: ~5-10 seconds per test (API latency)
- **Human Tests**: Manual process, can take hours/days

For large test suites, consider:
- Parallel execution (modify runners)
- Caching agent responses
- Sampling strategies for CI

## Next Steps

1. Implement `_call_agent` methods
2. Run initial hard evaluations
3. Fix any failures
4. Run LLM evaluations
5. Conduct human evaluations
6. Generate final report
7. Iterate based on results

## Support

For issues or questions:
1. Check error messages in JSONL files
2. Review test case definitions
3. Verify agent integration
4. Consult README.md for general guidance
