#!/usr/bin/env python3
"""
Test new query types with the enhanced RAG system
"""

import asyncio
import logging
from rag.hybrid_llamaindex_rag import hybrid_rag

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_new_query_types():
    """Test the new comprehensive query types"""
    
    print("🔄 Initializing RAG system...")
    await hybrid_rag.initialize()
    print("✅ RAG system initialized")
    
    # Test new query types
    test_queries = [
        "what is the total WTG count?",
        "show me MWG analysis by customer",
        "WTG deviation analysis",
        "breakdown by project phase",
        "analysis by fiscal year",
        "plan vs actual capacity",
        "average capacity per customer",
        "what is the minimum capacity project?",
        "how many projects do we have?",
        "compare different WTG models"
    ]
    
    for i, question in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {question}")
        print('='*60)
        
        try:
            result = await asyncio.wait_for(hybrid_rag.query(question), timeout=30.0)
            
            print(f"✅ Query successful")
            print(f"Question: {question}")
            print(f"Answer: {result['answer']}")
            print(f"Source Count: {result.get('source_count', 0)}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Has Data: {result['has_sufficient_data']}")
            
            if 'query_type' in result:
                print(f"Query Type: {result['query_type']}")
            
            if 'statistical_data' in result:
                print("Statistical Data Available: Yes")
                
        except asyncio.TimeoutError:
            print(f"⏰ Query timed out after 30 seconds")
        except Exception as e:
            print(f"❌ Query failed: {e}")
            logger.error(f"Query failed for '{question}': {e}")

if __name__ == "__main__":
    asyncio.run(test_new_query_types())