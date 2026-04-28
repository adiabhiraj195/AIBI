# Frontend Integration Guide - Visualization Agent

## ✅ Backend Format Now Matches Frontend Expectations

The backend has been updated to return visualizations in the exact format your frontend expects.

## Response Format

### Complete API Response
```json
{
  "query": "Show me capacity by state",
  "intent": "insights",
  "session_id": "test_123",
  "agent_stages": [...],
  "primary_agent": "orchestrator",
  "content": "💼 Executive Business Intelligence\n\n...\n\n📊 Generated 2 Visualizations...",
  "cfo_response": null,
  "visualizations": [
    {
      "type": "bar",
      "data": {
        "traces": [
          {
            "x": ["State 1", "State 2", "State 3"],
            "y": [95155.2, 79891.2, 27475.2],
            "type": "bar",
            "name": "",
            "marker": {
              "color": "#636efa"
            }
          }
        ]
      },
      "layout": {
        "title": {
          "text": "Average Capacity by State"
        },
        "xaxis": {
          "title": "State"
        },
        "yaxis": {
          "title": "Average Capacity"
        },
        "template": "plotly_white"
      },
      "config": {}
    },
    {
      "type": "pie",
      "data": {
        "traces": [
          {
            "labels": ["State 1", "State 2", "State 3"],
            "values": [95155.2, 79891.2, 27475.2],
            "type": "pie"
          }
        ]
      },
      "layout": {
        "title": {
          "text": "Distribution of Average Capacity"
        }
      },
      "config": {}
    }
  ],
  "follow_up_questions": [],
  "confidence": 0.95,
  "total_execution_time": 15.23,
  "metadata": {...}
}
```

## Visualization Object Structure

### ✅ Correct Format (What Backend Returns)
```json
{
  "type": "bar",                    // ✅ Uses "type" (not "chart_type")
  "data": {
    "traces": [                     // ✅ Wrapped in "traces" array
      {
        "x": [...],
        "y": [...],
        "type": "bar",
        "name": "...",
        "marker": {...}
      }
    ]
  },
  "layout": {
    "title": {                      // ✅ Title as object with "text"
      "text": "Chart Title"
    },
    "xaxis": {...},
    "yaxis": {...}
  },
  "config": {}
}
```

## Supported Chart Types

The backend returns these chart types (matching your frontend expectations):

```typescript
type ChartType = 
  | "bar"
  | "line"
  | "pie"
  | "scatter"
  | "box"
```

## Frontend Usage

### React/TypeScript Example

```typescript
import Plot from 'react-plotly.js';

interface Visualization {
  type: string;
  data: {
    traces: any[];
  };
  layout: any;
  config?: any;
}

// Render visualizations
{response.visualizations.map((viz: Visualization, index: number) => (
  <Plot
    key={index}
    data={viz.data.traces}      // ✅ Access traces directly
    layout={viz.layout}
    config={viz.config || {}}
  />
))}
```

### JavaScript Example

```javascript
// Fetch and render
fetch('/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "Show me capacity by state",
    session_id: "session_123"
  })
})
.then(res => res.json())
.then(data => {
  data.visualizations.forEach(viz => {
    Plotly.newPlot('chart-container', viz.data.traces, viz.layout, viz.config);
  });
});
```

## Chart Type Details

### Bar Chart
```json
{
  "type": "bar",
  "data": {
    "traces": [{
      "x": ["Category A", "Category B"],
      "y": [100, 200],
      "type": "bar",
      "marker": { "color": "#10b981" }
    }]
  },
  "layout": {
    "title": { "text": "Bar Chart Title" },
    "xaxis": { "title": "X Axis" },
    "yaxis": { "title": "Y Axis" }
  }
}
```

### Line Chart
```json
{
  "type": "line",
  "data": {
    "traces": [{
      "x": ["Jan", "Feb", "Mar"],
      "y": [10, 20, 15],
      "type": "scatter",
      "mode": "lines+markers"
    }]
  },
  "layout": {
    "title": { "text": "Trend Over Time" }
  }
}
```

### Pie Chart
```json
{
  "type": "pie",
  "data": {
    "traces": [{
      "labels": ["A", "B", "C"],
      "values": [30, 50, 20],
      "type": "pie"
    }]
  },
  "layout": {
    "title": { "text": "Distribution" }
  }
}
```

### Scatter Plot
```json
{
  "type": "scatter",
  "data": {
    "traces": [{
      "x": [1, 2, 3, 4],
      "y": [10, 15, 13, 17],
      "mode": "markers",
      "type": "scatter"
    }]
  },
  "layout": {
    "title": { "text": "Correlation Analysis" }
  }
}
```

## API Endpoint

### Request
```bash
POST /api/query
Content-Type: application/json

{
  "query": "Show me capacity by state",
  "session_id": "unique_session_id",
  "user_id": "optional_user_id"
}
```

### Response
```json
{
  "query": "...",
  "content": "...",
  "visualizations": [...],  // Array of visualization objects
  "confidence": 0.95,
  "total_execution_time": 15.23
}
```

## Testing

### Test with cURL
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me capacity by state",
    "session_id": "test_123"
  }'
```

### Expected Response
- ✅ Status: 200 OK
- ✅ visualizations: Array with 2-3 charts
- ✅ Each chart has: type, data.traces, layout, config
- ✅ Format matches frontend expectations exactly

## Common Issues & Solutions

### Issue: "traces" is undefined
**Cause**: Trying to access `viz.data` directly instead of `viz.data.traces`

**Solution**:
```typescript
// ❌ Wrong
<Plot data={viz.data} />

// ✅ Correct
<Plot data={viz.data.traces} />
```

### Issue: Title not displaying
**Cause**: Accessing title as string instead of object

**Solution**:
```typescript
// ❌ Wrong
viz.layout.title

// ✅ Correct
viz.layout.title.text
```

### Issue: Chart type validation error
**Cause**: Using invalid chart type

**Solution**: Use only these types:
- `"bar"`, `"line"`, `"pie"`, `"scatter"`, `"box"`

## Verification Checklist

Before deploying, verify:

- ✅ Response has `visualizations` array
- ✅ Each visualization has `type` field (not `chart_type`)
- ✅ Data is wrapped in `traces` array
- ✅ Layout title is object with `text` property
- ✅ Config is present (can be empty object)
- ✅ Chart types are valid strings
- ✅ Traces contain proper Plotly data

## Sample Files

- `frontend_sample_response.json` - Complete API response example
- `test_visualizations.json` - Test visualization data

## Status

✅ **Backend Updated** - Format matches frontend expectations
✅ **Tested** - All tests passing
✅ **Ready** - No frontend changes needed

## Support

If you encounter any format issues:
1. Check the sample response files
2. Verify chart type is valid
3. Ensure accessing `viz.data.traces` (not `viz.data`)
4. Check that title is accessed as `viz.layout.title.text`

---

**Last Updated**: November 10, 2025
**Status**: Production Ready ✅
