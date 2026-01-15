#!/usr/bin/env python3
"""
Human Evaluation Merge Script
Merges human evaluation results from CSV/JSON annotations into aggregated reports.
"""

import json
import csv
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import yaml

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class HumanEvalMerger:
    def __init__(self, config_path: str = "evaluation/configs/eval_config.yaml"):
        """Initialize the human evaluation merger."""
        self.config = self._load_config(config_path)
        self.output_dir = Path(self.config["global"]["output_dir"])
        self.jsonl_dir = Path(self.config["global"]["jsonl_dir"])
        self.jsonl_dir.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load evaluation configuration."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_human_evaluations(self, agent_name: str) -> List[Dict]:
        """Load human evaluation results for an agent."""
        agent_config = self.config["agents"][agent_name]
        
        if not agent_config.get("human_tests"):
            return []
        
        # Look for evaluation results file
        # Expected format: CSV or JSON with columns: test_id, usefulness, trustworthiness, reasoning_quality, decision_confidence, notes
        eval_file = self.output_dir / f"{agent_name}_human_evals.csv"
        
        if not eval_file.exists():
            # Try JSON format
            eval_file = self.output_dir / f"{agent_name}_human_evals.json"
            if not eval_file.exists():
                print(f"Warning: Human evaluation file not found for {agent_name}")
                return []
        
        results = []
        
        if eval_file.suffix == ".csv":
            with open(eval_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    result = {
                        "test_id": row.get("test_id", ""),
                        "usefulness": float(row.get("usefulness", 0)),
                        "trustworthiness": float(row.get("trustworthiness", 0)),
                        "reasoning_quality": float(row.get("reasoning_quality", 0)),
                        "decision_confidence": float(row.get("decision_confidence", 0)),
                        "notes": row.get("notes", ""),
                        "evaluator": row.get("evaluator", "unknown")
                    }
                    results.append(result)
        else:
            with open(eval_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    results = data
                else:
                    results = [data]
        
        return results
    
    def _calculate_scores(self, results: List[Dict], agent_config: Dict) -> Dict:
        """Calculate aggregated scores from human evaluations."""
        if not results:
            return {
                "total_evaluations": 0,
                "average_scores": {},
                "pass_rate": 0.0,
                "meets_threshold": False
            }
        
        dimensions = agent_config["human_tests"]["dimensions"]
        min_score = agent_config["human_tests"]["min_score_per_dimension"]
        
        # Calculate averages
        avg_scores = {}
        for dimension in dimensions:
            scores = [r.get(dimension, 0.0) for r in results if r.get(dimension) is not None]
            avg_scores[dimension] = sum(scores) / len(scores) if scores else 0.0
        
        # Calculate overall average
        all_scores = [score for scores in [avg_scores.values()] for score in scores]
        avg_scores["overall"] = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Count passes (all dimensions >= min_score)
        passed = sum(
            1 for r in results
            if all(r.get(dim, 0.0) >= min_score for dim in dimensions)
        )
        pass_rate = passed / len(results) if results else 0.0
        
        threshold = agent_config["human_tests"]["pass_threshold"]
        meets_threshold = pass_rate >= threshold
        
        return {
            "total_evaluations": len(results),
            "average_scores": avg_scores,
            "pass_rate": pass_rate,
            "threshold": threshold,
            "meets_threshold": meets_threshold,
            "passed": passed,
            "failed": len(results) - passed
        }
    
    def _generate_template(self, agent_name: str) -> str:
        """Generate a template CSV file for human evaluators."""
        agent_config = self.config["agents"][agent_name]
        
        if not agent_config.get("human_tests"):
            return ""
        
        test_file = agent_config["human_tests"]["file"]
        if not os.path.exists(test_file):
            return ""
        
        # Load test cases
        test_cases = []
        with open(test_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_cases.append(row)
        
        # Generate template
        template_file = self.output_dir / f"{agent_name}_human_evals_template.csv"
        
        with open(template_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "test_id", "query", "usefulness", "trustworthiness", 
                "reasoning_quality", "decision_confidence", "notes", "evaluator"
            ])
            
            for test_case in test_cases:
                writer.writerow([
                    test_case.get("id", ""),
                    test_case.get("query", ""),
                    "",  # usefulness (1-5)
                    "",  # trustworthiness (1-5)
                    "",  # reasoning_quality (1-5)
                    "",  # decision_confidence (1-5)
                    "",  # notes
                    ""   # evaluator name
                ])
        
        return str(template_file)
    
    def process_agent(self, agent_name: str) -> Dict:
        """Process human evaluations for a specific agent."""
        agent_config = self.config["agents"][agent_name]
        
        if not agent_config.get("human_tests"):
            return {}
        
        print(f"\nProcessing human evaluations for {agent_config['name']}")
        
        # Load evaluations
        results = self._load_human_evaluations(agent_name)
        
        if not results:
            print(f"  No evaluations found. Generating template...")
            template_file = self._generate_template(agent_name)
            if template_file:
                print(f"  Template generated: {template_file}")
            return {}
        
        # Calculate scores
        scores = self._calculate_scores(results, agent_config)
        
        # Save JSONL results
        jsonl_file = self.jsonl_dir / f"{agent_name}_human_evals.jsonl"
        with open(jsonl_file, 'w') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')
        
        print(f"  Processed {scores['total_evaluations']} evaluations")
        print(f"  Pass Rate: {scores['pass_rate']:.2%}")
        print(f"  Meets Threshold: {'✓' if scores['meets_threshold'] else '✗'}")
        
        return {
            "agent": agent_name,
            "scores": scores,
            "evaluations": results
        }
    
    def process_all_agents(self) -> Dict:
        """Process human evaluations for all agents."""
        all_results = {}
        
        for agent_name in self.config["agents"]:
            result = self.process_agent(agent_name)
            if result:
                all_results[agent_name] = result
        
        return all_results
    
    def generate_report(self, results: Dict[str, Dict]) -> Dict:
        """Generate aggregated report from human evaluation results."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "evaluation_type": "human",
            "agents": {}
        }
        
        for agent_name, agent_result in results.items():
            scores = agent_result["scores"]
            
            report["agents"][agent_name] = {
                "total_evaluations": scores["total_evaluations"],
                "passed": scores["passed"],
                "failed": scores["failed"],
                "pass_rate": scores["pass_rate"],
                "threshold": scores["threshold"],
                "meets_threshold": scores["meets_threshold"],
                "average_scores": scores["average_scores"]
            }
        
        return report


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Merge human evaluation results")
    parser.add_argument("--agent", type=str, help="Process evaluations for specific agent only")
    parser.add_argument("--config", type=str, default="evaluation/configs/eval_config.yaml",
                       help="Path to evaluation config")
    parser.add_argument("--generate-templates", action="store_true",
                       help="Generate template CSV files for human evaluators")
    
    args = parser.parse_args()
    
    merger = HumanEvalMerger(args.config)
    
    if args.generate_templates:
        print("Generating templates for all agents...")
        for agent_name in merger.config["agents"]:
            template_file = merger._generate_template(agent_name)
            if template_file:
                print(f"  Generated: {template_file}")
        return
    
    if args.agent:
        results = {args.agent: merger.process_agent(args.agent)}
    else:
        results = merger.process_all_agents()
    
    # Generate and save report
    report = merger.generate_report(results)
    report_file = merger.output_dir / "human_evals_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*60}")
    print("Human Evaluation Summary")
    print(f"{'='*60}\n")
    
    for agent_name, agent_report in report["agents"].items():
        print(f"{agent_name}:")
        print(f"  Total: {agent_report['total_evaluations']}")
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
