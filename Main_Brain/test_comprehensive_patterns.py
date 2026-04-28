#!/usr/bin/env python3
"""
Test comprehensive pattern matching for statistical queries
"""

import asyncio
from rag.statistical_queries import statistical_handler

async def test_all_patterns():
    """Test all the new comprehensive patterns"""
    
    test_queries = [
        # Original queries
        ("give me the total customer count?", "total_customers"),
        ("which customer has the highest capacity?", "highest_capacity"),
        ("what is the total capacity across all projects?", "total_capacity"),
        ("show me the top 5 customers by capacity", "customer_capacity"),
        ("which states have the most wind projects?", "state_analysis"),
        
        # WTG Analysis
        ("what is the total WTG count?", "wtg_analysis"),
        ("show me turbine count by model", "wtg_analysis"),
        ("how many turbines do we have?", "wtg_analysis"),
        ("WTG breakdown by type", "wtg_analysis"),
        ("which WTG models are most common?", "wtg_analysis"),
        ("HLT vs LLT turbine analysis", "wtg_analysis"),
        
        # MWG Analysis
        ("total MWG analysis", "mwg_analysis"),
        ("MWG breakdown by customer", "mwg_analysis"),
        ("average MWG per project", "mwg_analysis"),
        
        # Deviation Analysis
        ("show me WTG deviation analysis", "deviation_analysis"),
        ("what is the variance in MWG?", "deviation_analysis"),
        ("gap analysis between plan and actual", "deviation_analysis"),
        
        # Project Phase Analysis
        ("breakdown by project phase", "project_phase_analysis"),
        ("how many projects are in RO plan phase?", "project_phase_analysis"),
        ("phase wise capacity distribution", "project_phase_analysis"),
        
        # Fiscal Year Analysis
        ("analysis by fiscal year", "fiscal_year_analysis"),
        ("FY wise project breakdown", "fiscal_year_analysis"),
        ("trend over time for capacity", "fiscal_year_analysis"),
        ("projects in fiscal year 2024", "fiscal_year_analysis"),
        
        # Data Type Analysis
        ("plan vs actual capacity", "data_type_analysis"),
        ("budgeted vs actual analysis", "data_type_analysis"),
        ("forecast vs actual comparison", "data_type_analysis"),
        
        # Average Queries
        ("average capacity per customer", "average_queries"),
        ("what is the mean project size?", "average_queries"),
        ("average WTG count per project", "average_queries"),
        
        # Min/Max Queries
        ("what is the minimum capacity project?", "min_max_queries"),
        ("smallest project in our portfolio", "min_max_queries"),
        ("lowest WTG count project", "min_max_queries"),
        
        # Count Queries
        ("how many projects do we have?", "count_queries"),
        ("total number of projects", "count_queries"),
        ("project count by state", "count_queries"),
        
        # Ranking Queries
        ("top 10 customers by WTG count", "ranking_queries"),
        ("bottom 5 states by capacity", "ranking_queries"),
        ("lowest performing customers", "ranking_queries"),
        
        # Comparison Queries
        ("compare different WTG models", "comparison_queries"),
        ("difference between HLT vs LLT", "comparison_queries"),
        ("State 1 vs State 2 comparison", "comparison_queries"),
        
        # Filter Queries
        ("show me data for specific customer ABC", "filter_queries"),
        ("only HLT turbine projects", "filter_queries"),
        ("filter by business module", "filter_queries"),
    ]
    
    print("🔍 Testing Comprehensive Pattern Matching")
    print("=" * 60)
    
    correct_matches = 0
    total_tests = len(test_queries)
    
    for query, expected_type in test_queries:
        classified_type = statistical_handler.classify_query(query)
        
        if classified_type == expected_type:
            status = "✅"
            correct_matches += 1
        else:
            status = "❌"
        
        print(f"{status} Query: '{query}'")
        print(f"   Expected: {expected_type}")
        print(f"   Got: {classified_type}")
        print()
    
    print("=" * 60)
    print(f"📊 Results: {correct_matches}/{total_tests} patterns matched correctly")
    print(f"🎯 Accuracy: {(correct_matches/total_tests)*100:.1f}%")
    
    if correct_matches == total_tests:
        print("🎉 All patterns working perfectly!")
    else:
        print("⚠️  Some patterns need adjustment")

if __name__ == "__main__":
    asyncio.run(test_all_patterns())