#!/usr/bin/env python3
"""
LLM-based Evaluation Runner
Uses LLM-as-Judge to evaluate agent responses.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import yaml
import traceback

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not available. LLM evaluations will not work.")


class LLMEvalRunner:
    def __init__(self, config_path: str = "evaluation/configs/eval_config.yaml"):
        """Initialize the LLM evaluation runner."""
        self.config = self._load_config(config_path)
        self.results = []
        self.output_dir = Path(self.config["global"]["output_dir"])
        self.jsonl_dir = Path(self.config["global"]["jsonl_dir"])
        self.jsonl_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize LLM client
        if OPENAI_AVAILABLE:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
        
        # Load prompts
        self.system_prompt = self._load_prompt(
            self.config["llm_eval"]["system_prompt_template"]
        )
        self.eval_prompt_template = self._load_prompt(
            self.config["llm_eval"]["evaluation_prompt_template"]
        )
        
    def _load_config(self, config_path: str) -> Dict:
        """Load evaluation configuration."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_prompt(self, prompt_path: str) -> str:
        """Load prompt template from file."""
        with open(prompt_path, 'r') as f:
            return f.read()
    
    def _call_agent(self, agent_name: str, query: str) -> str:
        """Call the agent with a query. This is a placeholder - implement based on your agent interface."""
        # TODO: Implement actual agent calling logic
        # This should call your actual agent implementation
        return "Agent response not implemented. Please implement _call_agent method."
    
    def _evaluate_with_llm(self, query: str, agent_response: str, expected_output_type: str) -> Dict:
        """Use LLM to evaluate agent response."""
        if not self.client:
            return {
                "error": "LLM client not available",
                "correctness": 0.0,
                "completeness": 0.0,
                "faithfulness": 0.0,
                "clarity": 0.0,
                "overall_score": 0.0,
                "pass": False
            }
        
        # Format evaluation prompt
        eval_prompt = self.eval_prompt_template.format(
            query=query,
            agent_response=agent_response,
            expected_output_type=expected_output_type
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.config["llm_eval"]["model"],
                temperature=self.config["llm_eval"]["temperature"],
                max_tokens=self.config["llm_eval"]["max_tokens"],
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": eval_prompt}
                ],
                response_format={"type": "json_object"} if self.config["llm_eval"]["response_format"] == "json" else None
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            if self.config["llm_eval"]["response_format"] == "json":
                evaluation = json.loads(content)
            else:
                # Try to extract JSON from text response
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    evaluation = json.loads(json_match.group())
                else:
                    raise ValueError("Could not extract JSON from LLM response")
            
            return evaluation
            
        except Exception as e:
            return {
                "error": f"LLM evaluation failed: {str(e)}",
                "correctness": 0.0,
                "completeness": 0.0,
                "faithfulness": 0.0,
                "clarity": 0.0,
                "overall_score": 0.0,
                "pass": False
            }
    
    def _check_pass_criteria(self, evaluation: Dict, agent_config: Dict) -> bool:
        """Check if evaluation meets pass criteria."""
        min_score = agent_config["llm_tests"]["min_score_per_dimension"]
        dimensions = agent_config["llm_tests"]["dimensions"]
        
        # Check all dimension scores
        for dimension in dimensions:
            score = evaluation.get(dimension, 0.0)
            if score < min_score:
                return False
        
        # Check overall score
        overall_score = evaluation.get("overall_score", 0.0)
        if overall_score < agent_config["llm_tests"]["pass_threshold"] * 5.0:  # Convert threshold to 5.0 scale
            return False
        
        # Check for hallucinations (faithfulness must be high)
        faithfulness = evaluation.get("faithfulness", 0.0)
        if faithfulness < 3.5:  # Stricter threshold for faithfulness
            return False
        
        return True
    
    def run_tests_for_agent(self, agent_name: str, sample_size: Optional[int] = None) -> List[Dict]:
        """Run LLM evaluations for a specific agent."""
        agent_config = self.config["agents"][agent_name]
        
        if not agent_config.get("llm_tests"):
            print(f"LLM tests not configured for {agent_name}")
            return []
        
        test_file = agent_config["llm_tests"]["file"]
        if not os.path.exists(test_file):
            print(f"Test file not found: {test_file}")
            return []
        
        # Load test cases
        test_cases = []
        with open(test_file, 'r') as f:
            for line in f:
                if line.strip():
                    test_cases.append(json.loads(line))
        
        # Apply sample size if specified
        if sample_size and sample_size < len(test_cases):
            import random
            test_cases = random.sample(test_cases, sample_size)
        
        results = []
        
        print(f"\n{'='*60}")
        print(f"Running {len(test_cases)} LLM evaluations for {agent_config['name']}")
        print(f"{'='*60}\n")
        
        for test_case in test_cases:
            test_id = test_case.get("id", "unknown")
            query = test_case.get("query", "")
            expected_output_type = test_case.get("expected_output_type", "")
            
            print(f"Evaluating test: {test_id}")
            print(f"  Query: {query[:80]}...")
            
            try:
                # Call agent
                agent_response = self._call_agent(agent_name, query)
                
                # Evaluate with LLM
                evaluation = self._evaluate_with_llm(query, agent_response, expected_output_type)
                
                # Check pass criteria
                passed = self._check_pass_criteria(evaluation, agent_config)
                
                result = {
                    "test_id": test_id,
                    "agent": agent_name,
                    "query": query,
                    "expected_output_type": expected_output_type,
                    "agent_response": agent_response,
                    "evaluation": evaluation,
                    "passed": passed,
                    "timestamp": datetime.now().isoformat()
                }
                
                results.append(result)
                
                if passed:
                    print(f"  ✓ PASSED (Overall: {evaluation.get('overall_score', 0.0):.2f})")
                else:
                    print(f"  ✗ FAILED (Overall: {evaluation.get('overall_score', 0.0):.2f})")
                    if "issues" in evaluation:
                        print(f"    Issues: {', '.join(evaluation['issues'][:3])}")
                
            except Exception as e:
                error_result = {
                    "test_id": test_id,
                    "agent": agent_name,
                    "query": query,
                    "passed": False,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.now().isoformat()
                }
                results.append(error_result)
                print(f"  ✗ ERROR: {str(e)}")
        
        return results
    
    def run_all_tests(self, sample_size: Optional[int] = None) -> Dict[str, List[Dict]]:
        """Run LLM evaluations for all agents."""
        all_results = {}
        
        for agent_name in self.config["agents"]:
            agent_config = self.config["agents"][agent_name]
            if agent_config.get("llm_tests"):
                results = self.run_tests_for_agent(agent_name, sample_size)
                all_results[agent_name] = results
                
                # Save JSONL results
                jsonl_file = self.jsonl_dir / f"{agent_name}_llm_evals.jsonl"
                with open(jsonl_file, 'w') as f:
                    for result in results:
                        f.write(json.dumps(result) + '\n')
        
        return all_results
    
    def generate_report(self, results: Dict[str, List[Dict]]) -> Dict:
        """Generate aggregated report from results."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_type": "llm",
            "agents": {}
        }
        
        for agent_name, agent_results in results.items():
            total = len(agent_results)
            passed = sum(1 for r in agent_results if r.get("passed", False))
            failed = total - passed
            pass_rate = passed / total if total > 0 else 0.0
            
            # Calculate average scores
            evaluations = [r.get("evaluation", {}) for r in agent_results if "evaluation" in r]
            if evaluations:
                agent_config = self.config["agents"][agent_name]
                dimensions = agent_config["llm_tests"]["dimensions"]
                
                avg_scores = {}
                for dimension in dimensions:
                    scores = [e.get(dimension, 0.0) for e in evaluations]
                    avg_scores[dimension] = sum(scores) / len(scores) if scores else 0.0
                
                overall_scores = [e.get("overall_score", 0.0) for e in evaluations]
                avg_scores["overall"] = sum(overall_scores) / len(overall_scores) if overall_scores else 0.0
            else:
                avg_scores = {}
            
            agent_config = self.config["agents"][agent_name]
            threshold = agent_config["llm_tests"]["pass_threshold"]
            meets_threshold = pass_rate >= threshold
            
            report["agents"][agent_name] = {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": pass_rate,
                "threshold": threshold,
                "meets_threshold": meets_threshold,
                "average_scores": avg_scores,
                "failures": [
                    {
                        "test_id": r["test_id"],
                        "query": r.get("query", "")[:100],
                        "evaluation": r.get("evaluation", {}),
                        "issues": r.get("evaluation", {}).get("issues", [])
                    }
                    for r in agent_results if not r.get("passed", False)
                ]
            }
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run LLM-based evaluations")
    parser.add_argument("--agent", type=str, help="Run tests for specific agent only")
    parser.add_argument("--config", type=str, default="evaluation/configs/eval_config.yaml",
                       help="Path to evaluation config")
    parser.add_argument("--sample-size", type=int, help="Sample size for testing (for CI)")
    
    args = parser.parse_args()
    
    runner = LLMEvalRunner(args.config)
    
    if args.agent:
        results = {args.agent: runner.run_tests_for_agent(args.agent, args.sample_size)}
    else:
        results = runner.run_all_tests(args.sample_size)
    
    # Generate and save report
    report = runner.generate_report(results)
    report_file = runner.output_dir / "llm_evals_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*60}")
    print("LLM Evaluation Summary")
    print(f"{'='*60}\n")
    
    for agent_name, agent_report in report["agents"].items():
        print(f"{agent_name}:")
        print(f"  Total: {agent_report['total_tests']}")
        print(f"  Passed: {agent_report['passed']}")
        print(f"  Failed: {agent_report['failed']}")
        print(f"  Pass Rate: {agent_report['pass_rate']:.2%}")
        print(f"  Threshold: {agent_report['threshold']:.2%}")
        print(f"  Meets Threshold: {'✓' if agent_report['meets_threshold'] else '✗'}")
        if agent_report.get("average_scores"):
            print(f"  Average Scores:")
            for dim, score in agent_report["average_scores"].items():
                print(f"    {dim}: {score:.2f}")
        print()
    
    # Exit with error code if any agent fails threshold
    if any(not agent_report["meets_threshold"] for agent_report in report["agents"].values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
