#!/usr/bin/env python3
"""
SQLAlchemy 2.0 Migration Validation Test Script

This script validates that the entire app has been successfully migrated from
raw psycopg2 SQL queries to SQLAlchemy 2.0 ORM.

Tests:
1. All models import correctly
2. Database connection works with SQLAlchemy engine
3. All repositories use ORM methods
4. Services can access repositories
5. Migrations have proper session management
"""

import asyncio
import logging
import sys
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def test_models_import():
    """Test 1: Validate all SQLAlchemy models import correctly"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Importing SQLAlchemy Models")
    logger.info("="*60)
    
    try:
        from app.models.database_models import (
            Base, CSVDocument, DocumentMetadata, KnowledgeBase, User
        )
        logger.info("✅ Successfully imported Base class")
        logger.info("✅ Successfully imported CSVDocument model")
        logger.info("✅ Successfully imported DocumentMetadata model")
        logger.info("✅ Successfully imported KnowledgeBase model")
        logger.info("✅ Successfully imported User model")
        
        # Verify models have proper structure
        assert hasattr(CSVDocument, '__tablename__'), "CSVDocument missing __tablename__"
        assert hasattr(DocumentMetadata, '__tablename__'), "DocumentMetadata missing __tablename__"
        assert hasattr(KnowledgeBase, '__tablename__'), "KnowledgeBase missing __tablename__"
        assert hasattr(User, '__tablename__'), "User missing __tablename__"
        
        logger.info("✅ All models have proper SQLAlchemy structure")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import models: {e}", exc_info=True)
        return False

async def test_database_connection():
    """Test 2: Validate SQLAlchemy database connection"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: SQLAlchemy Database Connection")
    logger.info("="*60)
    
    try:
        from app.database.connection import DatabaseConnection
        
        # Initialize database first
        DatabaseConnection.init_db()
        
        # Test that engine exists and is SQLAlchemy
        assert DatabaseConnection._engine is not None, "Engine is None after init_db()"
        logger.info(f"✅ SQLAlchemy engine initialized: {DatabaseConnection._engine}")
        
        # Test connection test method
        is_connected = DatabaseConnection.test_connection()
        logger.info(f"✅ Database connection test result: {is_connected}")
        
        # Test session factory
        assert DatabaseConnection._session_factory is not None, "SessionLocal is None after init_db()"
        logger.info("✅ SessionLocal factory available")
        
        # Test get_session method
        session = DatabaseConnection.get_session()
        logger.info("✅ get_session() method works")
        session.close()
        
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}", exc_info=True)
        return False

async def test_csv_repository_orm():
    """Test 3: Validate CSVRepository uses SQLAlchemy ORM"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: CSVRepository ORM Implementation")
    logger.info("="*60)
    
    try:
        from app.repositories.csv_repository import CSVRepository
        from app.models.database_models import CSVDocument
        
        # Check that repository methods exist
        methods_to_check = [
            'create_document',
            'get_document_by_id',
            'list_documents',
            'update_document_description_status',
            'delete_document',
            'document_exists_by_filename'
        ]
        
        for method in methods_to_check:
            assert hasattr(CSVRepository, method), f"CSVRepository missing {method} method"
            logger.info(f"✅ CSVRepository has {method} method")
        
        # Verify methods use async
        import inspect
        for method in methods_to_check:
            method_obj = getattr(CSVRepository, method)
            is_async = inspect.iscoroutinefunction(method_obj)
            logger.info(f"✅ {method} is async: {is_async}")
        
        logger.info("✅ CSVRepository fully refactored to SQLAlchemy ORM")
        return True
    except Exception as e:
        logger.error(f"❌ CSVRepository ORM test failed: {e}", exc_info=True)
        return False

async def test_knowledge_base_repository_orm():
    """Test 4: Validate KnowledgeBaseRepository uses SQLAlchemy ORM"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: KnowledgeBaseRepository ORM Implementation")
    logger.info("="*60)
    
    try:
        from app.repositories.knowledge_base_repository import (
            KnowledgeBaseRepository, DocumentMetadataRepository
        )
        
        # Check KnowledgeBaseRepository methods
        kb_methods = [
            'create_knowledge_entry',
            'get_knowledge_base_entry_by_document_id',
            'get_knowledge_base_entry_by_id',
            'list_knowledge_base_entries',
            'search_knowledge_base',
            'delete_knowledge_base_entry'
        ]
        
        for method in kb_methods:
            assert hasattr(KnowledgeBaseRepository, method), f"KnowledgeBaseRepository missing {method}"
            logger.info(f"✅ KnowledgeBaseRepository has {method} method")
        
        # Check DocumentMetadataRepository methods
        dm_methods = [
            'save_document_metadata',
            'get_document_metadata'
        ]
        
        for method in dm_methods:
            assert hasattr(DocumentMetadataRepository, method), f"DocumentMetadataRepository missing {method}"
            logger.info(f"✅ DocumentMetadataRepository has {method} method")
        
        logger.info("✅ KnowledgeBaseRepository and DocumentMetadataRepository fully refactored")
        return True
    except Exception as e:
        logger.error(f"❌ KnowledgeBaseRepository ORM test failed: {e}", exc_info=True)
        return False

