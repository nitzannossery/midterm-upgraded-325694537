#!/usr/bin/env python3
"""
Verification Script for Evaluation Framework
Checks that all components are in place and properly configured.
"""

import os
import sys
from pathlib import Path
import yaml
import json


class EvaluationFrameworkVerifier:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.errors = []
        self.warnings = []
        self.checks_passed = 0
        self.total_checks = 0
    
    def check(self, condition: bool, message: str, is_error: bool = True):
        """Record a check result."""
        self.total_checks += 1
        if condition:
            self.checks_passed += 1
            print(f"  ✓ {message}")
        else:
            if is_error:
                self.errors.append(message)
                print(f"  ✗ ERROR: {message}")
            else:
                self.warnings.append(message)
                print(f"  ⚠ WARNING: {message}")
    
    def verify_structure(self):
        """Verify directory structure exists."""
        print("\n" + "="*60)
        print("VERIFYING DIRECTORY STRUCTURE")
        print("="*60)
        
        required_dirs = [
            "evaluation/configs",
            "evaluation/datasets/market_agent",
            "evaluation/datasets/fundamental_agent",
            "evaluation/datasets/portfolio_agent",
            "evaluation/datasets/summarizer",
            "evaluation/hard",
            "evaluation/llm/prompts",
            "evaluation/human",
            "evaluation/runners",
            "evaluation/reports",
            ".github/workflows"
        ]
        
        for dir_path in required_dirs:
            full_path = self.base_path / dir_path
            self.check(full_path.exists(), f"Directory exists: {dir_path}")
    
    def verify_config_files(self):
        """Verify configuration files exist and are valid."""
        print("\n" + "="*60)
        print("VERIFYING CONFIGURATION FILES")
        print("="*60)
        
        config_file = self.base_path / "evaluation/configs/eval_config.yaml"
        self.check(config_file.exists(), "Config file exists: eval_config.yaml")
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Check required sections
                required_sections = ["global", "agents", "llm_eval", "reporting", "ci"]
                for section in required_sections:
                    self.check(section in config, f"Config has section: {section}")
                
                # Check agents
                if "agents" in config:
                    expected_agents = ["market_data", "fundamental_news", "portfolio_risk", "summarizer"]
                    for agent in expected_agents:
                        self.check(agent in config["agents"], f"Agent configured: {agent}")
                
            except Exception as e:
                self.check(False, f"Config file is invalid YAML: {e}")
    
    def verify_test_files(self):
        """Verify test case files exist."""
        print("\n" + "="*60)
        print("VERIFYING TEST CASE FILES")
        print("="*60)
        
        # Hard evaluation tests
        hard_tests = [
            "evaluation/hard/market_agent_tests.yaml",
            "evaluation/hard/fundamental_agent_tests.yaml",
            "evaluation/hard/portfolio_agent_tests.yaml"
        ]
        
        for test_file in hard_tests:
            full_path = self.base_path / test_file
            self.check(full_path.exists(), f"Hard test file exists: {test_file}")
            
            if full_path.exists():
                try:
                    with open(full_path, 'r') as f:
                        data = yaml.safe_load(f)
                    if data and "tests" in data:
                        count = len(data["tests"])
                        self.check(count >= 20, f"{test_file} has {count} tests (>=20)", is_error=False)
                except Exception as e:
                    self.check(False, f"{test_file} is invalid YAML: {e}")
        
        # LLM test cases
        llm_tests = [
            "evaluation/datasets/market_agent/llm_test_cases.jsonl",
            "evaluation/datasets/fundamental_agent/llm_test_cases.jsonl",
            "evaluation/datasets/portfolio_agent/llm_test_cases.jsonl",
            "evaluation/datasets/summarizer/llm_test_cases.jsonl"
        ]
        
        for test_file in llm_tests:
            full_path = self.base_path / test_file
            self.check(full_path.exists(), f"LLM test file exists: {test_file}")
            
            if full_path.exists():
                try:
                    count = 0
                    with open(full_path, 'r') as f:
                        for line in f:
                            if line.strip():
                                json.loads(line)
                                count += 1
                    self.check(count >= 10, f"{test_file} has {count} tests (>=10)", is_error=False)
                except Exception as e:
                    self.check(False, f"{test_file} has invalid JSONL: {e}")
        
        # Human test cases
        human_tests = [
            "evaluation/datasets/market_agent/human_test_cases.csv",
            "evaluation/datasets/fundamental_agent/human_test_cases.csv",
            "evaluation/datasets/portfolio_agent/human_test_cases.csv",
            "evaluation/datasets/summarizer/human_test_cases.csv"
        ]
        
        for test_file in human_tests:
            full_path = self.base_path / test_file
            self.check(full_path.exists(), f"Human test file exists: {test_file}")
    
    def verify_runners(self):
        """Verify evaluation runner scripts exist."""
        print("\n" + "="*60)
        print("VERIFYING EVALUATION RUNNERS")
        print("="*60)
        
        runners = [
            "evaluation/runners/run_hard_evals.py",
            "evaluation/runners/run_llm_evals.py",
            "evaluation/runners/run_human_eval_merge.py",
            "evaluation/runners/run_all_evals.py"
        ]
        
        for runner in runners:
            full_path = self.base_path / runner
            self.check(full_path.exists(), f"Runner exists: {runner}")
            
            if full_path.exists():
                # Check if file is executable or at least readable
                self.check(full_path.is_file(), f"{runner} is a file")
                
                # Check for required methods/classes
                with open(full_path, 'r') as f:
                    content = f.read()
                    if "run_hard_evals" in runner:
                        self.check("_call_agent" in content or "TODO" in content, 
                                 f"{runner} has _call_agent method (or TODO)", is_error=False)
    
    def verify_prompts(self):
        """Verify LLM evaluation prompts exist."""
        print("\n" + "="*60)
        print("VERIFYING LLM PROMPTS")
        print("="*60)
        
        prompts = [
            "evaluation/llm/prompts/system_prompt.txt",
            "evaluation/llm/prompts/evaluation_prompt.txt"
        ]
        
        for prompt_file in prompts:
            full_path = self.base_path / prompt_file
            self.check(full_path.exists(), f"Prompt file exists: {prompt_file}")
            
            if full_path.exists():
                with open(full_path, 'r') as f:
                    content = f.read()
                    self.check(len(content) > 100, f"{prompt_file} has content (>100 chars)", is_error=False)
    
    def verify_rubrics(self):
        """Verify human evaluation rubrics exist."""
        print("\n" + "="*60)
        print("VERIFYING HUMAN EVALUATION RUBRICS")
        print("="*60)
        
        rubrics = [
            "evaluation/human/market_agent_rubric.md",
            "evaluation/human/fundamental_agent_rubric.md",
            "evaluation/human/portfolio_agent_rubric.md",
            "evaluation/human/summarizer_rubric.md"
        ]
        
        for rubric_file in rubrics:
            full_path = self.base_path / rubric_file
            self.check(full_path.exists(), f"Rubric exists: {rubric_file}")
    
    def verify_documentation(self):
        """Verify documentation files exist."""
        print("\n" + "="*60)
        print("VERIFYING DOCUMENTATION")
        print("="*60)
        
        docs = [
            "README.md",
            "EVALUATION_GUIDE.md",
            "PROJECT_SUMMARY.md",
            "requirements.txt"
        ]
        
        for doc_file in docs:
            full_path = self.base_path / doc_file
            self.check(full_path.exists(), f"Documentation exists: {doc_file}")
    
    def verify_ci(self):
        """Verify CI/CD configuration."""
        print("\n" + "="*60)
        print("VERIFYING CI/CD CONFIGURATION")
        print("="*60)
        
        ci_file = self.base_path / ".github/workflows/evaluation.yml"
        self.check(ci_file.exists(), "CI workflow exists: .github/workflows/evaluation.yml")
        
        if ci_file.exists():
            with open(ci_file, 'r') as f:
                content = f.read()
                self.check("hard-evaluations" in content, "CI includes hard evaluations job")
                self.check("llm-evaluations" in content, "CI includes LLM evaluations job")
    
    def verify_dependencies(self):
        """Verify Python dependencies."""
        print("\n" + "="*60)
        print("VERIFYING DEPENDENCIES")
        print("="*60)
        
        req_file = self.base_path / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                content = f.read()
                required_packages = ["pyyaml", "openai"]
                for package in required_packages:
                    self.check(package.lower() in content.lower(), 
                             f"Requirements include: {package}", is_error=False)
    
    def run_all_checks(self):
        """Run all verification checks."""
        print("\n" + "="*60)
        print("EVALUATION FRAMEWORK VERIFICATION")
        print("="*60)
        
        self.verify_structure()
        self.verify_config_files()
        self.verify_test_files()
        self.verify_runners()
        self.verify_prompts()
        self.verify_rubrics()
        self.verify_documentation()
        self.verify_ci()
        self.verify_dependencies()
        
        # Summary
        print("\n" + "="*60)
        print("VERIFICATION SUMMARY")
        print("="*60)
        print(f"\nTotal Checks: {self.total_checks}")
        print(f"Passed: {self.checks_passed}")
        print(f"Failed: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        
        if self.errors:
            print("\n" + "="*60)
            print("ERRORS FOUND")
            print("="*60)
            for error in self.errors:
                print(f"  ✗ {error}")
        
        if self.warnings:
            print("\n" + "="*60)
            print("WARNINGS")
            print("="*60)
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        success_rate = (self.checks_passed / self.total_checks * 100) if self.total_checks > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if len(self.errors) == 0:
            print("\n✓ Framework verification PASSED!")
            return True
        else:
            print("\n✗ Framework verification FAILED - fix errors above")
            return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify evaluation framework setup")
    parser.add_argument("--path", type=str, default=".", help="Base path to project")
    
    args = parser.parse_args()
    
    verifier = EvaluationFrameworkVerifier(args.path)
    success = verifier.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
