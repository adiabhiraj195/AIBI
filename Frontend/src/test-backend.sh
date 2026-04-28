#!/bin/bash

# Backend Connection Test Script
# Tests all endpoints to verify backend is working correctly

BACKEND_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=================================="
echo "Backend Connection Test"
echo "=================================="
echo ""
echo "Testing backend at: $BACKEND_URL"
echo ""

# Test 1: Health Check
echo -n "1. Health Check... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/health" 2>/dev/null)
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $RESPONSE)"
else
    echo -e "${RED}✗ FAIL${NC} (Status: $RESPONSE)"
fi

# Test 2: System Status
echo -n "2. System Status... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/system/status" 2>/dev/null)
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $RESPONSE)"
else
    echo -e "${RED}✗ FAIL${NC} (Status: $RESPONSE)"
fi

# Test 3: Database Status
echo -n "3. Database Status... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/system/database" 2>/dev/null)
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $RESPONSE)"
else
    echo -e "${RED}✗ FAIL${NC} (Status: $RESPONSE)"
fi

# Test 4: Query Endpoint
echo -n "4. Query Endpoint... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BACKEND_URL/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query":"What was the revenue for Q3 2024?","session_id":"test_123","user_id":"demo_user"}' 2>/dev/null)
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $RESPONSE)"
else
    echo -e "${RED}✗ FAIL${NC} (Status: $RESPONSE)"
fi

# Test 5: User Sessions
echo -n "5. User Sessions... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/user/demo_user/sessions" 2>/dev/null)
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $RESPONSE)"
else
    echo -e "${RED}✗ FAIL${NC} (Status: $RESPONSE)"
fi

# Test 6: Conversation History
echo -n "6. Conversation History... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/conversation/test_123?limit=10" 2>/dev/null)
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (Status: $RESPONSE)"
else
    echo -e "${YELLOW}⚠ WARNING${NC} (Status: $RESPONSE) - Session may not exist yet"
fi

echo ""
echo "=================================="
echo "Test Complete"
echo "=================================="
echo ""
echo "If all tests pass, your backend is ready!"
echo "If tests fail, check:"
echo "  - Backend is running: python main.py"
echo "  - Backend is on port 8000"
echo "  - CORS is configured correctly"
echo ""
