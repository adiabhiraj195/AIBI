# Debugging Visualizations - Quick Guide

## Issue Fixed

The frontend was looking for visualizations in the VISUALIZATION agent, but your backend puts them in the INSIGHTS agent response.

## Changes Made

### 1. ChatMessage.tsx
```typescript
// OLD (only checked VISUALIZATION agent)
const visualizations = visualizationAgent?.visualizations || [];

// NEW (checks both INSIGHTS and VISUALIZATION agents)
const visualizations = insightsAgent?.visualizations || visualizationAgent?.visualizations || [];
```

### 2. Added Debug Logging
Both components now log to console to help debug:
- ChatMessage logs what it receives from API
- VisualizationPanel logs what visualizations it gets

## How to Test

### 1. Open Browser Console
Press F12 or right-click → Inspect → Console tab

### 2. Start Your App
```bash
npm run dev
```

### 3. Send a Query
Ask something like: "Show me capacity by state"

### 4. Check Console Logs
You should see logs like:

```
[API] Received response: {...}
[API] Transformed response - agent_responses: [...]
[ChatMessage] Query response: {...}
[ChatMessage] Insights agent: {...}
[ChatMessage] Visualizations found: [...]
[VisualizationPanel] Received visualizations: [...]
[VisualizationPanel] Visualization count: 2
[VisualizationPanel] Selected chart: {...}
```

## What to Look For

### ✅ Success Indicators
```
[ChatMessage] Visualizations found: [{type: "bar", data: {...}}, {type: "pie", ...}]
[VisualizationPanel] Visualization count: 2
```

### ❌ Problem Indicators

#### No visualizations in response:
```
[ChatMessage] Visualizations found: []
[VisualizationPanel] No visualizations to display
```
**Solution**: Check backend is returning visualizations in response

#### Visualizations exist but empty:
```
[ChatMessage] Visualizations found: [{}]
```
**Solution**: Backend format issue - check data structure

#### Wrong data format:
```
[VisualizationPanel] Chart data: undefined
[VisualizationPanel] Chart traces: undefined
```
**Solution**: Backend needs to return `data.traces` format

## Backend Response Format Check

Your backend should return:

```json
{
  "content": "...",
  "visualizations": [
    {
      "type": "bar",
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
        "title": {"text": "Chart Title"}
      },
      "config": {}
    }
  ],
  "confidence": 0.95,
  "total_execution_time": 1.23
}
```

## Common Issues & Solutions

### Issue 1: "No visualizations to display"
**Cause**: Backend not returning visualizations
**Check**: 
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show capacity by state", "session_id": "test"}'
```
**Look for**: `"visualizations": [...]` in response

### Issue 2: Visualizations array is empty
**Cause**: Backend returns `"visualizations": []`
**Solution**: Check backend Visualization Agent is running

### Issue 3: Charts show but are blank
**Cause**: Wrong data format
**Check console for**:
```
[VisualizationPanel] Chart data: {...}
[VisualizationPanel] Chart traces: undefined  ← Problem!
```
**Solution**: Backend must return `data.traces` not just `data`

### Issue 4: "type" field missing
**Cause**: Backend using old `chart_type` field
**Solution**: Backend should use `type` field (you said this is fixed)

## Quick Backend Test

Test your backend directly:

```bash
# Test backend endpoint
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me capacity by state",
    "session_id": "test123"
  }' | jq '.visualizations'
```

Expected output:
```json
[
  {
    "type": "bar",
    "data": {
      "traces": [...]
    },
    "layout": {...},
    "config": {}
  },
  {
    "type": "pie",
    "data": {
      "traces": [...]
    },
    "layout": {...},
    "config": {}
  }
]
```

## Frontend Test with Mock Data

If backend is not ready, test frontend with mock data:

```typescript
// In ChatMessage.tsx, temporarily add:
const visualizations = insightsAgent?.visualizations || [
  {
    type: 'bar',
    data: {
      traces: [{
        x: ['A', 'B', 'C'],
        y: [10, 20, 30],
        type: 'bar'
      }]
    },
    layout: {
      title: { text: 'Test Chart' }
    },
    config: {}
  }
];
```

## Verification Checklist

- [ ] Backend is running on http://localhost:8000
- [ ] Backend returns 200 OK for /api/query
- [ ] Response includes `visualizations` array
- [ ] Each visualization has `type`, `data`, `layout` fields
- [ ] `data` contains `traces` array
- [ ] Frontend console shows visualizations received
- [ ] VisualizationPanel receives non-empty array
- [ ] Charts render on screen

## Next Steps

1. **Open browser console** (F12)
2. **Send a test query**
3. **Check console logs** for the flow
4. **Share console output** if still not working

The debug logs will tell us exactly where the data flow breaks!
