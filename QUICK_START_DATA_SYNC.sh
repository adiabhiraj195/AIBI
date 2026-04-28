#!/bin/bash
# Quick Start Script for Data Sync Implementation
# This script sets up and starts the data sync system

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║     AIBI Data Sync Implementation Quick Start            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Step 1: Check prerequisites
echo -e "${YELLOW}Step 1: Checking prerequisites...${NC}"
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python found${NC}"

if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠️  psql not found (optional - for direct SQL checks)${NC}"
else
    echo -e "${GREEN}✅ psql found${NC}"
fi

# Step 2: Navigate to Main Brain directory
echo -e "\n${YELLOW}Step 2: Setting up working directory...${NC}"
MAIN_BRAIN_DIR="/Users/abhi/Documents/Nspark/AIBI_Copilot_Main_Brain"
if [ ! -d "$MAIN_BRAIN_DIR" ]; then
    echo -e "${RED}❌ Directory not found: $MAIN_BRAIN_DIR${NC}"
    exit 1
fi
cd "$MAIN_BRAIN_DIR"
echo -e "${GREEN}✅ Working in: $(pwd)${NC}"

# Step 3: Verify migration files exist
echo -e "\n${YELLOW}Step 3: Verifying migration files...${NC}"
if [ ! -f "run_migration.py" ]; then
    echo -e "${RED}❌ run_migration.py not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ run_migration.py found${NC}"

if [ ! -f "services/data_sync_manager.py" ]; then
    echo -e "${RED}❌ services/data_sync_manager.py not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ services/data_sync_manager.py found${NC}"

# Step 4: Create Python virtual environment (if needed)
echo -e "\n${YELLOW}Step 4: Checking Python environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}ℹ️  No virtual environment found${NC}"
    echo -e "${YELLOW}Make sure you have dependencies installed:${NC}"
    echo -e "${YELLOW}  pip install -r requirements.txt${NC}"
fi

# Step 5: Run database migration
echo -e "\n${YELLOW}Step 5: Running database migration...${NC}"
echo -e "${BLUE}This will create necessary tables and columns${NC}\n"

python run_migration.py

if [ $? -ne 0 ]; then
    echo -e "\n${RED}❌ Migration failed!${NC}"
    echo -e "${YELLOW}Please check your database connection settings in .env${NC}"
    exit 1
fi

echo -e "\n${GREEN}✅ Migration completed successfully!${NC}"

# Step 6: Provide next steps
echo -e "\n${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  Setup Complete! ✅                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}📋 Next Steps:${NC}\n"

echo "1️⃣  Start the Main Brain service:"
echo -e "   ${BLUE}python main.py${NC}\n"

echo "2️⃣  In another terminal, start the Backend service:"
echo -e "   ${BLUE}cd ../AIBI_backend && python main.py${NC}\n"

echo "3️⃣  Verify sync status:"
echo -e "   ${BLUE}curl http://localhost:8000/api/v1/admin/sync/status | jq .${NC}\n"

echo "4️⃣  Test by uploading a CSV:"
echo -e "   ${BLUE}curl -X POST http://localhost:8001/api/v1/csv/upload \\${NC}"
echo -e "   ${BLUE}  -F 'file=@test.csv' -F 'filename=test.csv'${NC}\n"

echo "5️⃣  Check if it was synced:"
echo -e "   ${BLUE}curl http://localhost:8000/api/v1/admin/sync/pending | jq .${NC}\n"

echo -e "${YELLOW}📚 Documentation:${NC}"
echo -e "   See: ${BLUE}DATA_SYNC_IMPLEMENTATION_GUIDE.md${NC}\n"

echo -e "${YELLOW}🔍 Quick Commands:${NC}"
echo -e "   Status:  ${BLUE}curl http://localhost:8000/api/v1/admin/sync/status${NC}"
echo -e "   Pending: ${BLUE}curl http://localhost:8000/api/v1/admin/sync/pending${NC}"
echo -e "   Trigger: ${BLUE}curl -X POST http://localhost:8000/api/v1/admin/sync/trigger${NC}\n"

echo -e "${GREEN}Your ML models will now automatically sync with new uploads! 🚀${NC}\n"
