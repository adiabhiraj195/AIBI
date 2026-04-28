# Frontend API Routing Update - Port 8001 Configuration

## Summary
Updated the AIBI_Copilot_Frontend to call the CSV backend API (port 8001) for file upload, document management, and feedback operations, while keeping conversation/query APIs on port 8000 (Main Brain).

## Changes Made

### 1. **API Service Layer** (`src/services/api.ts`)

#### New Environment Variable
- Added `CSV_API_BASE_URL` constant that reads from `VITE_CSV_API_URL` environment variable
- Defaults to `http://localhost:8001` if not configured

#### Updated Endpoints (now point to port 8001)
1. **Feedback API**
   - `submitFeedback()` → `${CSV_API_BASE_URL}/api/v1/feedback`

2. **File Upload APIs**
   - `uploadSingleFile()` → `${CSV_API_BASE_URL}/api/v1/upload-single`
   - `uploadMultipleFiles()` → `${CSV_API_BASE_URL}/api/v1/upload-multiple`

3. **Document Management APIs**
   - `getUploadedFiles()` → `${CSV_API_BASE_URL}/api/v1/documents`
   - `getDocumentById()` → `${CSV_API_BASE_URL}/api/v1/document?id={id}`
   - `deleteUploadedFile()` → `${CSV_API_BASE_URL}/api/v1/document/{fileId}`

4. **Metadata APIs**
   - `saveMetadata()` → `${CSV_API_BASE_URL}/api/v1/metadata/save`
   - `processMetadata()` → `${CSV_API_BASE_URL}/api/v1/metadata/process/{documentId}`

### 2. **Environment Configuration**

#### `.env` File
- Added `VITE_CSV_API_URL=http://localhost:8001`
- Existing `VITE_API_URL=http://localhost:8000` remains for Main Brain queries

#### `.env.example` File
- Already includes documentation for both `VITE_API_URL` and `VITE_CSV_API_URL`

## Component Impact

### UploadedDataPage
- Automatically benefits from updated APIs in `src/services/api.ts`
- All calls to:
  - `getUploadedFiles()`
  - `getDocumentById()`
  - `saveMetadata()`
  - `processMetadata()`
  - `deleteUploadedFile()`
  
  Now route to port 8001 (CSV backend)

### Related Components
- Any component calling the updated API functions will use port 8001 for:
  - File uploads
  - Document/CSV operations
  - Metadata management
  - Feedback submission

## Architecture

```
Frontend (port 3000)
├── API_BASE_URL (port 8000)
│   └── Main Brain (RAG, multi-agent queries)
│       - Query processing
│       - Conversation management
│       - Insights generation
│
└── CSV_API_BASE_URL (port 8001)
    └── CSV Backend (file processing)
        - File uploads
        - Document management
        - Metadata/column mapping
        - Feedback storage
```

## Testing

To verify the changes:

1. **Start Docker Compose**
   ```bash
   docker compose up
   ```

2. **Test File Upload**
   - Navigate to UploadedDataPage
   - Upload a CSV file
   - Monitor network tab in browser DevTools
   - Verify request goes to `http://localhost:8001/api/v1/upload-single`

3. **Test Document Retrieval**
   - Check network tab for `http://localhost:8001/api/v1/documents`

4. **Test Feedback**
   - Submit feedback in chat
   - Verify request to `http://localhost:8001/api/v1/feedback`

## Rollback Instructions

If needed to revert to original configuration:
1. Replace all `${CSV_API_BASE_URL}` with `${API_BASE_URL}` in `src/services/api.ts`
2. Remove `VITE_CSV_API_URL` from `.env` files

## Notes

- Main conversation/query APIs remain on port 8000
- File operations are now isolated to the dedicated CSV backend (port 8001)
- Both backends share the same PostgreSQL database
- Allows independent scaling of file processing vs. conversation services
