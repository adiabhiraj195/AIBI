# Visualization Agent Documentation

## Overview

The Visualization Agent is a specialized component of the Multi-Agent Chatbot Copilot that automatically generates dynamic, contextually appropriate charts and visualizations from raw data using Plotly.

## Features

### Automatic Chart Generation
- **Generates 3 charts per query** to provide comprehensive data perspectives
- **Intelligent chart type selection** based on data characteristics
- **Business-friendly formatting** with proper labels and legends
- **Plotly JSON format** for seamless frontend integration

### Supported Chart Types

1. **Bar Chart** - For categorical comparisons and rankings
2. **Line Chart** - For temporal trends and time-series data
3. **Scatter Plot** - For correlations and relationships between variables
4. **Pie Chart** - For distribution and composition (up to 10 categories)
5. **Box Plot** - For statistical distributions
6. **Table** - For summary statistics

## Architecture

### Integration Flow

```
User Query
    ↓
Orchestrator Agent
    ↓
NL2SQL / Statistical Handler (gets raw data)
    ↓
Insights Agent (generates business intelligence)
    ↓
Visualization Agent (creates 3 charts)
    ↓
Combined Response (insights + visualizations)
```

### Data Processing Pipeline

1. **Data Preparation**: Converts raw data to pandas DataFrame
2. **Column Analysis**: Identifies numeric and categorical columns
3. **Chart Selection**: Intelligently selects 3 appropriate chart types
4. **Chart Generation**: Creates Plotly charts with business formatting
5. **JSON Export**: Converts charts to JSON for frontend rendering

## Usage

### Direct Usage

```python
from agents.visualization import visualization_agent
from agents.base import QueryContext

# Initialize agent
await visualization_agent.initialize()

# Prepare context with data
context = QueryContext(
    query="Show me capacity by state",
    session_id="session_123",
    metadata={
        "processed_data": [
            {"state": "State 1", "capacity": 150.5},
            {"state": "State 2", "capacity": 200.3},
            # ... more data
        ],
        "handler": "nl2sql_agent"
    }
)

# Generate visualizations
response = await visualization_agent.process(context)

# Access visualizations
for viz in response.visualizations:
    print(f"Chart Type: {viz['type']}")
    print(f"Title: {viz['title']}")
    # viz['data'] contains full Plotly JSON
```

### Through Orchestrator (Automatic)

The Visualization Agent is automatically invoked by the Orchestrator when data is available:

```python
from agents.orchestrator import orchestrator_agent
from agents.base import QueryContext

# Initialize orchestrator
await orchestrator_agent.initialize()

# Process query
context = QueryContext(
    query="Show me total capacity by business module",
    session_id="session_123"
)

response = await orchestrator_agent.process(context)

# Response includes:
# - response.content: Combined insights + visualization summary
# - response.visualizations: List of 3 Plotly charts
```

## Chart Selection Logic

### Primary Chart (Chart 1)
- **Bar Chart**: For categorical data without temporal patterns
- **Line Chart**: For temporal data (dates, periods, fiscal years)
- Selects the most important numeric metric (capacity, revenue, etc.)
- Groups by the most relevant categorical dimension

### Distribution Chart (Chart 2)
- **Pie Chart**: When categories ≤ 10 (shows composition)
- **Box Plot**: When categories > 10 (shows distribution)
- Visualizes how values are distributed across categories

### Trend/Correlation Chart (Chart 3)
- **Scatter Plot**: Shows relationship between two numeric variables
- Uses color coding for categorical dimensions when available
- Limited to 100 data points for performance

### Summary Table (Fallback)
- Generated if fewer than 3 charts can be created
- Shows statistical summary (count, mean, std, min, max, quartiles)

## Data Requirements

### Minimum Requirements
- At least 1 numeric column
- At least 1 categorical column (for grouping)
- Non-empty dataset

### Optimal Data Structure
```python
[
    {
        "category_field": "State 1",      # Categorical dimension
        "numeric_field": 150.5,           # Numeric metric
        "secondary_numeric": 50,          # Optional: for scatter plots
        "temporal_field": "2024-Q1"       # Optional: for line charts
    },
    # ... more records
]
```

### Column Selection Priority

**Numeric Columns** (in order of preference):
1. Columns with keywords: `total`, `sum`, `capacity`, `mwg`, `revenue`, `amount`
2. Columns with highest variance (most interesting data)

**Categorical Columns** (in order of preference):
1. Columns with keywords: `state`, `customer`, `business_module`, `project`, `phase`
2. Columns with 2-50 unique values (reasonable cardinality)

## Output Format

### Visualization Object Structure

