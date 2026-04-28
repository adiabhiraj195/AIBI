#!/usr/bin/env python3
"""
Test Complex CFO-Level Queries for Wind Energy Business Intelligence
"""

import asyncio
import logging
from rag.hybrid_llamaindex_rag import hybrid_rag

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_cfo_queries():
    """Test complex CFO-level business intelligence queries"""
    
    print("🔄 Initializing RAG system for CFO-level analysis...")
    await hybrid_rag.initialize()
    print("✅ RAG system initialized")
    
    # Complex CFO-level queries based on available data
    cfo_queries = [
        # Financial Performance & Risk Analysis
        {
            "category": "Financial Performance",
            "query": "What is our total portfolio capacity and how does it break down by business module?",
            "business_context": "Portfolio diversification and revenue potential analysis"
        },
        {
            "category": "Budget Variance Analysis", 
            "query": "Show me the plan vs actual capacity deviations across all projects",
            "business_context": "Budget control and forecasting accuracy"
        },
        {
            "category": "Customer Concentration Risk",
            "query": "What percentage of our total capacity is concentrated in our top 5 customers?",
            "business_context": "Customer concentration risk assessment"
        },
        {
            "category": "Geographic Risk Analysis",
            "query": "Which states contribute the most to our revenue and what's our geographic diversification?",
            "business_context": "Geographic risk and market penetration analysis"
        },
        {
            "category": "Project Pipeline Analysis",
            "query": "How many projects are in each phase and what's the total capacity in our pipeline?",
            "business_context": "Revenue pipeline and cash flow forecasting"
        },
        {
            "category": "Technology Mix Analysis",
            "query": "What's our WTG model distribution and capacity by turbine type?",
            "business_context": "Technology risk and operational efficiency"
        },
        {
            "category": "Fiscal Performance",
            "query": "Compare our capacity additions between FY2425 and FY2526",
            "business_context": "Year-over-year growth analysis"
        },
        {
            "category": "Operational Efficiency",
            "query": "What's the average project size and how does it vary by business module?",
            "business_context": "Operational scale and efficiency metrics"
        },
        {
            "category": "Deviation Analysis",
            "query": "Which customers or states show the highest variance between planned and actual capacity?",
            "business_context": "Execution risk and customer reliability assessment"
        },
        {
            "category": "Business Unit Performance",
            "query": "Rank our business modules by total capacity and customer count",
            "business_context": "Business unit performance and resource allocation"
        },
        {
            "category": "Market Share Analysis",
            "query": "What's our market position in terms of total WTG count and generation capacity?",
            "business_context": "Market share and competitive positioning"
        },
        {
            "category": "Project Economics",
            "query": "What's the capacity utilization efficiency across different WTG models?",
            "business_context": "Asset utilization and technology ROI"
        }
    ]
    
    print(f"\n🎯 Testing {len(cfo_queries)} CFO-Level Business Intelligence Queries")
    print("=" * 80)
    
    successful_queries = 0
    
    for i, query_info in enumerate(cfo_queries, 1):
        print(f"\n{'='*80}")
        print(f"CFO Query {i}: {query_info['category']}")
        print(f"Business Context: {query_info['business_context']}")
        print(f"Query: {query_info['query']}")
        print('='*80)
        
        try:
            result = await asyncio.wait_for(hybrid_rag.query(query_info['query']), timeout=45.0)
            
            print(f"✅ Query successful")
            print(f"Answer: {result['answer']}")
            print(f"Source Count: {result.get('source_count', 0)}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Has Sufficient Data: {result['has_sufficient_data']}")
            
            if 'query_type' in result:
                print(f"Query Type: {result['query_type']}")
            
            if 'statistical_data' in result:
                print("Statistical Analysis: Available")
                # Show key metrics if available
                stats = result['statistical_data']
                if 'total_capacity' in stats:
                    print(f"  Total Capacity: {stats['total_capacity']:.2f} MW")
                if 'customer_breakdown' in stats:
                    print(f"  Top Customers: {len(stats['customer_breakdown'])}")
                if 'state_breakdown' in stats:
                    print(f"  States Covered: {len(stats['state_breakdown'])}")
            
            successful_queries += 1
            
        except asyncio.TimeoutError:
            print(f"⏰ Query timed out after 45 seconds")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            logger.error(f"CFO query failed for '{query_info['query']}': {e}")
    
    print(f"\n{'='*80}")
    print(f"📊 CFO Query Results Summary")
    print(f"✅ Successful Queries: {successful_queries}/{len(cfo_queries)}")
    print(f"🎯 Success Rate: {(successful_queries/len(cfo_queries))*100:.1f}%")
    print("=" * 80)
    
    if successful_queries == len(cfo_queries):
        print("🎉 All CFO-level queries executed successfully!")
        print("💼 Your RAG system is ready for executive-level business intelligence!")
    else:
        print("⚠️  Some queries may need additional pattern recognition or handlers")

if __name__ == "__main__":
    asyncio.run(test_cfo_queries())