#!/usr/bin/env python3
"""
Master Evaluation Runner
Runs all evaluation types (hard, LLM, human) and generates comprehensive reports.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import yaml
import subprocess

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import runners - adjust path based on your project structure
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from run_hard_evals import HardEvalRunner
    from run_llm_evals import LLMEvalRunner
    from run_human_eval_merge import HumanEvalMerger
    from run_retrieval_evals import RetrievalEvalRunner
    from run_system_tests import SystemTestRunner
except ImportError:
    # Fallback: import directly
    import importlib.util
    spec = importlib.util.spec_from_file_location("run_hard_evals", current_dir / "run_hard_evals.py")
    hard_evals_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hard_evals_module)
    HardEvalRunner = hard_evals_module.HardEvalRunner
    
    spec = importlib.util.spec_from_file_location("run_llm_evals", current_dir / "run_llm_evals.py")
    llm_evals_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(llm_evals_module)
    LLMEvalRunner = llm_evals_module.LLMEvalRunner
    
    spec = importlib.util.spec_from_file_location("run_human_eval_merge", current_dir / "run_human_eval_merge.py")
    human_evals_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(human_evals_module)
    HumanEvalMerger = human_evals_module.HumanEvalMerger
    
    spec = importlib.util.spec_from_file_location("run_retrieval_evals", current_dir / "run_retrieval_evals.py")
    retrieval_evals_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(retrieval_evals_module)
    RetrievalEvalRunner = retrieval_evals_module.RetrievalEvalRunner
    
    spec = importlib.util.spec_from_file_location("run_system_tests", current_dir / "run_system_tests.py")
    system_tests_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(system_tests_module)
    SystemTestRunner = system_tests_module.SystemTestRunner


class MasterEvalRunner:
    def __init__(self, config_path: str = "evaluation/configs/eval_config.yaml"):
        """Initialize the master evaluation runner."""
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self.output_dir = Path(self.config["global"]["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: str) -> dict:
        """Load evaluation configuration."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def run_hard_evals(self, agent: str = None) -> dict:
        """Run hard evaluations."""
        print("\n" + "="*60)
        print("RUNNING HARD EVALUATIONS")
        print("="*60)
        
        runner = HardEvalRunner(self.config_path)
        
        if agent:
            results = {agent: runner.run_tests_for_agent(agent)}
        else:
            results = runner.run_all_tests()
        
        report = runner.generate_report(results)
        
        # Save report
        report_file = self.output_dir / "hard_evals_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_llm_evals(self, agent: str = None, sample_size: int = None) -> dict:
        """Run LLM evaluations."""
        print("\n" + "="*60)
        print("RUNNING LLM EVALUATIONS")
        print("="*60)
        
        runner = LLMEvalRunner(self.config_path)
        
        if agent:
            results = {agent: runner.run_tests_for_agent(agent, sample_size)}
        else:
            results = runner.run_all_tests(sample_size)
        
        report = runner.generate_report(results)
        
        # Save report
        report_file = self.output_dir / "llm_evals_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_system_tests(self) -> dict:
        """Run system-level tests."""
        print("\n" + "="*60)
        print("RUNNING SYSTEM-LEVEL TESTS")
        print("="*60)
        
        runner = SystemTestRunner(self.config_path)
        results = runner.run_all_system_tests()
        report = runner.generate_report(results)
        
        # Save report
        report_file = self.output_dir / "system_tests_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_retrieval_evals(self, agent: str = None) -> dict:
        """Run retrieval evaluations."""
        print("\n" + "="*60)
        print("RUNNING RETRIEVAL EVALUATIONS")
        print("="*60)
        
        runner = RetrievalEvalRunner(self.config_path)
        
        if agent:
            results = {agent: runner.run_tests_for_agent(agent)}
        else:
            results = runner.run_all_tests()
        
        report = runner.generate_report(results)
        
        # Save report
        report_file = self.output_dir / "retrieval_evals_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_human_evals(self, agent: str = None) -> dict:
        """Process human evaluations."""
        print("\n" + "="*60)
        print("PROCESSING HUMAN EVALUATIONS")
        print("="*60)
        
        merger = HumanEvalMerger(self.config_path)
        
        if agent:
            results = {agent: merger.process_agent(agent)}
        else:
            results = merger.process_all_agents()
        
        report = merger.generate_report(results)
        
        # Save report
        report_file = self.output_dir / "human_evals_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def generate_markdown_report(self, hard_report: dict, retrieval_report: dict, llm_report: dict, human_report: dict, system_report: dict) -> str:
        """Generate comprehensive Markdown report."""
        template_path = Path(self.config["reporting"]["markdown_template"])
        
        if template_path.exists():
            with open(template_path, 'r') as f:
                template = f.read()
        else:
            template = self._default_template()
        
        # Generate report content
        report_lines = []
        report_lines.append("# Financial Analysis Multi-Agent System - Evaluation Report\n")
        report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("---\n")
        
        # Summary section
        report_lines.append("## Executive Summary\n")
        report_lines.append("### Overall Results\n")
        report_lines.append("| Agent | Hard Evals | Retrieval Evals | LLM Evals | Human Evals | Overall Status |\n")
        report_lines.append("|-------|------------|-----------------|-----------|-------------|----------------|\n")
        
        all_agents = set()
        if hard_report.get("agents"):
            all_agents.update(hard_report["agents"].keys())
        if llm_report.get("agents"):
            all_agents.update(llm_report["agents"].keys())
        if human_report.get("agents"):
            all_agents.update(human_report["agents"].keys())
        
        for agent_name in sorted(all_agents):
            hard_status = "N/A"
            retrieval_status = "N/A"
            llm_status = "N/A"
            human_status = "N/A"
            
            if agent_name in hard_report.get("agents", {}):
                hard_agent = hard_report["agents"][agent_name]
                hard_status = f"{hard_agent['pass_rate']:.1%} ({'✓' if hard_agent['meets_threshold'] else '✗'})"
            
            if agent_name in retrieval_report.get("agents", {}):
                retrieval_agent = retrieval_report["agents"][agent_name]
                retrieval_status = f"{retrieval_agent['pass_rate']:.1%} ({'✓' if retrieval_agent['meets_threshold'] else '✗'})"
            
            if agent_name in llm_report.get("agents", {}):
                llm_agent = llm_report["agents"][agent_name]
                llm_status = f"{llm_agent['pass_rate']:.1%} ({'✓' if llm_agent['meets_threshold'] else '✗'})"
            
            if agent_name in human_report.get("agents", {}):
                human_agent = human_report["agents"][agent_name]
                human_status = f"{human_agent['pass_rate']:.1%} ({'✓' if human_agent['meets_threshold'] else '✗'})"
            
            # Determine overall status
            all_pass = True
            if agent_name in hard_report.get("agents", {}):
                all_pass = all_pass and hard_report["agents"][agent_name]["meets_threshold"]
            if agent_name in retrieval_report.get("agents", {}):
                all_pass = all_pass and retrieval_report["agents"][agent_name]["meets_threshold"]
            if agent_name in llm_report.get("agents", {}):
                all_pass = all_pass and llm_report["agents"][agent_name]["meets_threshold"]
            if agent_name in human_report.get("agents", {}):
                all_pass = all_pass and human_report["agents"][agent_name]["meets_threshold"]
            
            overall_status = "✓ PASS" if all_pass else "✗ FAIL"
            
            report_lines.append(f"| {agent_name} | {hard_status} | {retrieval_status} | {llm_status} | {human_status} | {overall_status} |\n")
        
        # Detailed sections
        report_lines.append("\n## Detailed Results\n")
        
        # Retrieval evaluations
        report_lines.append("### Retrieval Evaluations (RAG/Evidence-based)\n")
        if retrieval_report.get("agents"):
            for agent_name, agent_data in retrieval_report["agents"].items():
                report_lines.append(f"#### {agent_name}\n")
                report_lines.append(f"- **Total Tests:** {agent_data['total_tests']}\n")
                report_lines.append(f"- **Passed:** {agent_data['passed']}\n")
                report_lines.append(f"- **Failed:** {agent_data['failed']}\n")
                report_lines.append(f"- **Pass Rate:** {agent_data['pass_rate']:.2%}\n")
                report_lines.append(f"- **Threshold:** {agent_data['threshold']:.2%}\n")
                report_lines.append(f"- **Status:** {'✓ PASS' if agent_data['meets_threshold'] else '✗ FAIL'}\n")
                if agent_data.get("check_failures"):
                    report_lines.append("\n**Check Failures:**\n")
                    for check_name, check_stats in agent_data["check_failures"].items():
                        report_lines.append(f"- {check_name}: {check_stats['passed']} passed, {check_stats['failed']} failed\n")
                report_lines.append("\n")
        
        # Hard evaluations
        report_lines.append("### Hard Evaluations\n")
        if hard_report.get("agents"):
            for agent_name, agent_data in hard_report["agents"].items():
                report_lines.append(f"#### {agent_name}\n")
                report_lines.append(f"- **Total Tests:** {agent_data['total_tests']}\n")
                report_lines.append(f"- **Passed:** {agent_data['passed']}\n")
                report_lines.append(f"- **Failed:** {agent_data['failed']}\n")
                report_lines.append(f"- **Pass Rate:** {agent_data['pass_rate']:.2%}\n")
                report_lines.append(f"- **Threshold:** {agent_data['threshold']:.2%}\n")
                report_lines.append(f"- **Status:** {'✓ PASS' if agent_data['meets_threshold'] else '✗ FAIL'}\n")
                
                if agent_data.get("failures"):
                    report_lines.append("\n**Failures:**\n")
                    for failure in agent_data["failures"][:5]:  # Show first 5
                        report_lines.append(f"- {failure['test_id']}: {failure['test_name']}\n")
                        for error in failure.get("errors", [])[:2]:  # Show first 2 errors
                            report_lines.append(f"  - {error}\n")
                report_lines.append("\n")
        
        # LLM evaluations
        report_lines.append("### LLM Evaluations\n")
        if llm_report.get("agents"):
            for agent_name, agent_data in llm_report["agents"].items():
                report_lines.append(f"#### {agent_name}\n")
                report_lines.append(f"- **Total Tests:** {agent_data['total_tests']}\n")
                report_lines.append(f"- **Passed:** {agent_data['passed']}\n")
                report_lines.append(f"- **Failed:** {agent_data['failed']}\n")
                report_lines.append(f"- **Pass Rate:** {agent_data['pass_rate']:.2%}\n")
                report_lines.append(f"- **Threshold:** {agent_data['threshold']:.2%}\n")
                report_lines.append(f"- **Status:** {'✓ PASS' if agent_data['meets_threshold'] else '✗ FAIL'}\n")
                
                if agent_data.get("average_scores"):
                    report_lines.append("\n**Average Scores:**\n")
                    for dim, score in agent_data["average_scores"].items():
                        report_lines.append(f"- {dim}: {score:.2f}/5.0\n")
                report_lines.append("\n")
        
        # Human evaluations
        report_lines.append("### Human Evaluations\n")
        if human_report.get("agents"):
            for agent_name, agent_data in human_report["agents"].items():
                report_lines.append(f"#### {agent_name}\n")
                report_lines.append(f"- **Total Evaluations:** {agent_data['total_evaluations']}\n")
                report_lines.append(f"- **Passed:** {agent_data['passed']}\n")
                report_lines.append(f"- **Failed:** {agent_data['failed']}\n")
                report_lines.append(f"- **Pass Rate:** {agent_data['pass_rate']:.2%}\n")
                report_lines.append(f"- **Threshold:** {agent_data['threshold']:.2%}\n")
                report_lines.append(f"- **Status:** {'✓ PASS' if agent_data['meets_threshold'] else '✗ FAIL'}\n")
                
                if agent_data.get("average_scores"):
                    report_lines.append("\n**Average Scores:**\n")
                    for dim, score in agent_data["average_scores"].items():
                        report_lines.append(f"- {dim}: {score:.2f}/5.0\n")
                report_lines.append("\n")
        
        # Failure patterns
        report_lines.append("## Failure Patterns\n")
        report_lines.append("### Common Issues\n")
        # TODO: Analyze failures and identify patterns
        report_lines.append("- Analysis of failure patterns would go here\n")
        
        # Strengths and weaknesses
        report_lines.append("## Strengths & Weaknesses\n")
        report_lines.append("### Strengths\n")
        report_lines.append("- Analysis of strengths would go here\n")
        report_lines.append("\n### Weaknesses\n")
        report_lines.append("- Analysis of weaknesses would go here\n")
        
        return "".join(report_lines)
    
    def _default_template(self) -> str:
        """Return default template if custom template not found."""
        return ""
    
    def run_all(self, agent: str = None, llm_sample_size: int = None, skip_human: bool = False):
        """Run all evaluation types."""
        print("\n" + "="*60)
        print("MASTER EVALUATION RUNNER")
        print("="*60)
        
        # Run hard evals
        hard_report = self.run_hard_evals(agent)
        
        # Run retrieval evals
        retrieval_report = {"agents": {}}
        try:
            retrieval_report = self.run_retrieval_evals(agent)
        except Exception as e:
            print(f"Warning: Could not run retrieval evaluations: {e}")
        
        # Run system tests
        system_report = {"test_types": {}}
        try:
            system_report = self.run_system_tests()
        except Exception as e:
            print(f"Warning: Could not run system tests: {e}")
        
        # Run LLM evals
        llm_report = self.run_llm_evals(agent, llm_sample_size)
        
        # Process human evals (if available)
        human_report = {"agents": {}}
        if not skip_human:
            try:
                human_report = self.run_human_evals(agent)
            except Exception as e:
                print(f"Warning: Could not process human evaluations: {e}")
        
        # Generate Markdown report
        markdown_report = self.generate_markdown_report(hard_report, retrieval_report, llm_report, human_report, system_report)
        report_file = self.output_dir / "evaluation_report.md"
        with open(report_file, 'w') as f:
            f.write(markdown_report)
        
        print(f"\n{'='*60}")
        print("EVALUATION COMPLETE")
        print(f"{'='*60}")
        print(f"\nReports saved to: {self.output_dir}")
        print(f"  - Hard evals: {self.output_dir / 'hard_evals_report.json'}")
        print(f"  - Retrieval evals: {self.output_dir / 'retrieval_evals_report.json'}")
        print(f"  - LLM evals: {self.output_dir / 'llm_evals_report.json'}")
        print(f"  - Human evals: {self.output_dir / 'human_evals_report.json'}")
        print(f"  - Markdown report: {report_file}")
        
        # Determine overall success
        all_pass = True
        for agent_name in hard_report.get("agents", {}):
            if not hard_report["agents"][agent_name]["meets_threshold"]:
                all_pass = False
        for agent_name in retrieval_report.get("agents", {}):
            if not retrieval_report["agents"][agent_name]["meets_threshold"]:
                all_pass = False
        for agent_name in llm_report.get("agents", {}):
            if not llm_report["agents"][agent_name]["meets_threshold"]:
                all_pass = False
        for agent_name in human_report.get("agents", {}):
            if not human_report["agents"][agent_name]["meets_threshold"]:
                all_pass = False
        
        if not all_pass:
            print("\n⚠️  Some evaluations did not meet thresholds!")
            sys.exit(1)
        else:
            print("\n✓ All evaluations passed!")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run all evaluations")
    parser.add_argument("--agent", type=str, help="Run tests for specific agent only")
    parser.add_argument("--config", type=str, default="evaluation/configs/eval_config.yaml",
                       help="Path to evaluation config")
    parser.add_argument("--llm-sample-size", type=int, help="Sample size for LLM evals (for CI)")
    parser.add_argument("--skip-human", action="store_true", help="Skip human evaluations")
    
    args = parser.parse_args()
    
    runner = MasterEvalRunner(args.config)
    runner.run_all(args.agent, args.llm_sample_size, args.skip_human)


if __name__ == "__main__":
    main()
