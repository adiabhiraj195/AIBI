@echo off
REM Backend Connection Test Script for Windows
REM Tests all endpoints to verify backend is working correctly

set BACKEND_URL=http://localhost:8000

echo ==================================
echo Backend Connection Test
echo ==================================
echo.
echo Testing backend at: %BACKEND_URL%
echo.

REM Test 1: Health Check
echo 1. Testing Health Check...
curl -s -o NUL -w "   Status: %%{http_code}\n" %BACKEND_URL%/health
echo.

REM Test 2: System Status
echo 2. Testing System Status...
curl -s -o NUL -w "   Status: %%{http_code}\n" %BACKEND_URL%/api/system/status
echo.

REM Test 3: Database Status
echo 3. Testing Database Status...
curl -s -o NUL -w "   Status: %%{http_code}\n" %BACKEND_URL%/api/system/database
echo.

REM Test 4: Query Endpoint
echo 4. Testing Query Endpoint...
curl -s -o NUL -w "   Status: %%{http_code}\n" -X POST %BACKEND_URL%/api/query -H "Content-Type: application/json" -d "{\"query\":\"What was the revenue for Q3 2024?\",\"session_id\":\"test_123\",\"user_id\":\"demo_user\"}"
echo.

REM Test 5: User Sessions
echo 5. Testing User Sessions...
curl -s -o NUL -w "   Status: %%{http_code}\n" %BACKEND_URL%/api/user/demo_user/sessions
echo.

REM Test 6: Conversation History
echo 6. Testing Conversation History...
curl -s -o NUL -w "   Status: %%{http_code}\n" %BACKEND_URL%/api/conversation/test_123?limit=10
echo.

echo ==================================
echo Test Complete
echo ==================================
echo.
echo Status 200 = Success
echo Status 404 = Endpoint not found
echo Status 500 = Server error
echo.
echo If all tests return 200, your backend is ready!
echo If tests fail, check:
echo   - Backend is running: python main.py
echo   - Backend is on port 8000
echo   - CORS is configured correctly
echo.
pause
