"""Test script to verify data insertion into dynamic tables"""
import asyncio
import logging
from app.services.metadata_service import MetadataService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_reprocess():
    """Reprocess document 14 to trigger data insertion"""
    doc_id = 14
    
    logger.info("="*70)
    logger.info(f" REPROCESSING Document ID: {doc_id}")
    logger.info("="*70)
    
    try:
        # Initialize services
        metadata_service = MetadataService()
        
        # Process document (this will recreate table and insert data)
        result = await metadata_service.process_document_with_ai(doc_id)
        
        logger.info("\n" + "="*70)
        logger.info(" PROCESS COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        logger.info(f"Success: {result.success}")
        logger.info(f"Message: {result.message}")
        logger.info(f"Knowledge Base ID: {result.knowledge_base_id}")
        
        return True
        
    except Exception as e:
        logger.error("\n" + "="*70)
        logger.error(" PROCESS FAILED")
        logger.error("="*70)
        logger.error(f"Error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    asyncio.run(test_reprocess())
