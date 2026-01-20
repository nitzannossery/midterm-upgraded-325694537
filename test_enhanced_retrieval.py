#!/usr/bin/env python3
"""
Test script for enhanced retrieval system with needle-in-haystack and tabular data support.
Tests both broad queries and specific needle queries.
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.orchestrator import Orchestrator
from app.retrieval.retriever import Retriever
import json

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(result):
    """Print formatted result."""
    print(f"\n📋 Mode: {result.mode}")
    print(f"\n📊 Final Answer:")
    print("-" * 70)
    print(result.final_answer)
    print("-" * 70)
    
    if result.agent_outputs:
        print(f"\n🤖 Agent Outputs ({len(result.agent_outputs)}):")
        for i, agent_out in enumerate(result.agent_outputs, 1):
            print(f"\n  {i}. {agent_out.agent}")
            print(f"     Content: {agent_out.content[:200]}...")
            if agent_out.sources:
                print(f"     Sources: {len(agent_out.sources)}")
    
    if result.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"     - {warning}")

def test_retriever():
    """Test the enhanced retriever."""
    print_section("Testing Enhanced Retriever")
    
    retriever = Retriever()
    
    # Test 1: Needle query - specific value
    print("\n🔍 Test 1: Needle Query - Specific Value")
    query1 = "What was Apple's revenue in Q4 2023 according to their earnings report?"
    sources1 = retriever.retrieve(query1, top_k=3)
    print(f"Query: {query1}")
    print(f"Retrieved {len(sources1)} sources:")
    for i, source in enumerate(sources1, 1):
        print(f"  {i}. {source.title}")
        print(f"     Snippet: {source.snippet}")
    
    # Test 2: Tabular data extraction
    print("\n📊 Test 2: Tabular Data Extraction")
    query2 = "Get current price and market cap for AAPL"
    sources2 = retriever.retrieve(query2, top_k=3)
    print(f"Query: {query2}")
    print(f"Retrieved {len(sources2)} sources:")
    for i, source in enumerate(sources2, 1):
        print(f"  {i}. {source.title}")
        if source.snippet:
            print(f"     Snippet: {source.snippet}")
    
    # Test 3: Broad query
    print("\n🌐 Test 3: Broad Query")
    query3 = "Analyze AAPL investment opportunity considering market data, fundamentals, and risk"
    sources3 = retriever.retrieve(query3, top_k=5)
    print(f"Query: {query3}")
    print(f"Retrieved {len(sources3)} sources:")
    for i, source in enumerate(sources3, 1):
        print(f"  {i}. {source.title}")

def test_needle_queries():
    """Test needle-in-haystack queries."""
    print_section("Testing Needle-in-Haystack Queries")
    
    orchestrator = Orchestrator()
    
    needle_queries = [
        "According to the latest earnings report, what was Apple's operating income?",
        "What was Microsoft's revenue in FY2023 according to their annual filing?",
        "What is Apple's gross margin reported in the last quarterly filing?",
        "Get the current price of AAPL",
    ]
    
    for i, query in enumerate(needle_queries, 1):
        print(f"\n{'='*70}")
        print(f"Needle Query {i}: {query}")
        print("="*70)
        
        try:
            result = orchestrator.run(query)
            print(f"\n✅ Success")
            print(f"Answer: {result.final_answer[:300]}...")
            print(f"Sources: {len(result.agent_outputs)} agents + {sum(len(ao.sources) for ao in result.agent_outputs)} total sources")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_broad_queries():
    """Test broad/comprehensive queries."""
    print_section("Testing Broad/Comprehensive Queries")
    
    orchestrator = Orchestrator()
    
    broad_queries = [
        "Should I invest in AAPL? Consider market data, fundamentals, and risk",
        "Analyze AAPL investment opportunity",
        "Provide comprehensive analysis for GOOGL covering all relevant factors",
    ]
    
    for i, query in enumerate(broad_queries, 1):
        print(f"\n{'='*70}")
        print(f"Broad Query {i}: {query}")
        print("="*70)
        
        try:
            result = orchestrator.run(query)
            print(f"\n✅ Success")
            print(f"Answer: {result.final_answer[:300]}...")
            print(f"Agents Used: {len(result.agent_outputs)}")
            if result.warnings:
                print(f"Warnings: {len(result.warnings)}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_tabular_queries():
    """Test tabular data extraction queries."""
    print_section("Testing Tabular Data Extraction Queries")
    
    orchestrator = Orchestrator()
    
    tabular_queries = [
        "Get price data for AAPL from 2024-01-01 to 2024-01-31",
        "What is the historical price and volume for MSFT for the last 90 days?",
        "Get current price, market cap, and P/E ratio for GOOGL",
    ]
    
    for i, query in enumerate(tabular_queries, 1):
        print(f"\n{'='*70}")
        print(f"Tabular Query {i}: {query}")
        print("="*70)
        
        try:
            result = orchestrator.run(query)
            print(f"\n✅ Success")
            print(f"Answer: {result.final_answer[:300]}...")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def main():
    """Run all tests."""
    print("\n" + "🚀" * 35)
    print("  Enhanced Retrieval System - Comprehensive Tests")
    print("🚀" * 35)
    
    # Test retriever directly
    try:
        test_retriever()
    except Exception as e:
        print(f"\n❌ Retriever test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test needle queries
    try:
        test_needle_queries()
    except Exception as e:
        print(f"\n❌ Needle queries test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test broad queries
    try:
        test_broad_queries()
    except Exception as e:
        print(f"\n❌ Broad queries test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test tabular queries
    try:
        test_tabular_queries()
    except Exception as e:
        print(f"\n❌ Tabular queries test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("  Tests Completed!")
    print("="*70)

if __name__ == "__main__":
    main()
