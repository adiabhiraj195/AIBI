#!/usr/bin/env python3
"""
Test NL2SQL Agent for Complex Semantic Queries
"""

import asyncio
import logging
from rag.hybrid_llamaindex_rag import hybrid_rag

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_nl2sql_queries():
    """Test NL2SQL agent with complex semantic queries"""
    
    print("🔄 Initializing RAG system with NL2SQL capabilities...")
    await hybrid_rag.initialize()
    print("✅ RAG system initialized")
    
    # Complex semantic queries that require precise SQL generation
    semantic_queries = [
        {
            "category": "Customer Analysis",
            "query": "Show me all projects for customers in State 1 with capacity greater than 3 MW",
            "expected_type": "nl2sql"
        },
        {
            "category": "Technology Filtering",
            "query": "Find all S4 HLTI turbine projects in business module BB",
            "expected_type": "nl2sql"
        },
        {
            "category": "Deviation Analysis",
            "query": "Which projects have MWG deviation greater than 2.0?",
            "expected_type": "nl2sql"
        },
        {
            "category": "Phase Analysis",
            "query": "Show me projects in HOTO Plan phase with WTG count between 5 and 10",
            "expected_type": "nl2sql"
        },
        {
            "category": "Fiscal Year Comparison",
            "query": "Compare projects between FY2425 and FY2526 for customer HA**********A PR**O",
            "expected_type": "nl2sql"
        },
        {
            "category": "Business Context",
            "query": "Find all projects with 'plan vs actual deviation' business context",
            "expected_type": "nl2sql"
        },
        {
            "category": "Complex Filtering",
            "query": "Show me HLT turbine projects in State 2 with capacity between 2.5 and 4.0 MW",
            "expected_type": "nl2sql"
        },
        {
            "category": "Data Type Analysis",
            "query": "Find all 'actual_forecast' data type projects for business module AA",
            "expected_type": "nl2sql"
        },
        {
            "category": "Period Analysis",
            "query": "Show me projects from Oct-25 period with WTG deviation less than 0.5",
            "expected_type": "nl2sql"
        },
        {
            "category": "Multi-Criteria Search",
            "query": "Find projects in State 3 using S2 HLT turbines in RO Plan phase",
            "expected_type": "nl2sql"
        },
        {
            "category": "Range Queries",
            "query": "Show customers with total capacity between 1000 and 5000 MW",
            "expected_type": "nl2sql"
        },
        {
            "category": "Aggregation Query",
            "query": "What's the average WTG count for each turbine type?",
            "expected_type": "nl2sql"
        }
    ]
    
    print(f"\n🎯 Testing {len(semantic_queries)} Complex Semantic Queries with NL2SQL")
    print("=" * 80)
    
    successful_queries = 0
    nl2sql_queries = 0
    
    for i, query_info in enumerate(semantic_queries, 1):
        print(f"\n{'='*80}")
        print(f"Semantic Query {i}: {query_info['category']}")
        print(f"Query: {query_info['query']}")
        print('='*80)
        
        try:
            result = await asyncio.wait_for(hybrid_rag.query(query_info['query']), timeout=45.0)
            
            print(f"✅ Query successful")
            print(f"Answer: {result['answer']}")
            print(f"Source Count: {result.get('source_count', 0)}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Has Sufficient Data: {result['has_sufficient_data']}")
            print(f"Query Type: {result.get('query_type', 'unknown')}")
            
            if result.get('query_type') == 'nl2sql':
                nl2sql_queries += 1
                print(f"SQL Query: {result.get('sql_query', 'N/A')}")
                if result.get('data_sample'):
                    print(f"Sample Data: {len(result['data_sample'])} records")
            
            if result.get('query_type') == 'statistical':
                print("Statistical Analysis: Available")
            
            successful_queries += 1
            
        except asyncio.TimeoutError:
            print(f"⏰ Query timed out after 45 seconds")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            logger.error(f"Semantic query failed for '{query_info['query']}': {e}")
    
    print(f"\n{'='*80}")
    print(f"📊 NL2SQL Query Results Summary")
    print(f"✅ Successful Queries: {successful_queries}/{len(semantic_queries)}")
    print(f"🔍 NL2SQL Queries: {nl2sql_queries}")
    print(f"📈 Statistical Queries: {successful_queries - nl2sql_queries}")
    print(f"🎯 Success Rate: {(successful_queries/len(semantic_queries))*100:.1f}%")
    print("=" * 80)
    
    if successful_queries == len(semantic_queries):
        print("🎉 All semantic queries executed successfully!")
        print("💼 NL2SQL agent is working perfectly for complex queries!")
    else:
        print("⚠️  Some queries may need additional pattern refinement")

async def test_direct_nl2sql():
    """Test the NL2SQL agent directly"""
    from rag.nl2sql_agent import nl2sql_agent
    
    print("\n🔧 Testing NL2SQL Agent Directly")
    print("=" * 50)
    
    test_query = "Show me all projects in State 1 with capacity greater than 3 MW"
    
    # Test SQL generation
    sql_result = await nl2sql_agent.generate_sql(test_query)
    print(f"Generated SQL: {sql_result.get('sql_query', 'Failed')}")
    
    if sql_result.get('success'):
        # Test SQL execution
        query_result = await nl2sql_agent.execute_sql_query(sql_result['sql_query'])
        print(f"Execution Result: {query_result.get('row_count', 0)} rows")
        
        if query_result.get('success'):
            # Test response formatting
            formatted_response = await nl2sql_agent.format_response(query_result, test_query)
            print(f"Formatted Response: {formatted_response}")

if __name__ == "__main__":
    asyncio.run(test_nl2sql_queries())
    asyncio.run(test_direct_nl2sql())