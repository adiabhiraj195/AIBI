"""
Test script to demonstrate File Registry functionality
Run this after uploading and processing a file
"""
import asyncio
import logging
from app.repositories.file_registry_repository import FileRegistryRepository
from app.database.connection import init_and_get_engine

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_file_registry():
    """Test all file registry operations"""
    
    logger.info("\n" + "="*70)
    logger.info(" FILE REGISTRY - FEATURE TEST")
    logger.info("="*70 + "\n")
    
    try:
        # 1. Get Summary
        logger.info("1️⃣  Getting File Registry Summary...")
        summary = await FileRegistryRepository.get_registry_summary()
        logger.info(f"   Total files: {summary['total_files']}")
        logger.info(f"   Verified files: {summary['verified_files']}")
        logger.info(f"   With dynamic tables: {summary['with_dynamic_tables']}")
        logger.info(f"   Unverified files: {summary['unverified_files']}")
        
        # 2. List All Files
        logger.info("\n2️⃣  Listing All Registered Files...")
        all_files = await FileRegistryRepository.list_all_files(limit=5)
        if all_files:
            for f in all_files:
                logger.info(f"   • {f.filename}")
                logger.info(f"     - ID: {f.document_id}, Table: {f.dynamic_table_name}")
                logger.info(f"     - Category: {f.data_category}, Verified: {f.is_described}")
        else:
            logger.info("   No files registered yet")
        
        # 3. List Verified Files Only
        logger.info("\n3️⃣  Listing Verified Files Only...")
        verified_files = await FileRegistryRepository.list_all_files(limit=10, only_verified=True)
        if verified_files:
            logger.info(f"   Found {len(verified_files)} verified file(s)")
            for f in verified_files:
                logger.info(f"   • {f.filename} -> {f.dynamic_table_name}")
        else:
            logger.info("   No verified files yet")
        
        # 4. Get File by Category
        logger.info("\n4️⃣  Querying Files by Category...")
        categories = ["Financial", "Sales", "Customer", "Operations"]
        for cat in categories:
            try:
                files = await FileRegistryRepository.get_files_by_category(cat)
                if files:
                    logger.info(f"   • {cat}: {len(files)} file(s)")
                    for f in files:
                        logger.info(f"     - {f.filename}")
            except:
                pass
        
        logger.info("\n" + "="*70)
        logger.info(" ✅ FILE REGISTRY TEST COMPLETE")
        logger.info("="*70 + "\n")
        
        # 5. Instructions
        logger.info("📊 Next Steps:")
        logger.info("   1. Upload a CSV file: POST /api/v1/csv/upload")
        logger.info("   2. Save metadata: POST /api/v1/metadata/save/{doc_id}")
        logger.info("   3. Process file: POST /api/v1/metadata/process/{doc_id}")
        logger.info("   4. Check registry: GET /api/v1/metadata/registry/summary")
        logger.info("   5. List files: GET /api/v1/metadata/registry/files")
        logger.info("\n")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_file_registry())