```json
{
  "type": "bar",
  "title": "Capacity by State",
  "data": {
    "data": [...],      // Plotly trace data
    "layout": {...}     // Plotly layout configuration
  }
}
```

### Response Content

The agent generates a summary message:

```
📊 **Generated 3 Visualizations**

Based on 25 data records, I've created the following charts:

1. **Bar Chart**: Capacity by State
2. **Pie Chart**: Distribution of Capacity
3. **Scatter Chart**: WTG Count vs Capacity

These visualizations provide different perspectives on your data for comprehensive analysis.
```

## Configuration

### Agent Configuration

```python
visualization_agent = VisualizationAgent(config={
    "max_charts": 3,           # Maximum charts to generate
    "max_categories": 50,      # Maximum unique categories for grouping
    "max_scatter_points": 100  # Maximum points for scatter plots
})
```

### Chart Customization

All charts use:
- **Template**: `plotly_white` (clean, professional look)
- **Hover mode**: `x unified` (better interactivity)
- **Business-friendly labels**: Automatic title case conversion
- **Responsive layout**: Adapts to container size

## Testing

### Unit Tests

```bash
# Test visualization agent directly
python test_visualization_agent.py
```

### Integration Tests

```bash
# Test with orchestrator
python test_orchestrator_with_viz.py
```

### Test Coverage

- ✅ Basic chart generation (bar, line, pie, scatter)
- ✅ Data preparation and cleaning
- ✅ Column type detection
- ✅ Chart type selection logic
- ✅ Empty data handling
- ✅ Integration with orchestrator
- ✅ JSON serialization

## Performance

### Benchmarks
- **Initialization**: < 0.1s
- **Chart generation**: 0.5-1.0s for 3 charts
- **Data processing**: < 0.1s for up to 1000 records
- **Total overhead**: ~1s added to query response time

### Optimization
- Automatic data aggregation for large datasets (>20 records)
- Top-N filtering for readability (top 15 for bar charts, top 8 for pie charts)
- Scatter plot limiting (100 points maximum)
- Efficient DataFrame operations using pandas

## Error Handling

### Graceful Degradation
- **No data**: Returns empty visualizations with informative message
- **Invalid data**: Logs error and returns empty visualizations
- **Chart generation failure**: Skips failed chart, continues with others
- **Minimum guarantee**: Always attempts to generate at least 1 chart

### Error Messages
```python
# No data
"No data available for visualization"

# Processing error
"Unable to generate visualizations: {error_message}"
```

## Frontend Integration

### React/TypeScript Usage

```typescript
interface Visualization {
  type: string;
  title: string;
  data: any;  // Plotly JSON
}

// Render visualizations
{response.visualizations.map((viz, index) => (
  <Plot
    key={index}
    data={viz.data.data}
    layout={viz.data.layout}
  />
))}
```

### API Response Format

```json
{
  "query": "Show me capacity by state",
  "content": "💼 Executive insights...\n\n📊 Generated 3 Visualizations...",
  "visualizations": [
    {
      "type": "bar",
      "title": "Capacity by State",
      "data": { ... }
    },
    ...
  ],
  "confidence": 0.95
}
```

## Future Enhancements

### Planned Features
- [ ] Heatmap support for correlation matrices
- [ ] Choropleth maps for geographic data
- [ ] Waterfall charts for variance analysis
- [ ] Sankey diagrams for flow visualization
- [ ] Interactive filtering and drill-down
- [ ] Export to PNG/PDF
- [ ] Custom color schemes per business module

### Configuration Options
- [ ] User-specified chart preferences
- [ ] Chart count customization (1-5 charts)
- [ ] Color palette selection
- [ ] Chart size/aspect ratio control

## Troubleshooting

### Common Issues

**Issue**: No visualizations generated
- **Cause**: Empty or invalid data
- **Solution**: Check that `processed_data` in metadata is non-empty

**Issue**: Charts look cluttered
- **Cause**: Too many categories
- **Solution**: Agent automatically limits to top 15 items

**Issue**: Wrong chart type selected
- **Cause**: Data characteristics don't match expectations
- **Solution**: Review column naming and data types

### Debug Mode

Enable detailed logging:
```python
import logging
logging.getLogger("agents.visualization").setLevel(logging.DEBUG)
```

## Dependencies

```
plotly==5.17.0
pandas==2.2.2
numpy==1.26.4
```

## License

Part of the Multi-Agent Chatbot Copilot system.

## Support

For issues or questions:
1. Check test files: `test_visualization_agent.py`
2. Review integration tests: `test_orchestrator_with_viz.py`
3. Check logs for detailed error messages
