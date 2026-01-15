#!/usr/bin/env python3
"""
Hard Evaluation Runner
Runs deterministic tests with exact or tolerance-based expected outputs.
"""

import yaml
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import traceback

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class HardEvalRunner:
    def __init__(self, config_path: str = "evaluation/configs/eval_config.yaml"):
        """Initialize the hard evaluation runner."""
        self.config = self._load_config(config_path)
        self.results = []
        self.output_dir = Path(self.config["global"]["output_dir"])
        self.jsonl_dir = Path(self.config["global"]["jsonl_dir"])
        self.jsonl_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load evaluation configuration."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _validate_output(self, test: Dict, actual_output: Dict) -> Dict:
        """Validate actual output against expected output."""
        expected = test["expected_output"]
        validation = test.get("validation", {})
        result = {
            "test_id": test["id"],
            "test_name": test["name"],
            "passed": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = validation.get("required_fields", [])
        for field in required_fields:
            if field not in actual_output:
                result["passed"] = False
                result["errors"].append(f"Missing required field: {field}")
        
        # Check status
        if expected.get("status") and actual_output.get("status") != expected["status"]:
            result["passed"] = False
            result["errors"].append(
                f"Status mismatch: expected {expected['status']}, got {actual_output.get('status')}"
            )
        
        # Validate field types and values
        for field, expected_spec in expected.items():
            if field == "status" or field == "type":
                continue
                
            if field not in actual_output:
                continue
                
            actual_value = actual_output[field]
            expected_type = expected_spec.get("type")
            
            if expected_type == "float":
                if not isinstance(actual_value, (int, float)):
                    result["passed"] = False
                    result["errors"].append(f"{field} should be float, got {type(actual_value)}")
                else:
                    expected_val = expected_spec.get("value")
                    tolerance = expected_spec.get("tolerance", self.config["global"]["tolerance"]["numerical"])
                    if expected_val is not None:
                        if abs(actual_value - expected_val) > tolerance:
                            result["passed"] = False
                            result["errors"].append(
                                f"{field} value mismatch: expected {expected_val}, got {actual_value} "
                                f"(tolerance: {tolerance})"
                            )
                    # Check min/max bounds
                    if "min" in expected_spec and actual_value < expected_spec["min"]:
                        result["passed"] = False
                        result["errors"].append(f"{field} below minimum: {actual_value} < {expected_spec['min']}")
                    if "max" in expected_spec and actual_value > expected_spec["max"]:
                        result["passed"] = False
                        result["errors"].append(f"{field} above maximum: {actual_value} > {expected_spec['max']}")
            
            elif expected_type == "int":
                if not isinstance(actual_value, int):
                    result["passed"] = False
                    result["errors"].append(f"{field} should be int, got {type(actual_value)}")
                else:
                    if "min" in expected_spec and actual_value < expected_spec["min"]:
                        result["passed"] = False
                        result["errors"].append(f"{field} below minimum: {actual_value} < {expected_spec['min']}")
                    if "max" in expected_spec and actual_value > expected_spec["max"]:
                        result["passed"] = False
                        result["errors"].append(f"{field} above maximum: {actual_value} > {expected_spec['max']}")
                    if "exact" in expected_spec and actual_value != expected_spec["exact"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"{field} exact value mismatch: expected {expected_spec['exact']}, got {actual_value}"
                        )
            
            elif expected_type == "string":
                if not isinstance(actual_value, str):
                    result["passed"] = False
                    result["errors"].append(f"{field} should be string, got {type(actual_value)}")
                if "enum" in expected_spec and actual_value not in expected_spec["enum"]:
                    result["passed"] = False
                    result["errors"].append(
                        f"{field} value '{actual_value}' not in allowed values: {expected_spec['enum']}"
                    )
            
            elif expected_type == "array":
                if not isinstance(actual_value, list):
                    result["passed"] = False
                    result["errors"].append(f"{field} should be array, got {type(actual_value)}")
                else:
                    if "min_length" in expected_spec and len(actual_value) < expected_spec["min_length"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"{field} array length below minimum: {len(actual_value)} < {expected_spec['min_length']}"
                        )
                    if "max_length" in expected_spec and len(actual_value) > expected_spec["max_length"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"{field} array length above maximum: {len(actual_value)} > {expected_spec['max_length']}"
                        )
                    if "length" in expected_spec and len(actual_value) != expected_spec["length"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"{field} array length mismatch: expected {expected_spec['length']}, got {len(actual_value)}"
                        )
            
            elif expected_type == "dict":
                if not isinstance(actual_value, dict):
                    result["passed"] = False
                    result["errors"].append(f"{field} should be dict, got {type(actual_value)}")
                else:
                    if "required_keys" in expected_spec:
                        missing_keys = set(expected_spec["required_keys"]) - set(actual_value.keys())
                        if missing_keys:
                            result["passed"] = False
                            result["errors"].append(f"{field} missing required keys: {missing_keys}")
                    if "min_keys" in expected_spec and len(actual_value) < expected_spec["min_keys"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"{field} dict has fewer keys than minimum: {len(actual_value)} < {expected_spec['min_keys']}"
                        )
                    if "count" in expected_spec and len(actual_value) != expected_spec["count"]:
                        result["passed"] = False
                        result["errors"].append(
                            f"{field} dict key count mismatch: expected {expected_spec['count']}, got {len(actual_value)}"
                        )
        
        # Custom validation rules
        if "weights_sum_to_one" in validation and validation["weights_sum_to_one"]:
            # This would need to be implemented based on actual portfolio structure
            pass
        
        return result
    
    def _call_agent(self, agent_name: str, input_data: Dict) -> Dict:
        """Call the agent with input data. This is a placeholder - implement based on your agent interface."""
        # TODO: Implement actual agent calling logic
        # This should call your actual agent implementation
        # For now, return a mock response
        return {
            "status": "error",
            "error": "Agent calling not implemented. Please implement _call_agent method."
        }
    
    def run_tests_for_agent(self, agent_name: str) -> List[Dict]:
        """Run all hard tests for a specific agent."""
        agent_config = self.config["agents"][agent_name]
        
        if not agent_config["hard_tests"].get("enabled", True):
            print(f"Hard tests disabled for {agent_name}")
            return []
        
        test_file = agent_config["hard_tests"]["file"]
        if not os.path.exists(test_file):
            print(f"Test file not found: {test_file}")
            return []
        
        # Load test cases
        with open(test_file, 'r') as f:
            test_data = yaml.safe_load(f)
        
        tests = test_data.get("tests", [])
        results = []
        
        print(f"\n{'='*60}")
        print(f"Running {len(tests)} hard tests for {agent_config['name']}")
        print(f"{'='*60}\n")
        
        for test in tests:
            print(f"Running test: {test['id']} - {test['name']}")
            try:
                # Call agent
                actual_output = self._call_agent(agent_name, test["input"])
                
                # Validate output
                validation_result = self._validate_output(test, actual_output)
                validation_result["agent"] = agent_name
                validation_result["input"] = test["input"]
                validation_result["expected_output"] = test["expected_output"]
                validation_result["actual_output"] = actual_output
                validation_result["timestamp"] = datetime.now().isoformat()
                
                results.append(validation_result)
                
                if validation_result["passed"]:
                    print(f"  ✓ PASSED")
                else:
                    print(f"  ✗ FAILED: {', '.join(validation_result['errors'])}")
                    
            except Exception as e:
                error_result = {
                    "test_id": test["id"],
                    "test_name": test["name"],
                    "agent": agent_name,
                    "passed": False,
                    "errors": [f"Exception during test execution: {str(e)}"],
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.now().isoformat()
                }
                results.append(error_result)
                print(f"  ✗ ERROR: {str(e)}")
        
        return results
    
    def run_all_tests(self) -> Dict[str, List[Dict]]:
        """Run all hard tests for all agents."""
        all_results = {}
        
        for agent_name in self.config["agents"]:
            agent_config = self.config["agents"][agent_name]
            if agent_config["hard_tests"].get("enabled", True):
                results = self.run_tests_for_agent(agent_name)
                all_results[agent_name] = results
                
                # Save JSONL results
                jsonl_file = self.jsonl_dir / f"{agent_name}_hard_evals.jsonl"
                with open(jsonl_file, 'w') as f:
                    for result in results:
                        f.write(json.dumps(result) + '\n')
        
        return all_results
    
    def generate_report(self, results: Dict[str, List[Dict]]) -> Dict:
        """Generate aggregated report from results."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_type": "hard",
            "agents": {}
        }
        
        for agent_name, agent_results in results.items():
            total = len(agent_results)
            passed = sum(1 for r in agent_results if r.get("passed", False))
            failed = total - passed
            pass_rate = passed / total if total > 0 else 0.0
            
            agent_config = self.config["agents"][agent_name]
            threshold = agent_config["hard_tests"]["pass_threshold"]
            meets_threshold = pass_rate >= threshold
            
            report["agents"][agent_name] = {
                "total_tests": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": pass_rate,
                "threshold": threshold,
                "meets_threshold": meets_threshold,
                "failures": [
                    {
                        "test_id": r["test_id"],
                        "test_name": r["test_name"],
                        "errors": r.get("errors", [])
                    }
                    for r in agent_results if not r.get("passed", False)
                ]
            }
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run hard evaluations")
    parser.add_argument("--agent", type=str, help="Run tests for specific agent only")
    parser.add_argument("--config", type=str, default="evaluation/configs/eval_config.yaml",
                       help="Path to evaluation config")
    
    args = parser.parse_args()
    
    runner = HardEvalRunner(args.config)
    
    if args.agent:
        results = {args.agent: runner.run_tests_for_agent(args.agent)}
    else:
        results = runner.run_all_tests()
    
    # Generate and save report
    report = runner.generate_report(results)
    report_file = runner.output_dir / "hard_evals_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*60}")
    print("Hard Evaluation Summary")
    print(f"{'='*60}\n")
    
    for agent_name, agent_report in report["agents"].items():
        print(f"{agent_name}:")
        print(f"  Total: {agent_report['total_tests']}")
        print(f"  Passed: {agent_report['passed']}")
        print(f"  Failed: {agent_report['failed']}")
        print(f"  Pass Rate: {agent_report['pass_rate']:.2%}")
        print(f"  Threshold: {agent_report['threshold']:.2%}")
        print(f"  Meets Threshold: {'✓' if agent_report['meets_threshold'] else '✗'}")
        print()
    
    # Exit with error code if any agent fails threshold
    if any(not agent_report["meets_threshold"] for agent_report in report["agents"].values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
