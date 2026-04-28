# Visualization Agent - Quick Start Guide

## 🚀 Quick Start

### 1. Basic Usage

```python
from agents.visualization import visualization_agent
from agents.base import QueryContext

# Initialize
await visualization_agent.initialize()

# Create context with data
context = QueryContext(
    query="Show me capacity by state",
    session_id="session_123",
    metadata={
        "processed_data": [
            {"state": "State 1", "capacity": 150.5},
            {"state": "State 2", "capacity": 200.3},
            # ... more data
        ]
    }
)

# Generate visualizations
response = await visualization_agent.process(context)

# Access results
print(f"Generated {len(response.visualizations)} charts")
for viz in response.visualizations:
    print(f"- {viz['type']}: {viz['title']}")
```

### 2. Through Orchestrator (Automatic)

```python
from agents.orchestrator import orchestrator_agent
from agents.base import QueryContext

# Initialize
await orchestrator_agent.initialize()

# Process query (visualizations generated automatically)
context = QueryContext(
    query="Show me total capacity by business module",
    session_id="session_123"
)

response = await orchestrator_agent.process(context)

# Response includes:
# - response.content: Insights + visualization summary
# - response.visualizations: List of 3 Plotly charts
```

### 3. API Usage

```bash
# POST request to /api/query
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me capacity by state",
    "session_id": "session_123"
  }'

# Response includes visualizations array
{
  "content": "...",
  "visualizations": [
    {
      "type": "bar",
      "title": "Capacity by State",
      "data": { ... }
    },
    ...
  ]
}
```

## 📊 What You Get

### 3 Charts Per Query
1. **Primary Chart**: Bar or Line chart showing main metric
2. **Distribution Chart**: Pie or Box plot showing data distribution
3. **Correlation Chart**: Scatter plot or Summary table

### Automatic Selection
- Bar charts for categorical comparisons
- Line charts for temporal trends
- Pie charts for composition (≤10 categories)
- Scatter plots for correlations
- Tables for summary statistics

## 🎨 Chart Types

| Type | Use Case | Example |
|------|----------|---------|
| Bar | Categorical comparison | Capacity by State |
| Line | Temporal trends | Capacity over Fiscal Years |
| Pie | Composition | Distribution by Module |
| Scatter | Correlation | WTG Count vs Capacity |
| Box | Distribution | Capacity Distribution |
| Table | Statistics | Summary Stats |

## 📝 Data Format

### Input Data Structure
```python
[
    {
        "category": "State 1",      # Categorical dimension
        "metric": 150.5,            # Numeric value
        "secondary": 50             # Optional: for scatter plots
    },
    # ... more records
]
```

### Output Format
```python
{
    "type": "bar",
    "title": "Capacity by State",
    "data": {
        "data": [...],      # Plotly traces
        "layout": {...}     # Plotly layout
    }
}
```

## 🧪 Testing

```bash
# Unit tests
python test_visualization_agent.py

# Integration tests
python test_orchestrator_with_viz.py

# Full demo
python demo_visualization_e2e.py
```

## 🔧 Configuration

```python
# Default configuration
visualization_agent = VisualizationAgent(config={
    "max_charts": 3,           # Number of charts to generate
    "max_categories": 50,      # Max unique values for grouping
    "max_scatter_points": 100  # Max points in scatter plots
})
```

## 📚 Documentation

- **Full Documentation**: `VISUALIZATION_AGENT_README.md`
- **Task Summary**: `TASK_6_COMPLETION_SUMMARY.md`
- **Code**: `agents/visualization.py`

## 🎯 Key Features

✅ Automatic chart generation (3 per query)
✅ Intelligent chart type selection
✅ Business-friendly formatting
✅ Plotly JSON output
✅ Frontend-ready
✅ Integrated with orchestrator
✅ Comprehensive error handling

## 🚨 Common Issues

**No visualizations generated?**
- Check that `processed_data` in metadata is non-empty
- Ensure data has at least 1 numeric and 1 categorical column

**Wrong chart type?**
- Review column naming (use keywords like 'capacity', 'state')
- Check data types (numeric vs categorical)

**Charts look cluttered?**
- Agent automatically limits to top 15 items
- Large datasets are aggregated automatically

## 💡 Tips

1. **Column Naming**: Use descriptive names (e.g., `total_capacity`, `customer_name`)
2. **Data Size**: Agent handles 1-1000 records efficiently
3. **Temporal Data**: Include date/period columns for line charts
4. **Categories**: Keep unique values between 2-50 for best results

## 🎉 Quick Examples

### Example 1: State Analysis
```python
data = [
    {"state": "State 1", "capacity": 150.5},
    {"state": "State 2", "capacity": 200.3},
]
# Generates: Bar chart, Pie chart, Summary table
```

### Example 2: Temporal Trend
```python
data = [
    {"fiscal_year": "FY2023", "capacity": 1000},
    {"fiscal_year": "FY2024", "capacity": 1200},
]
# Generates: Line chart, Distribution, Summary
```

### Example 3: Customer Analysis
```python
data = [
    {"customer": "Customer A", "capacity": 150, "projects": 5},
    {"customer": "Customer B", "capacity": 200, "projects": 8},
]
# Generates: Bar chart, Pie chart, Scatter plot
```

## 🔗 Related Components

- **Orchestrator**: Routes queries and coordinates agents
- **Insights Agent**: Generates CFO-grade business intelligence
- **NL2SQL Agent**: Retrieves raw data from database
- **Statistical Handler**: Provides aggregated metrics

## 📞 Support

For issues or questions:
1. Check test files for examples
2. Review full documentation
3. Check logs for detailed error messages
4. Verify data format and structure

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: November 10, 2025
