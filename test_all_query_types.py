#!/usr/bin/env python3
"""
Test all query types to ensure the system handles them correctly.
"""

import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from app.orchestrator import Orchestrator
import json
import time

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_query(query, query_type):
    """Test a single query."""
    print(f"\n🔍 Query Type: {query_type}")
    print(f"📝 Query: {query}")
    print("-" * 70)
    
    orchestrator = Orchestrator()
    
    start_time = time.time()
    try:
        result = orchestrator.run(query)
        elapsed = time.time() - start_time
        
        print(f"✅ Success! (took {elapsed:.2f}s)")
        print(f"\n📊 Final Answer (first 300 chars):")
        print(result.final_answer[:300] + "..." if len(result.final_answer) > 300 else result.final_answer)
        
        print(f"\n🤖 Agents Used: {len(result.agent_outputs)}")
        for ao in result.agent_outputs:
            print(f"   - {ao.agent}")
        
        print(f"\n📚 Total Sources: {sum(len(ao.sources) for ao in result.agent_outputs)}")
        
        if result.warnings:
            print(f"\n⚠️  Warnings: {len(result.warnings)}")
            for w in result.warnings:
                print(f"   - {w}")
        
        # Check if answer contains actual data (not just placeholder)
        has_data = any(keyword in result.final_answer.lower() for keyword in 
                      ["$", "billion", "million", "%", "revenue", "income", "price", "according"])
        
        if has_data:
            print("\n✅ Answer contains actual data!")
        else:
            print("\n⚠️  Answer may be placeholder - check if data was retrieved")
        
        return True, elapsed
        
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Error after {elapsed:.2f}s: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, elapsed

def main():
    print("\n" + "🚀" * 35)
    print("  Testing All Query Types")
    print("🚀" * 35)
    
    # Test queries for each type
    test_queries = {
        "Broad Query": "Should I invest in AAPL? Consider market data, fundamentals, and risk",
        "Needle Query": "According to the latest earnings report, what was Apple's operating income?",
        "Tabular Query": "Get current price and market cap for AAPL"
    }
    
    results = {}
    
    for query_type, query in test_queries.items():
        print_header(f"Testing {query_type}")
        success, elapsed = test_query(query, query_type)
        results[query_type] = {
            "success": success,
            "elapsed": elapsed,
            "query": query
        }
        
        # Wait a bit between queries
        time.sleep(2)
    
    # Summary
    print_header("Test Summary")
    print("\n📊 Results:")
    for query_type, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"  {status} - {query_type}: {result['elapsed']:.2f}s")
    
    all_passed = all(r["success"] for r in results.values())
    
    if all_passed:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed - check output above")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
