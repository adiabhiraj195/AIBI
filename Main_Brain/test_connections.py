#!/usr/bin/env python3
"""
Connection Testing Script for Multi-Agent Chatbot Copilot
Tests database, Redis, LLM API, and embedding model connections
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional
import json
import time

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that required packages are available"""
    print("🧪 Testing package imports...")
    
    missing_packages = []
    
    try:
        import psycopg2
        print("✅ psycopg2 available")
    except ImportError:
        missing_packages.append("psycopg2-binary")
    
    try:
        import redis
        print("✅ redis available")
    except ImportError:
        missing_packages.append("redis")
    
    try:
        import httpx
        print("✅ httpx available")
    except ImportError:
        missing_packages.append("httpx")
    
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers available")
    except ImportError:
        missing_packages.append("sentence-transformers")
    
    if missing_packages:
        print(f"❌ Missing packages: {missing_packages}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def test_database_connection():
    """Test PostgreSQL database connection"""
    print("\n🗄️  Testing PostgreSQL Database Connection...")
    
    try:
        import psycopg2
        from config import settings
        
        # Create connection string
        conn_params = {
            'host': settings.database.host,
            'port': settings.database.port,
            'database': settings.database.name,
            'user': settings.database.user,
            'password': settings.database.password
        }
        
        print(f"   Connecting to: {settings.database.host}:{settings.database.port}/{settings.database.name}")
        print(f"   User: {settings.database.user}")
        
        # Test connection
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database connected successfully")
        print(f"   PostgreSQL version: {version}")
        
        # Check for pgvector extension
        cursor.execute("SELECT * FROM pg_extension WHERE extname = 'vector';")
        vector_ext = cursor.fetchone()
        if vector_ext:
            print("✅ pgvector extension is installed")
        else:
            print("⚠️  pgvector extension not found")
        
        # Check for rag_embeddings table
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'rag_embeddings';
        """)
        table_exists = cursor.fetchone()[0] > 0
        
        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM rag_embeddings;")
            count = cursor.fetchone()[0]
            print(f"✅ rag_embeddings table found with {count:,} records")
        else:
            print("⚠️  rag_embeddings table not found")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    print("\n🔴 Testing Redis Connection...")
    
    try:
        import redis
        from config import settings
        
        print(f"   Connecting to: {settings.redis.host}:{settings.redis.port}")
        print(f"   Database: {settings.redis.db}")
        
        # Create Redis client
        r = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            db=settings.redis.db,
            password=settings.redis.password,
            decode_responses=True
        )
        
        # Test connection
        r.ping()
        print("✅ Redis connected successfully")
        
        # Test basic operations
        test_key = "test_connection"
        test_value = "hello_world"
        
        r.set(test_key, test_value, ex=10)  # Expire in 10 seconds
        retrieved_value = r.get(test_key)
        
        if retrieved_value == test_value:
            print("✅ Redis read/write operations working")
        else:
            print("⚠️  Redis read/write test failed")
        
        # Get Redis info
        info = r.info()
        print(f"   Redis version: {info.get('redis_version', 'unknown')}")
        print(f"   Memory usage: {info.get('used_memory_human', 'unknown')}")
        
        # Clean up test key
        r.delete(test_key)
        
        return True
        
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        return False

async def test_llm_connection():
    """Test LLM API connection"""
    print("\n🤖 Testing LLM API Connection...")
    
    try:
        import httpx
        from config import settings
        
        print(f"   Model: {settings.llm.model}")
        print(f"   Base URL: {settings.llm.base_url}")
        
        # Prepare request
        headers = {
            "Authorization": f"Bearer {settings.llm.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": settings.llm.model,
            "messages": [
                {"role": "user", "content": "Hi! Please respond with exactly: 'Connection test successful'"}
            ],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.llm.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result["choices"][0]["message"]["content"]
                print("✅ LLM API connected successfully")
                print(f"   Response: {message}")
                
                # Check usage info if available
                if "usage" in result:
                    usage = result["usage"]
                    print(f"   Tokens used: {usage.get('total_tokens', 'unknown')}")
                
                return True
            else:
                print(f"❌ LLM API request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ LLM API connection failed: {str(e)}")
        return False

def test_embedding_model():
    """Test embedding model loading"""
    print("\n🔤 Testing Embedding Model...")
    
    try:
        from sentence_transformers import SentenceTransformer
        from config import settings
        
        model_name = settings.rag.embedding_model
        print(f"   Loading model: {model_name}")
        
        # Load the model (this will download if not cached)
        start_time = time.time()
        model = SentenceTransformer(model_name)
        load_time = time.time() - start_time
        
        print(f"✅ Embedding model loaded successfully ({load_time:.2f}s)")
        
        # Test encoding
        test_texts = [
            "This is a test sentence for embedding.",
            "Another test sentence to verify the model works."
        ]
        
        start_time = time.time()
        embeddings = model.encode(test_texts)
        encode_time = time.time() - start_time
        
        print(f"✅ Embedding generation working ({encode_time:.3f}s for {len(test_texts)} texts)")
        print(f"   Embedding dimension: {embeddings.shape[1]}")
        print(f"   Expected dimension: {settings.rag.embedding_dimension}")
        
        if embeddings.shape[1] == settings.rag.embedding_dimension:
            print("✅ Embedding dimensions match configuration")
        else:
            print(f"⚠️  Embedding dimension mismatch: got {embeddings.shape[1]}, expected {settings.rag.embedding_dimension}")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedding model test failed: {str(e)}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n⚙️  Testing Configuration...")
    
    try:
        from config import settings
        
        print("✅ Configuration loaded successfully")
        
        # Check critical settings
        critical_settings = [
            ("Database host", settings.database.host),
            ("Database user", settings.database.user),
            ("Redis host", settings.redis.host),
            ("LLM model", settings.llm.model),
            ("LLM API key", "***" + settings.llm.api_key[-4:] if settings.llm.api_key else "Not set"),
            ("Embedding model", settings.rag.embedding_model),
        ]
        
        for name, value in critical_settings:
            print(f"   {name}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

async def main():
    """Run all connection tests"""
    print("🔍 Multi-Agent Chatbot Copilot Connection Tests")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database Connection", test_database_connection),
        ("Redis Connection", test_redis_connection),
        ("LLM API Connection", test_llm_connection),
        ("Embedding Model", test_embedding_model),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Connection Test Results:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All connections successful! System is ready.")
        return True
    else:
        print("⚠️  Some connections failed. Check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)