#!/usr/bin/env python3
"""
System-Level Tests Runner
Runs cross-agent, regression, and edge case tests.
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


class SystemTestRunner:
    def __init__(self, config_path: str = "evaluation/configs/eval_config.yaml"):
        """Initialize the system test runner."""
        self.config = self._load_config(config_path)
        self.results = []
        self.output_dir = Path(self.config["global"]["output_dir"])
        self.jsonl_dir = Path(self.config["global"]["jsonl_dir"])
        self.jsonl_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load evaluation configuration."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _call_system(self, test: Dict) -> Dict:
        """Call the system/orchestrator with test input. This is a placeholder."""
        # TODO: Implement actual system/orchestrator calling logic
        return {
            "status": "error",
            "error": "System calling not implemented. Please implement _call_system method."
        }
    
    def _validate_system_output(self, test: Dict, actual_output: Dict) -> Dict:
        """Validate system output against expected output."""
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
            if expected["status"] == "success_or_warning" and actual_output.get("status") in ["success", "warning"]:
                pass  # Acceptable
            else:
                result["passed"] = False
                result["errors"].append(
                    f"Status mismatch: expected {expected['status']}, got {actual_output.get('status')}"
                )
        
        # Validate specific checks
        if "all_expected_agents_present" in validation and validation["all_expected_agents_present"]:
            agents_called = actual_output.get("agents_called", [])
            expected_agents = test["input"].get("expected_agents", [])
            missing = set(expected_agents) - set(agents_called)
            if missing:
                result["passed"] = False
                result["errors"].append(f"Missing agents: {missing}")
        
        if "graceful_error_handling" in validation and validation["graceful_error_handling"]:
            if not actual_output.get("error_handled_gracefully", False):
                result["passed"] = False
                result["errors"].append("Error not handled gracefully")
        
        if "uncertainty_explicitly_stated" in validation and validation["uncertainty_explicitly_stated"]:
            response_text = str(actual_output).lower()
            if not any(keyword in response_text for keyword in ["insufficient", "not found", "unavailable", "uncertain"]):
                result["passed"] = False
                result["errors"].append("Uncertainty not explicitly stated")
        
        return result
    
    def run_tests(self, test_type: str) -> List[Dict]:
        """Run system tests of a specific type."""
        if "system_tests" not in self.config:
            print(f"System tests not configured")
            return []
        
        test_config = self.config["system_tests"].get(test_type)
        if not test_config:
            print(f"Test type {test_type} not configured")
            return []
        
        test_file = test_config["file"]
        if not os.path.exists(test_file):
            print(f"Test file not found: {test_file}")
            return []
        
        # Load test cases
        with open(test_file, 'r') as f:
            test_data = yaml.safe_load(f)
        
        tests = test_data.get("tests", [])
        results = []
        
        print(f"\n{'='*60}")
        print(f"Running {len(tests)} {test_config['name']}")
        print(f"{'='*60}\n")
        
        for test in tests:
            print(f"Running test: {test['id']} - {test['name']}")
            try:
                # Call system
                actual_output = self._call_system(test)
                
                # Validate output
                validation_result = self._validate_system_output(test, actual_output)
                validation_result["test_type"] = test_type
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
                    "test_type": test_type,
                    "passed": False,
                    "errors": [f"Exception during test execution: {str(e)}"],
                    "traceback": traceback.format_exc(),
                    "timestamp": datetime.now().isoformat()
                }
                results.append(error_result)
                print(f"  ✗ ERROR: {str(e)}")
        
        return results
    
    def run_all_system_tests(self) -> Dict[str, List[Dict]]:
        """Run all system-level tests."""
        all_results = {}
        
        test_types = ["cross_agent", "regression", "edge_cases"]
        
        for test_type in test_types:
            if test_type in self.config.get("system_tests", {}):
                results = self.run_tests(test_type)
                all_results[test_type] = results
                
                # Save JSONL results
                jsonl_file = self.jsonl_dir / f"system_{test_type}_tests.jsonl"
                with open(jsonl_file, 'w') as f:
                    for result in results:
                        f.write(json.dumps(result) + '\n')
        
        return all_results
    
    def generate_report(self, results: Dict[str, List[Dict]]) -> Dict:
        """Generate aggregated report from results."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_type": "system_tests",
            "test_types": {}
        }
        
        for test_type, test_results in results.items():
            total = len(test_results)
            passed = sum(1 for r in test_results if r.get("passed", False))
            failed = total - passed
            pass_rate = passed / total if total > 0 else 0.0
            
            test_config = self.config["system_tests"][test_type]
            threshold = test_config["pass_threshold"]
            meets_threshold = pass_rate >= threshold
            
            report["test_types"][test_type] = {
                "name": test_config["name"],
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
                    for r in test_results if not r.get("passed", False)
                ]
            }
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run system-level tests")
    parser.add_argument("--test-type", type=str, choices=["cross_agent", "regression", "edge_cases", "all"],
                       default="all", help="Type of system tests to run")
    parser.add_argument("--config", type=str, default="evaluation/configs/eval_config.yaml",
                       help="Path to evaluation config")
    
    args = parser.parse_args()
    
    runner = SystemTestRunner(args.config)
    
    if args.test_type == "all":
        results = runner.run_all_system_tests()
    else:
        results = {args.test_type: runner.run_tests(args.test_type)}
    
    # Generate and save report
    report = runner.generate_report(results)
    report_file = runner.output_dir / "system_tests_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*60}")
    print("System Tests Summary")
    print(f"{'='*60}\n")
    
    for test_type, test_report in report["test_types"].items():
        print(f"{test_report['name']}:")
        print(f"  Total: {test_report['total_tests']}")
        print(f"  Passed: {test_report['passed']}")
        print(f"  Failed: {test_report['failed']}")
        print(f"  Pass Rate: {test_report['pass_rate']:.2%}")
        print(f"  Threshold: {test_report['threshold']:.2%}")
        print(f"  Meets Threshold: {'✓' if test_report['meets_threshold'] else '✗'}")
        print()
    
    # Exit with error code if any test type fails threshold
    if any(not test_report["meets_threshold"] for test_report in report["test_types"].values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
