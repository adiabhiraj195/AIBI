# Setup Guide for CSV Knowledge Base API

This guide will help you set up the enhanced CSV Knowledge Base API with LLM integration.

## 🚀 Quick Setup

### 1. Database Schema Setup

Execute the following SQL in your Supabase SQL editor:

```sql
-- Run the complete database_schema.sql file
-- This creates the required tables: document_metadata and knowledge_base
```

### 2. Environment Variables

Ensure your `.env` file includes all required configuration:

```env
# Supabase Configuration (existing)
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
DATABASE_URL=your_supabase_database_url

# Application Configuration
DEBUG=false
APP_NAME=CSV Upload and Knowledge Base API
APP_VERSION=2.0.0

# LLM Configuration (Groq API)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
GROQ_BASE_URL=https://api.groq.com/openai/v1/chat/completions
GROQ_TEMPERATURE=0.3
GROQ_MAX_TOKENS=2000
```

**Important**: 
- Replace `your_groq_api_key_here` with your actual Groq API key
- Get your Groq API key from: https://console.groq.com/keys
- All LLM settings are now configurable via environment variables

### 3. Install New Dependencies

```bash
pip install httpx==0.25.2
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### 4. Start the Application

```bash
python main.py
```

## 🔑 Getting Groq API Key

1. Visit https://console.groq.com/
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and add it to your `.env` file

## 🧪 Testing the New Features

### 1. Test Column Metadata Extraction

```bash
# Upload a CSV file first, then extract metadata
curl -X GET "http://localhost:8000/api/v1/metadata/extract/1"
```

### 2. Test Complete Workflow

```bash
python examples/metadata_examples.py
```

### 3. Run All Tests

```bash
python test_endpoints.py
```

## 📊 API Workflow

### Complete Pipeline Example

1. **Upload CSV**: `POST /api/v1/upload-single`
2. **Extract Metadata**: `GET /api/v1/metadata/extract/{id}`
3. **Save Complete Metadata**: `POST /api/v1/metadata/save`
4. **Process with AI**: `POST /api/v1/metadata/process/{id}`
5. **Query Knowledge Base**: `GET /api/v1/metadata/knowledge-base/{id}`

## 🔧 Configuration Notes

### LLM Service Configuration

The LLM service is now fully configurable via environment variables:

- **GROQ_API_KEY**: Your Groq API key (required)
- **GROQ_MODEL**: Model to use (default: llama-3.1-8b-instant)
- **GROQ_BASE_URL**: API endpoint (default: Groq's endpoint)
- **GROQ_TEMPERATURE**: Response randomness (default: 0.3)
- **GROQ_MAX_TOKENS**: Maximum response length (default: 2000)

### Database Tables

Three main tables:
1. **csv_documents** - Original CSV storage
2. **document_metadata** - User-enriched column metadata
3. **knowledge_base** - LLM analysis results

## 🛡️ Security Considerations

1. **API Key Security**: ✅ Now stored in environment variables
2. **Input Validation**: All inputs are validated with Pydantic models
3. **Database Security**: Uses Supabase's built-in security features
4. **Error Handling**: Comprehensive error handling without exposing sensitive data

## 📈 Monitoring

### Health Checks

- **API Health**: `GET /health`
- **Database Connection**: Included in health check
- **LLM Service**: Errors logged and handled gracefully

### Logging

All services include comprehensive logging:
- Request/response logging
- Error tracking
- Performance monitoring
- Database operation logging
- LLM API call logging

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection**: Verify Supabase credentials in `.env`
2. **LLM API Errors**: 
   - Check GROQ_API_KEY is set correctly
   - Verify API key is valid and has credits
   - Check rate limits
3. **File Upload Issues**: Verify file size limits and CSV format
4. **Missing Dependencies**: Run `pip install -r requirements.txt`

### Debug Mode

Enable debug mode in `.env`:
```env
DEBUG=true
```

This provides detailed error messages and request logging.

### LLM Configuration Validation

The LLM service validates configuration on startup:
- Missing GROQ_API_KEY will raise a clear error
- Invalid configuration values are logged
- Fallback responses are provided if LLM API fails

## 🔄 Migration from Previous Version

If upgrading from the basic CSV API:

1. **Database**: Run `database_schema.sql` to add new tables
2. **Dependencies**: Install `httpx` for LLM API calls
3. **Environment**: Add LLM configuration to `.env`
4. **Code**: No breaking changes to existing endpoints
5. **Testing**: Run test suite to verify compatibility

## 📚 Next Steps

1. **Frontend Integration**: Use the new metadata endpoints in your UI
2. **Custom LLM Prompts**: Modify the LLM service for domain-specific analysis
3. **Knowledge Base Queries**: Implement advanced search and filtering
4. **Monitoring**: Set up production monitoring and alerting
5. **API Key Rotation**: Implement API key rotation for production

## 🤝 Support

For issues:
1. Check the logs for detailed error information
2. Verify database schema matches `database_schema.sql`
3. Ensure all environment variables are set correctly
4. Test individual endpoints using `/docs`
5. Review the example files for proper usage patterns

## 🔐 Production Deployment

For production:
1. Use strong, unique API keys
2. Set up environment variable management (AWS Secrets Manager, etc.)
3. Enable request rate limiting
4. Monitor API usage and costs
5. Implement proper logging and alerting