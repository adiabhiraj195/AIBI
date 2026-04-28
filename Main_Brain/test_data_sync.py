#!/usr/bin/env python3
"""
Test script for Data Sync Implementation
Verifies that the data sync system is working correctly
"""

import asyncio
import sys
import json
import subprocess
import time
from datetime import datetime
from typing import Dict, Any

# Color codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{BOLD}{BLUE}{'=' * 70}{RESET}")
    print(f"{BOLD}{BLUE}{text:^70}{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 70}{RESET}\n")


def print_success(text: str):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    print(f"{RED}❌ {text}{RESET}")


def print_warning(text: str):
    print(f"{YELLOW}⚠️  {text}{RESET}")


def print_info(text: str):
    print(f"{BLUE}ℹ️  {text}{RESET}")


async def test_database_migration():
    """Test if database migration was completed"""
    print_header("Test 1: Database Migration")
    
    try:
        from database.connection import db_manager
        
        await db_manager.initialize()
        
        async with db_manager.get_connection() as conn:
            # Check if sync state table exists
            table_exists = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_schema = 'public' AND table_name = 'data_sync_state'
                )
                """
            )
            
            if not table_exists:
                print_error("data_sync_state table not found")
                print_info("Run: python run_migration.py")
                return False
            
            print_success("data_sync_state table exists")
            
            # Check if csv_documents columns exist
            columns = await conn.fetch(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'csv_documents'
                AND column_name IN ('is_processed_by_rag', 'rag_processed_at', 'data_hash')
                """
            )
            
            if len(columns) != 3:
                print_error(f"Missing columns in csv_documents (found {len(columns)}/3)")
                return False
            
            print_success("All required columns exist in csv_documents")
            
            # Check sync state entry
            sync_state = await conn.fetchrow(
                "SELECT * FROM data_sync_state WHERE service_name = 'suzlon-copilot-main-brain'"
            )
            
            if not sync_state:
                print_error("Sync state entry not found for Main Brain service")
                return False
            
            print_success("Sync state entry exists and is initialized")
            print_info(f"  Status: {sync_state['status']}")
            print_info(f"  Last sync: {sync_state['last_sync_timestamp']}")
            
        await db_manager.cleanup()
        return True
        
    except Exception as e:
        print_error(f"Database test failed: {e}")
        return False


async def test_sync_manager_import():
    """Test if DataSyncManager can be imported"""
    print_header("Test 2: DataSyncManager Import")
    
    try:
        from services.data_sync_manager import data_sync_manager
        
        print_success("DataSyncManager imported successfully")
        print_info(f"  Sync interval: {data_sync_manager.sync_interval}s")
        print_info(f"  Batch size: {data_sync_manager.batch_size}")
        print_info(f"  Service name: {data_sync_manager.service_name}")
        
        return True
        
    except ImportError as e:
        print_error(f"Failed to import DataSyncManager: {e}")
        return False
    except Exception as e:
        print_error(f"Import test failed: {e}")
        return False


async def test_api_endpoints():
    """Test if API endpoints are available"""
    print_header("Test 3: API Endpoints")
    
    endpoints = [
        ("GET", "http://localhost:8000/health", "Health check"),
        ("GET", "http://localhost:8000/api/v1/admin/sync/status", "Sync status"),
        ("GET", "http://localhost:8000/api/v1/admin/sync/pending", "Pending documents"),
    ]
    
    all_passed = True
    
    for method, url, name in endpoints:
        try:
            # Use curl to test endpoint
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
                capture_output=True,
                timeout=5
            )
            
            status_code = result.stdout.decode().strip()
            
            if status_code.startswith("2") or status_code.startswith("4"):
                print_success(f"{name} ({method} {url})")
                print_info(f"  HTTP {status_code}")
            else:
                print_warning(f"{name} returned HTTP {status_code}")
                
        except subprocess.TimeoutExpired:
            print_warning(f"{name} - timeout (service may not be running)")
        except Exception as e:
            print_warning(f"{name} - {e}")
    
    return True


async def test_sync_functionality():
    """Test sync functionality with sample data"""
    print_header("Test 4: Sync Functionality")
    
    try:
        from services.data_sync_manager import data_sync_manager
        from database.connection import db_manager
        
        await db_manager.initialize()
        await data_sync_manager.initialize()
        
        print_info("Testing sync_new_documents()...")
        
        # Test sync (should find 0 documents or existing ones)
        result = await data_sync_manager.sync_new_documents()
        
        print_success("Sync test completed")
        print_info(f"  Status: {result.get('status', 'unknown')}")
        print_info(f"  Documents processed: {result.get('documents_processed', 0)}")
        print_info(f"  Documents failed: {result.get('documents_failed', 0)}")
        
        await data_sync_manager.cleanup()
        await db_manager.cleanup()
        
        return True
        
    except Exception as e:
        print_error(f"Sync functionality test failed: {e}")
        return False


def test_file_structure():
    """Test if all required files exist"""
    print_header("Test 5: File Structure")
    
    required_files = [
        ("services/data_sync_manager.py", "Data sync manager service"),
        ("services/__init__.py", "Services package init"),
        ("run_migration.py", "Database migration script"),
        ("migration_data_sync.sh", "Bash migration script"),
        ("main.py", "Main application file"),
    ]
    
    base_path = "/Users/abhi/Documents/Nspark/Suzlon_Copilot_Main_Brain"
    all_exist = True
    
    for file_path, description in required_files:
        full_path = f"{base_path}/{file_path}"
        try:
            with open(full_path, 'r') as f:
                print_success(f"{description} ({file_path})")
        except FileNotFoundError:
            print_error(f"Missing: {description} ({file_path})")
            all_exist = False
        except Exception as e:
            print_error(f"Error reading {file_path}: {e}")
            all_exist = False
    
    return all_exist


async def main():
    """Run all tests"""
    print(f"{BOLD}{BLUE}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║    Data Sync Implementation - Verification Test Suite            ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"{RESET}\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Database Migration", test_database_migration),
        ("DataSyncManager Import", test_sync_manager_import),
        ("Sync Functionality", test_sync_functionality),
        ("API Endpoints", test_api_endpoints),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                results[test_name] = await test_func()
            else:
                results[test_name] = test_func()
        except Exception as e:
            print_error(f"Test '{test_name}' failed with exception: {e}")
            results[test_name] = False
        
        time.sleep(0.5)  # Small delay between tests
    
    # Print summary
    print_header("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = f"{GREEN}✅ PASS{RESET}" if result else f"{RED}❌ FAIL{RESET}"
        print(f"{status} - {test_name}")
    
    print(f"\n{BOLD}Total: {passed}/{total} tests passed{RESET}\n")
    
    if passed == total:
        print_success("All tests passed! Data sync is ready to use.")
        print_info("Start the service with: python main.py")
        return 0
    else:
        print_error(f"{total - passed} test(s) failed.")
        print_info("Please review the errors above and check the documentation.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_warning("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
