# Visualization Agent API Format Fix

## Issue
The visualization agent was returning data in a format that didn't match the Pydantic `PlotlyChart` model expected by the FastAPI endpoint.

## Error Messages
```
6 validation errors for QueryResponse
visualizations.0.chart_type
  Field required [type=missing]
visualizations.0.layout
  Field required [type=missing]
visualizations.0.data
  Input should be a valid dictionary [type=dict_type]
visualizations.2.chart_type
  Input should be 'bar', 'stacked_bar', 'line', ... [type=enum]
```

## Root Causes

### 1. Field Naming Mismatch
**Problem**: Agent returned `type` field, but model expected `chart_type`

**Fix**: Changed all chart returns to use `chart_type` instead of `type`

### 2. Data Structure Mismatch
**Problem**: Agent returned `data` as a list of Plotly traces, but model expected a dictionary

**Fix**: Wrapped traces in a dictionary: `{"traces": fig_json.get("data", [])}`

### 3. Invalid Chart Type
**Problem**: Agent returned `"table"` which wasn't in the `ChartType` enum

**Fix**: Removed summary table generation (not in supported chart types)

## Changes Made

### File: `agents/visualization.py`

#### Change 1: Field Names
```python
# Before
return {
    "type": "bar",
    "title": "...",
    "data": json.loads(fig.to_json())
}

# After
return {
    "chart_type": "bar",
    "data": {"traces": fig_json.get("data", [])},
    "layout": fig_json.get("layout", {}),
    "config": {}
}
```

#### Change 2: All Chart Types Updated
- ✅ Bar charts
- ✅ Line charts
- ✅ Pie charts
- ✅ Box plots
- ✅ Scatter plots
- ❌ Table charts (removed - not in enum)

#### Change 3: Summary Text Generation
```python
# Updated to use chart_type instead of type
chart_type = chart.get('chart_type', 'unknown').title()
```

### File: `test_visualization_agent.py`

Updated test assertions to match new format:
```python
# Before
viz.get('type')
viz.get('data', {}).keys()

# After
viz.get('chart_type')
viz.get('data', [])  # Now a dict with 'traces' key
viz.get('layout', {})
```

## Expected Format

### PlotlyChart Model (from models.py)
```python
class PlotlyChart(BaseModel):
    chart_type: ChartType  # Enum value
    data: Dict[str, Any]   # Dictionary (not list)
    layout: Dict[str, Any] # Plotly layout
    config: Optional[Dict[str, Any]]  # Optional config
```

### Visualization Agent Output
```json
{
  "chart_type": "bar",
  "data": {
    "traces": [
      {
        "x": [...],
        "y": [...],
        "type": "bar"
      }
    ]
  },
  "layout": {
    "title": {...},
    "xaxis": {...},
    "yaxis": {...}
  },
  "config": {}
}
```

## Testing Results

### Unit Tests
```bash
$ python test_visualization_agent.py
✅ All tests passing
✅ 3 visualizations generated (bar, pie, scatter)
✅ Correct format with chart_type, data, layout
```

### API Tests
```bash
$ curl -X POST http://localhost:8000/api/query \
  -d '{"query": "Show me capacity by state", "session_id": "test"}'

✅ Response: 200 OK
✅ Visualizations: 2 charts (bar, pie)
✅ Format: Valid PlotlyChart objects
```

## Impact

### Before Fix
- ❌ API returned 500 errors
- ❌ Pydantic validation failures
- ❌ No visualizations in response

### After Fix
- ✅ API returns 200 OK
- ✅ Pydantic validation passes
- ✅ 2-3 visualizations per query
- ✅ Frontend-ready format

## Chart Count Change

**Before**: 3 charts (bar, pie/box, scatter/table)
**After**: 2-3 charts (bar, pie/box, scatter)

**Reason**: Removed table chart as it's not in the ChartType enum. The system now generates:
1. Primary chart (bar or line)
2. Distribution chart (pie or box)
3. Correlation chart (scatter) - when applicable

## Frontend Integration

The format now matches what the frontend expects:

```typescript
interface PlotlyChart {
  chart_type: ChartType;
  data: {
    traces: any[];
  };
  layout: any;
  config?: any;
}
```

Frontend can render with:
```typescript
<Plot
  data={viz.data.traces}
  layout={viz.layout}
  config={viz.config}
/>
```

## Status

✅ **FIXED** - Visualization agent now returns API-compatible format
✅ **TESTED** - All tests passing
✅ **DEPLOYED** - Ready for production use

## Date
November 10, 2025