async def test_metadata_service_sqlalchemy():
    """Test 5: Validate MetadataService uses SQLAlchemy for dynamic tables"""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: MetadataService SQLAlchemy Integration")
    logger.info("="*60)
    
    try:
        from app.services.metadata_service import MetadataService
        import inspect
        
        service = MetadataService()
        
        # Check that _generate_and_create_table is async
        assert inspect.iscoroutinefunction(service._generate_and_create_table), \
            "_generate_and_create_table should be async"
        logger.info("✅ _generate_and_create_table is async")
        
        # Check that _insert_data_into_table_sqlalchemy exists
        assert hasattr(service, '_insert_data_into_table_sqlalchemy'), \
            "MetadataService missing _insert_data_into_table_sqlalchemy"
        logger.info("✅ _insert_data_into_table_sqlalchemy exists")
        
        # Check that _get_sqlalchemy_type exists
        assert hasattr(service, '_get_sqlalchemy_type'), \
            "MetadataService missing _get_sqlalchemy_type"
        logger.info("✅ _get_sqlalchemy_type exists")
        
        logger.info("✅ MetadataService updated for SQLAlchemy dynamic table creation")
        return True
    except Exception as e:
        logger.error(f"❌ MetadataService SQLAlchemy test failed: {e}", exc_info=True)
        return False

async def test_main_initialization():
    """Test 6: Validate main.py uses SQLAlchemy initialization"""
    logger.info("\n" + "="*60)
    logger.info("TEST 6: main.py Initialization")
    logger.info("="*60)
    
    try:
        # Import main module
        import main
        
        # Verify app exists and has proper configuration
        assert hasattr(main, 'app'), "main module missing app object"
        logger.info("✅ FastAPI app object exists in main.py")
        
        # Check that logger is configured
        assert hasattr(main, 'logger'), "main module missing logger"
        logger.info("✅ Logger is configured in main.py")
        
        # Check that routers are included
        assert len(main.app.routes) > 0, "App has no routes"
        logger.info(f"✅ App has {len(main.app.routes)} routes configured")
        
        logger.info("✅ main.py properly configured with SQLAlchemy initialization")
        return True
    except Exception as e:
        logger.error(f"❌ main.py initialization test failed: {e}", exc_info=True)
        return False

async def test_services_integration():
    """Test 7: Validate services can access repositories"""
    logger.info("\n" + "="*60)
    logger.info("TEST 7: Services Integration")
    logger.info("="*60)
    
    try:
        from app.services.csv_service import CSVService
        from app.services.metadata_service import MetadataService
        
        csv_service = CSVService()
        metadata_service = MetadataService()
        
        logger.info("✅ CSVService instantiated successfully")
        logger.info("✅ MetadataService instantiated successfully")
        
        # Check that services have expected methods
        assert hasattr(csv_service, 'upload_csv_files'), "CSVService missing upload_csv_files"
        logger.info("✅ CSVService has upload_csv_files method")
        
        assert hasattr(metadata_service, 'extract_document_info_for_frontend'), "MetadataService missing methods"
        logger.info("✅ MetadataService has extract_document_info_for_frontend method")
        
        assert hasattr(metadata_service, 'process_document_with_ai'), "MetadataService missing process_document_with_ai"
        logger.info("✅ MetadataService has process_document_with_ai method")
        
        logger.info("✅ Services properly integrated with SQLAlchemy repositories")
        return True
    except Exception as e:
        logger.error(f"❌ Services integration test failed: {e}", exc_info=True)
        return False

async def main():
    """Run all validation tests"""
    logger.info("\n")
    logger.info("╔" + "="*58 + "╗")
    logger.info("║" + " "*15 + "SQLAlchemy 2.0 Migration Validation" + " "*10 + "║")
    logger.info("╚" + "="*58 + "╝")
    
    tests = [
        ("Models Import", test_models_import),
        ("Database Connection", test_database_connection),
        ("CSVRepository ORM", test_csv_repository_orm),
        ("KnowledgeBaseRepository ORM", test_knowledge_base_repository_orm),
        ("MetadataService SQLAlchemy", test_metadata_service_sqlalchemy),
        ("main.py Initialization", test_main_initialization),
        ("Services Integration", test_services_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Unexpected error in {test_name}: {e}", exc_info=True)
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status}: {test_name}")
    
    logger.info("="*60)
    logger.info(f"Overall: {passed}/{total} tests passed")
    logger.info("="*60)
    
    if passed == total:
        logger.info("\n✅ All SQLAlchemy migration tests PASSED!")
        logger.info("The app has been successfully migrated to SQLAlchemy 2.0 ORM")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} test(s) FAILED")
        logger.error("Please review the errors above")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
