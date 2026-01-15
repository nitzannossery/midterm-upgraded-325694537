#!/usr/bin/env python3
"""
Retrieval Evaluation Runner
Evaluates RAG/evidence-based retrieval capabilities.
Checks that agents retrieve correct documents, cite sources, and handle missing data appropriately.
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


class RetrievalEvalRunner:
    def __init__(self, config_path: str = "evaluation/configs/eval_config.yaml"):
        """Initialize the retrieval evaluation runner."""
        self.config = self._load_config(config_path)
        self.results = []
        self.output_dir = Path(self.config["global"]["output_dir"])
        self.jsonl_dir = Path(self.config["global"]["jsonl_dir"])
        self.jsonl_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load evaluation configuration."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _call_agent(self, agent_name: str, query: str) -> Dict:
        """Call the agent with a query. This is a placeholder - implement based on your agent interface."""
        # TODO: Implement actual agent calling logic
        # This should call your actual agent implementation
        return {
            "status": "error",
            "error": "Agent calling not implemented. Please implement _call_agent method."
        }
    
    def _check_retrieval_criteria(self, test_case: Dict, agent_response: Dict) -> Dict:
        """Check if agent response meets retrieval evaluation criteria."""
        expected_checks = test_case.get("expected_checks", [])
        result = {
            "test_id": test_case["id"],
            "query": test_case["query"],
            "passed": True,
            "checks": {},
            "errors": [],
            "warnings": []
        }
        
        # Check 1: Document Retrieved
        if "document_retrieved" in expected_checks:
            has_document = (
                "document" in agent_response or
                "source" in agent_response or
                "retrieved_document" in agent_response or
                agent_response.get("status") == "success"
            )
            result["checks"]["document_retrieved"] = has_document
            if not has_document:
                result["passed"] = False
                result["errors"].append("No document retrieved or referenced")
        
        # Check 2: Value Quoted from Source
        if "value_quoted_from_source" in expected_checks:
            has_quoted_value = (
                "value" in agent_response or
                "quoted_value" in agent_response or
                any(keyword in str(agent_response).lower() 
                    for keyword in ["according to", "from", "reported", "stated"])
            )
            result["checks"]["value_quoted_from_source"] = has_quoted_value
            if not has_quoted_value:
                result["passed"] = False
                result["errors"].append("Value not clearly quoted from source")
        
        # Check 3: Citation Included
        if "citation_included" in expected_checks:
            has_citation = (
                "citation" in agent_response or
                "source" in agent_response or
                "reference" in agent_response or
                "url" in agent_response or
                any(keyword in str(agent_response).lower() 
                    for keyword in ["source:", "reference:", "filing", "report"])
            )
            result["checks"]["citation_included"] = has_citation
            if not has_citation:
                result["passed"] = False
                result["errors"].append("No citation or reference included")
        
        # Check 4: Value Consistent with Document
        if "value_consistent_with_document" in expected_checks:
            # This would require comparing against actual document
            # For now, check if value is present and numeric
            has_consistent_value = (
                "value" in agent_response or
                any(keyword in str(agent_response).lower() 
                    for keyword in ["$", "billion", "million", "%", "ratio"])
            )
            result["checks"]["value_consistent_with_document"] = has_consistent_value
            if not has_consistent_value:
                result["warnings"].append("Cannot verify value consistency without document access")
        
        # Check 5: Explicit Uncertainty When No Source
        if "explicit_uncertainty_when_no_source" in expected_checks:
            response_text = str(agent_response).lower()
            has_explicit_uncertainty = (
                "no verified source" in response_text or
                "no source found" in response_text or
                "not found" in response_text or
                "unable to find" in response_text or
                "no document" in response_text
            )
            result["checks"]["explicit_uncertainty_when_no_source"] = has_explicit_uncertainty
            
            # Check for hallucination (automatic fail)
            has_hallucination = (
                "value" in agent_response and
                not has_explicit_uncertainty and
                agent_response.get("status") != "error"
            )
            if has_hallucination:
                result["passed"] = False
                result["errors"].append("HALLUCINATION DETECTED: Provided value without source")
            elif not has_explicit_uncertainty:
                result["passed"] = False
                result["errors"].append("Missing explicit uncertainty statement when no source found")
        
        return result
    
    def run_tests_for_agent(self, agent_name: str) -> List[Dict]:
        """Run retrieval evaluations for a specific agent."""
        agent_config = self.config["agents"][agent_name]
        
        if not agent_config.get("retrieval_tests"):
            print(f"Retrieval tests not configured for {agent_name}")
            return []
        
        test_file = agent_config["retrieval_tests"]["file"]
        if not os.path.exists(test_file):
            print(f"Test file not found: {test_file}")
            return []
        
        # Load test cases
        test_cases = []
        with open(test_file, 'r') as f:
            for line in f:
                if line.strip():
                    test_cases.append(json.loads(line))
        
        results = []
        
        print(f"\n{'='*60}")
        print(f"Running {len(test_cases)} retrieval evaluations for {agent_config['name']}")
        print(f"{'='*60}\n")
        
        for test_case in test_cases:
            test_id = test_case.get("id", "unknown")
            query = test_case.get("query", "")
            
            print(f"Evaluating test: {test_id}")
            print(f"  Query: {query[:80]}...")
            
            try:
                # Call agent
                agent_response = self._call_agent(agent_name, query)
                
                # Check retrieval criteria
                evaluation_result = self._check_retrieval_criteria(test_case, agent_response)
                evaluation_result["agent"] = agent_name
                evaluation_result["agent_response"] = agent_response
                evaluation_result["expected_checks"] = test_case.get("expected_checks", [])
                evaluation_result["timestamp"] = datetime.now().isoformat()
                
                results.append(evaluation_result)
                
                if evaluation_result["passed"]:
                    print(f"  ✓ PASSED")
                else:
                    print(f"  ✗ FAILED: {', '.join(evaluation_result['errors'])}")
                    if evaluation_result.get("warnings"):
                        print(f"    Warnings: {', '.join(evaluation_result['warnings'])}")
                
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
    
    def run_all_tests(self) -> Dict[str, List[Dict]]:
        """Run retrieval evaluations for all agents."""
        all_results = {}
        
        for agent_name in self.config["agents"]:
            agent_config = self.config["agents"][agent_name]
            if agent_config.get("retrieval_tests"):
                results = self.run_tests_for_agent(agent_name)
                all_results[agent_name] = results
                
                # Save JSONL results
                jsonl_file = self.jsonl_dir / f"{agent_name}_retrieval_evals.jsonl"
                with open(jsonl_file, 'w') as f:
                    for result in results:
                        f.write(json.dumps(result) + '\n')
        
        return all_results
    
    def generate_report(self, results: Dict[str, List[Dict]]) -> Dict:
        """Generate aggregated report from results."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_type": "retrieval",
            "agents": {}
        }
        
        for agent_name, agent_results in results.items():
            total = len(agent_results)
            passed = sum(1 for r in agent_results if r.get("passed", False))
            failed = total - passed
            pass_rate = passed / total if total > 0 else 0.0
            
            # Count check failures
            check_failures = {}
            for result in agent_results:
                for check_name, check_passed in result.get("checks", {}).items():
                    if check_name not in check_failures:
                        check_failures[check_name] = {"passed": 0, "failed": 0}
                    if check_passed:
                        check_failures[check_name]["passed"] += 1
                    else:
                        check_failures[check_name]["failed"] += 1
            
            agent_config = self.config["agents"][agent_name]
            threshold = agent_config["retrieval_tests"]["pass_threshold"]
            meets_threshold = pass_rate >= threshold
            
            report["agents"][agent_name] = {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": pass_rate,
                "threshold": threshold,
                "meets_threshold": meets_threshold,
                "check_failures": check_failures,
                "failures": [
                    {
                        "test_id": r["test_id"],
                        "query": r.get("query", "")[:100],
                        "errors": r.get("errors", [])
                    }
                    for r in agent_results if not r.get("passed", False)
                ]
            }
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run retrieval evaluations")
    parser.add_argument("--agent", type=str, help="Run tests for specific agent only")
    parser.add_argument("--config", type=str, default="evaluation/configs/eval_config.yaml",
                       help="Path to evaluation config")
    
    args = parser.parse_args()
    
    runner = RetrievalEvalRunner(args.config)
    
    if args.agent:
        results = {args.agent: runner.run_tests_for_agent(args.agent)}
    else:
        results = runner.run_all_tests()
    
    # Generate and save report
    report = runner.generate_report(results)
    report_file = runner.output_dir / "retrieval_evals_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*60}")
    print("Retrieval Evaluation Summary")
    print(f"{'='*60}\n")
    
    for agent_name, agent_report in report["agents"].items():
        print(f"{agent_name}:")
        print(f"  Total: {agent_report['total_tests']}")
        print(f"  Passed: {agent_report['passed']}")
        print(f"  Failed: {agent_report['failed']}")
        print(f"  Pass Rate: {agent_report['pass_rate']:.2%}")
        print(f"  Threshold: {agent_report['threshold']:.2%}")
        print(f"  Meets Threshold: {'✓' if agent_report['meets_threshold'] else '✗'}")
        if agent_report.get("check_failures"):
            print(f"  Check Failures:")
            for check_name, check_stats in agent_report["check_failures"].items():
                print(f"    {check_name}: {check_stats['passed']} passed, {check_stats['failed']} failed")
        print()
    
    # Exit with error code if any agent fails threshold
    if any(not agent_report["meets_threshold"] for agent_report in report["agents"].values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
