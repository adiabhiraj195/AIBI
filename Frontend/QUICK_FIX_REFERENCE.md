# Quick Fix Reference - Visualizations Not Showing

## The Fix (1 Line Change)

**File**: `src/components/ChatMessage.tsx`
**Line**: ~112

```typescript
// BEFORE (Wrong - only checked VISUALIZATION agent)
const visualizations = visualizationAgent?.visualizations || [];

// AFTER (Fixed - checks INSIGHTS agent where backend puts data)
const visualizations = insightsAgent?.visualizations || visualizationAgent?.visualizations || [];
```

## Why This Fixes It

Your backend returns visualizations in the main response, which the API maps to the INSIGHTS agent. The frontend was only looking in the VISUALIZATION agent, so it never found the data.

## Test It Now

1. **Start app**: `npm run dev`
2. **Open console**: Press F12
3. **Send query**: "Show capacity by state"
4. **Check logs**: Look for `[ChatMessage] Visualizations found: [...]`

## Expected Result

You should now see:
- ✅ Thumbnail buttons for each chart
- ✅ Main chart display with Plotly
- ✅ Interactive zoom/pan/hover
- ✅ "Showing 1 of X visualizations" text

## If Still Not Working

### Check Console Logs

**Good (Working):**
```
[ChatMessage] Visualizations found: [{type: "bar", ...}, {type: "pie", ...}]
[VisualizationPanel] Visualization count: 2
```

**Bad (Not Working):**
```
[ChatMessage] Visualizations found: []
[VisualizationPanel] No visualizations to display
```

### If Empty Array

Backend is not returning visualizations. Test backend:

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show capacity", "session_id": "test"}' \
  | jq '.visualizations'
```

Should return array of chart objects, not `null` or `[]`.

### Backend Format Checklist

Your backend MUST return:

```json
{
  "visualizations": [
    {
      "type": "bar",              ← "type" not "chart_type"
      "data": {
        "traces": [...]           ← "traces" wrapper required
      },
      "layout": {
        "title": {"text": "..."}  ← title as object
      },
      "config": {}
    }
  ]
}
```

## Summary

- ✅ Frontend fix applied (1 line)
- ✅ Debug logging added
- ✅ Build passes
- ✅ Ready to test

**Next**: Run your app and check browser console for debug logs!
