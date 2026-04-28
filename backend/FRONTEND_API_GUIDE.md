# Frontend API Guide

This guide focuses on the API endpoints that frontend applications will consume for the CSV Knowledge Base system.

## 🔧 Prerequisites

Before using the API, ensure your environment is configured:

```bash
# Validate your configuration
python validate_config.py

# Start the API server
python main.py
```

Required environment variables in `.env`:
- `GROQ_API_KEY`: Your Groq API key from https://console.groq.com/keys
- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`: Supabase configuration

## 🎯 Frontend Workflow

### 1. Upload CSV File
```http
POST /api/v1/upload-single
Content-Type: multipart/form-data
```

**Response:**
```json
{
  "success": true,
  "data": [{
    "id": 123,
    "filename": "sales_data.csv",
    "preview": [...],
    "row_count": 1000,
    "column_count": 5
  }]
}
```

### 2. Get Column Info for Metadata Form
```http
GET /api/v1/metadata/extract/{document_id}
```

**Response:**
```json
{
  "document_id": 123,
  "filename": "sales_data.csv",
  "columns": [
    {"column_name": "date", "data_type": "date"},
    {"column_name": "sales", "data_type": "float"},
    {"column_name": "region", "data_type": "string"}
  ],
  "total_columns": 3,
  "sample_data": [
    {"date": "2024-01-01", "sales": 1000.50, "region": "North"},
    {"date": "2024-01-02", "sales": 1200.75, "region": "South"}
  ]
}
```

### 3. Save Complete Metadata
```http
POST /api/v1/metadata/save
Content-Type: application/json
```

**Request Body:**
```json
{
  "document_id": 123,
  "columns": [
    {
      "column_name": "date",
      "data_type": "date",
      "connection_key": "date_key",
      "alias": "transaction_date",
      "description": "Date when the sales transaction occurred"
    },
    {
      "column_name": "sales",
      "data_type": "float",
      "connection_key": null,
      "alias": "revenue_amount",
      "description": "Total sales amount in USD for the transaction"
    }
  ]
}
```

**Response:**
```json
{
  "document_id": 123,
  "filename": "sales_data.csv",
  "columns": [...],
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### 4. Process with AI
```http
POST /api/v1/metadata/process/{document_id}
```

**Response:**
```json
{
  "success": true,
  "knowledge_base_id": 456,
  "message": "Document processed successfully with AI",
  "summary": "Sales transaction data with regional breakdown and temporal analysis capabilities"
}
```

### 5. Get Knowledge Base Entry
```http
GET /api/v1/metadata/knowledge-base/{document_id}
```

**Response:**
```json
{
  "id": 456,
  "document_id": 123,
  "filename": "sales_data.csv",
  "summary": "Sales transaction data with regional breakdown",
  "data_category": "sales",
  "insights": [
    "Data shows consistent daily sales patterns",
    "Regional distribution indicates market concentration",
    "Temporal data enables trend analysis"
  ],
  "use_cases": [
    "Sales performance analysis",
    "Regional market analysis",
    "Revenue forecasting"
  ],
  "column_analysis": {
    "date": {
      "purpose": "Transaction timestamp for temporal analysis",
      "data_quality": "Excellent - consistent date format",
      "business_value": "Critical for time-series analysis",
      "relationships": "Primary key for temporal joins"
    }
  },
  "data_quality_score": 92.5,
  "recommendations": [
    "Consider adding customer segmentation data",
    "Validate currency consistency across regions"
  ],
  "created_at": "2024-01-15T10:35:00Z"
}
```

## 📊 Dashboard Endpoints

### List Knowledge Base (for Dashboard)
```http
GET /api/v1/metadata/knowledge-base?limit=20&offset=0
```

**Response:**
```json
[
  {
    "id": 456,
    "document_id": 123,
    "filename": "sales_data.csv",
    "summary": "Sales transaction data with regional breakdown",
    "data_category": "sales",
    "data_quality_score": 92.5,
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

### Search Knowledge Base
```http
GET /api/v1/metadata/knowledge-base/search?query=sales&limit=10
```

**Response:** Same format as list endpoint, filtered by query.

## 🔧 Management Endpoints

### Get Saved Metadata
```http
GET /api/v1/metadata/document/{document_id}
```

### Delete Knowledge Base Entry
```http
DELETE /api/v1/metadata/knowledge-base/{entry_id}
```

## 🎨 Frontend Implementation Tips

### 1. Metadata Form Component
```javascript
// After getting column info from /metadata/extract/{id}
const MetadataForm = ({ columnInfo }) => {
  const [formData, setFormData] = useState(
    columnInfo.columns.map(col => ({
      column_name: col.column_name,
      data_type: col.data_type,
      connection_key: '',
      alias: '',
      description: '' // Required field
    }))
  );

  const handleSubmit = async () => {
    const response = await fetch('/api/v1/metadata/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        document_id: columnInfo.document_id,
        columns: formData
      })
    });
    // Handle response
  };
};
```

### 2. Knowledge Base Dashboard
```javascript
const KnowledgeBaseDashboard = () => {
  const [entries, setEntries] = useState([]);
  
  useEffect(() => {
    fetch('/api/v1/metadata/knowledge-base?limit=20')
      .then(res => res.json())
      .then(setEntries);
  }, []);

  return (
    <div>
      {entries.map(entry => (
        <div key={entry.id} className="knowledge-card">
          <h3>{entry.filename}</h3>
          <p>{entry.summary}</p>
          <span className="category">{entry.data_category}</span>
          <span className="score">{entry.data_quality_score}/100</span>
        </div>
      ))}
    </div>
  );
};
```

### 3. Search Component
```javascript
const SearchKnowledgeBase = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    const response = await fetch(
      `/api/v1/metadata/knowledge-base/search?query=${query}&limit=10`
    );
    const data = await response.json();
    setResults(data);
  };

  return (
    <div>
      <input 
        value={query} 
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search knowledge base..."
      />
      <button onClick={handleSearch}>Search</button>
      {/* Render results */}
    </div>
  );
};
```

## ✅ Validation Rules

### Required Fields
- **description**: Must be provided for all columns (not empty)
- **column_name**: Must match extracted column names
- **data_type**: Must be valid type (string, integer, float, boolean, date)

### Optional Fields
- **connection_key**: Can be null or empty
- **alias**: Can be null or empty

### Error Handling
```javascript
const handleApiError = (response) => {
  if (!response.ok) {
    if (response.status === 400) {
      // Validation error - show field-specific messages
    } else if (response.status === 404) {
      // Resource not found
    } else if (response.status === 500) {
      // Server error
    }
  }
};
```

## 🚀 Complete Frontend Flow

1. **Upload Page**: Use `/upload-single` endpoint
2. **Metadata Form**: Use `/metadata/extract/{id}` to populate form
3. **Save Metadata**: Use `/metadata/save` with complete user inputs
4. **Process with AI**: Use `/metadata/process/{id}` 
5. **View Results**: Use `/metadata/knowledge-base/{id}`
6. **Dashboard**: Use `/metadata/knowledge-base` for listing
7. **Search**: Use `/metadata/knowledge-base/search` for search functionality

## 📱 Mobile Considerations

- All endpoints return JSON suitable for mobile apps
- Use pagination parameters for large datasets
- Implement proper loading states for AI processing
- Cache knowledge base summaries for offline viewing