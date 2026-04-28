# CSV Upload and Knowledge Base API

Production-grade FastAPI application for CSV file upload, preview, metadata management, and AI-powered knowledge base creation with Supabase integration.

## 🚀 Features

### Core CSV Management
- **Single & Multiple File Upload**: Upload CSV files with validation and preview
- **Data Preview**: Get first 5 rows of uploaded CSV files
- **Full Data Access**: Retrieve complete CSV data when needed
- **File Management**: List, update, and delete uploaded documents
- **Data Validation**: Comprehensive file validation and error handling

### 🧠 AI-Powered Knowledge Base
- **Column Metadata Extraction**: Automatic detection of column names and data types
- **User Enrichment**: Add connection keys, aliases, and descriptions to columns
- **LLM Analysis**: Process metadata with Groq's Llama-3.1-8b-instant model
- **Knowledge Base Creation**: Generate structured insights and recommendations
- **Search & Discovery**: Search and browse knowledge base entries

### 🔧 Technical Features
- **Supabase Integration**: Secure cloud database storage
- **Production Ready**: Comprehensive error handling and logging
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Type Safety**: Full Pydantic model validation
- **CORS Support**: Cross-origin resource sharing enabled
- **Health Monitoring**: Built-in health check endpoints

## 📋 Requirements

- Python 3.8+
- Supabase account and project
- Groq API key for LLM features

## �️ Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd csv-upload-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
Create a `.env` file in the root directory:
```env
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
DATABASE_URL=your_supabase_database_url

# Application Configuration
DEBUG=false
APP_NAME=CSV Upload and Knowledge Base API
APP_VERSION=2.0.0
```

5. **Database Setup**
Execute the SQL commands in `database_schema.sql` in your Supabase SQL editor to create the required tables.

## 🚀 Running the Application

### Development
```bash
python main.py
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### CSV Management Endpoints

#### Upload Files
- `POST /api/v1/upload-single` - Upload single CSV file
- `POST /api/v1/upload-multiple` - Upload multiple CSV files

#### Document Management
- `GET /api/v1/document?id={id}` - Get document by ID
- `GET /api/v1/documents` - List all documents
- `PATCH /api/v1/document/{id}/description-status` - Update description status
- `DELETE /api/v1/document/{id}` - Delete document

### 🧠 Metadata & Knowledge Base Endpoints

#### Column Metadata
- `GET /api/v1/metadata/document/{id}/columns` - Extract column metadata
- `POST /api/v1/metadata/document/save` - Save enriched metadata
- `GET /api/v1/metadata/document/{id}` - Get saved metadata

#### LLM Analysis
- `POST /api/v1/metadata/document/{id}/analyze` - Analyze with LLM

#### Knowledge Base
- `GET /api/v1/metadata/knowledge-base/document/{id}` - Get knowledge base entry
- `GET /api/v1/metadata/knowledge-base` - List all entries
- `GET /api/v1/metadata/knowledge-base/search?query={query}` - Search entries

## 🔄 Complete Workflow

### 1. Upload CSV File
```python
import requests

files = {'file': ('data.csv', open('data.csv', 'rb'), 'text/csv')}
response = requests.post('http://localhost:8000/api/v1/upload-single', files=files)
document_id = response.json()['data'][0]['id']
```

### 2. Extract Column Metadata
```python
response = requests.get(f'http://localhost:8000/api/v1/metadata/document/{document_id}/columns')
columns = response.json()
```

### 3. Enrich and Save Metadata
```python
enriched_columns = []
for col in columns:
    enriched_columns.append({
        "column_name": col["column_name"],
        "data_type": col["data_type"],
        "connection_key": "your_connection_key",
        "alias": "your_alias",
        "description": "your_description"
    })

payload = {"document_id": document_id, "columns": enriched_columns}
response = requests.post('http://localhost:8000/api/v1/metadata/document/save', json=payload)
```

### 4. Analyze with LLM
```python
response = requests.post(f'http://localhost:8000/api/v1/metadata/document/{document_id}/analyze')
knowledge_base_id = response.json()['knowledge_base_id']
```

### 5. Query Knowledge Base
```python
response = requests.get(f'http://localhost:8000/api/v1/metadata/knowledge-base/document/{document_id}')
knowledge_entry = response.json()
```

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_endpoints.py
```

Or run specific examples:
```bash
python examples/upload_examples.py
python examples/metadata_examples.py
```

## 🏗️ Database Schema

The application uses the following Supabase tables:

### `csv_documents`
- Stores uploaded CSV files and metadata
- Contains preview data and full data as JSONB

### `document_metadata`
- Stores user-enriched column metadata
- Links to csv_documents via document_id

### `knowledge_base`
- Stores LLM analysis results
- Contains structured insights and recommendations

## 🔧 Configuration

### File Upload Limits
- Maximum file size: 200MB
- Allowed extensions: .csv
- Multiple file upload supported

### LLM Configuration
- Model: llama-3.1-8b-instant (Groq)
- Temperature: 0.3 (for consistent results)
- Max tokens: 2000

## 🛡️ Security Features

- Input validation with Pydantic models
- File type and size validation
- SQL injection protection via Supabase
- Error handling without sensitive data exposure
- CORS configuration for web applications

## 📊 Monitoring

- Health check endpoint: `/health`
- Comprehensive logging throughout the application
- Database connection monitoring
- Error tracking and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the example files in the `examples/` directory
3. Run the test suite to verify functionality
4. Check the logs for detailed error information