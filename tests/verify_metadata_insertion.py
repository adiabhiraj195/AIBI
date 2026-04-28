
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Setup path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Suzlon_backend'))
sys.path.insert(0, backend_path)

# Mock dependencies that metadata_service imports
# We do NOT mock 'app' or 'app.services' because we want to load the real metadata_service module
sys.modules['app.models'] = MagicMock()
sys.modules['app.models.column_metadata'] = MagicMock()
sys.modules['app.repositories'] = MagicMock()
sys.modules['app.repositories.csv_repository'] = MagicMock()
sys.modules['app.repositories.knowledge_base_repository'] = MagicMock()
sys.modules['app.repositories.file_registry_repository'] = MagicMock() # It was imported inside a method
sys.modules['app.services.llm_service'] = MagicMock()
sys.modules['app.database'] = MagicMock()
sys.modules['app.database.connection'] = MagicMock()

# Now import the class we want to test
# We have to be careful if it does 'from app.xyz import abc'
# Since we mocked sys.modules['app.xyz'], the import should succeed and give us a Mock

try:
    from app.services.metadata_service import MetadataService
except ImportError:
    # If import fails, try inserting the path again or verify structure
    print(f"Path is: {sys.path}")
    print(f"Backend path: {backend_path}")
    raise

class TestMetadataInsertion(unittest.TestCase):
    def setUp(self):
        self.service = MetadataService()
        self.mock_engine = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        
        # Setup connection chain
        self.mock_engine.raw_connection.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        
    def test_insert_data_logic(self):
        # Mock actual table columns return (from information_schema)
        # Assuming table has 'product_name', 'amount', 'category' (and NOT 'upload_date' in schema)
        self.mock_cursor.fetchall.return_value = [('product_name',), ('amount',), ('category',)]
        
        # Input data (keys might be different case/format)
        full_data = [
            {'Product Name': 'Widget A', 'Amount': 100, 'Category': 'Parts', 'upload_date': '2023-01-01'},
            {'Product Name': 'Widget B', 'Amount': 200, 'Category': 'Parts', 'upload_date': '2023-01-02'}
        ]
        
        table_name = "test_table_1"
        columns = [] # Not used
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # We call the method on the service instance
            inserted_count = loop.run_until_complete(
                self.service._insert_data_into_table_sqlalchemy(table_name, columns, full_data, self.mock_engine)
            )
            
            print(f"Inserted count: {inserted_count}")
            
            # Verify cursor execution for fetching columns
            # The exact whitespace formatting in the source file matters for this assertion
            # So we check if substring exists
            
            calls = self.mock_cursor.execute.call_args_list
            fetch_sql_call = calls[0][0][0]
            
            print(f"Fetch SQL: {fetch_sql_call}")
            self.assertIn("column_name NOT IN ('id', 'created_at', 'upload_date')", fetch_sql_call)
            
            # Verify insert calls
            self.assertEqual(inserted_count, 2)
            
            # Find insert calls
            insert_calls = [call for call in calls if "INSERT INTO" in str(call)]
            self.assertTrue(len(insert_calls) >= 2)
            
            first_call_args = insert_calls[0]
            sql = first_call_args[0][0]
            params = first_call_args[0][1]
            
            print(f"Generated SQL: {sql}")
            print(f"Params: {params}")
            
            self.assertIn(f'INSERT INTO "{table_name}"', sql)
            self.assertIn('"product_name"', sql)
            self.assertIn('"amount"', sql)
            self.assertIn('"category"', sql)
            
            # Verify values
            self.assertIn('Widget A', params)
            self.assertIn(100, params)
            self.assertIn('Parts', params)
            
        finally:
            loop.close()

if __name__ == '__main__':
    unittest.main()
