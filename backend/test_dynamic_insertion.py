#!/usr/bin/env python3
"""
Test script to verify dynamic data insertion with any number of rows and columns
"""
import asyncio
import logging
import sys
from app.services.metadata_service import MetadataService
from app.repositories.csv_repository import CSVRepository
from app.models.csv_document import CSVDocumentCreate

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_data_insertion():
    """Test data insertion with sample CSV data"""
    
    logger.info("="*70)
    logger.info(" TESTING DYNAMIC DATA INSERTION")
    logger.info("="*70)
    
    try:
        # Create sample CSV data - variable rows and columns
        csv_data = [
            {
                'Invoice_ID': 'INV-2001',
                'Customer_Name': 'Client A',
                'Invoice_Date': '2024-01-10',
                'Invoice_Amount_USD': 25000,
                'Payment_Status': 'Paid',
                'Risk_Level': 'Low'
            },
            {
                'Invoice_ID': 'INV-2002',
                'Customer_Name': 'Client B',
                'Invoice_Date': '2024-01-15',
                'Invoice_Amount_USD': 45000,
                'Payment_Status': 'Pending',
                'Risk_Level': 'Medium'
            },
            {
                'Invoice_ID': 'INV-2003',
                'Customer_Name': 'Client C',
                'Invoice_Date': '2024-01-20',
                'Invoice_Amount_USD': 35000,
                'Payment_Status': 'Overdue',
                'Risk_Level': 'High'
            },
            {
                'Invoice_ID': 'INV-2004',
                'Customer_Name': 'Client D',
                'Invoice_Date': '2024-01-22',
                'Invoice_Amount_USD': 18000,
                'Payment_Status': 'Paid',
                'Risk_Level': 'Low'
            },
            {
                'Invoice_ID': 'INV-2005',
                'Customer_Name': 'Client E',
                'Invoice_Date': '2024-01-25',
                'Invoice_Amount_USD': 52000,
                'Payment_Status': 'Paid',
                'Risk_Level': 'Low'
            }
        ]
        
        logger.info(f"Sample data prepared: {len(csv_data)} rows with {len(csv_data[0])} columns")
        
        # Upload document
        logger.info("\n1. Uploading CSV document...")
        doc_data = CSVDocumentCreate(
            filename="test_accounts_receivable.csv",
            preview_data=csv_data[:3],  # First 3 rows as preview
            full_data=csv_data,
            row_count=len(csv_data),
            column_count=len(csv_data[0])
        )
        doc = await CSVRepository.create_document(doc_data)
        
        logger.info(f"✅ Document uploaded successfully: ID={doc.id}")
        
        # Process with metadata extraction
        logger.info(f"\n2. Processing document ID {doc.id} for dynamic table creation...")
        metadata_service = MetadataService()
        
        result = await metadata_service.process_document_with_ai(doc.id)
        
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
    success = asyncio.run(test_data_insertion())
    sys.exit(0 if success else 1)
