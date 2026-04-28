# Quick Start: Multi-Chart Visualization

## 🚀 What's New

Your app now displays up to 3 different visualizations per query with thumbnail switching, just like in your screenshot!

## ✅ Installation Complete

Dependencies installed:
- `plotly.js` - Plotly charting library
- `react-plotly.js` - React wrapper for Plotly
- `@types/plotly.js` - TypeScript types
- `@types/react-plotly.js` - TypeScript types

## 📦 Files Changed

1. **VisualizationPanel.tsx** - Complete rewrite with Plotly
2. **ChatMessage.tsx** - Updated to use new panel
3. **package.json** - Added Plotly dependencies

## 🎯 How to Use

### Backend Format (Python)
```python
# Your visualization agent should return:
{
    "chart_type": "bar",  # or "line", "pie", "scatter", etc.
    "data": {
        "traces": [...]  # ⚠️ Must wrap traces in dict!
    },
    "layout": {
        "title": {"text": "Chart Title"}
    },
    "config": {}
}
```

### Frontend Usage (TypeScript)
```tsx
// Already integrated in ChatMessage.tsx
<VisualizationPanel visualizations={visualizations} />
```

## 🧪 Test It

1. Start your dev server:
   ```bash
   npm run dev
   ```

2. Ask a query that generates visualizations:
   ```
   "Show me WTG deviation by state"
   ```

3. You should see:
   - 3 thumbnail buttons at the top
   - Main chart display
   - Click thumbnails to switch charts

## 🔍 Verify Backend Format

Check your backend returns this structure:
```json
{
  "agent_responses": [
    {
      "agent_name": "Visualization",
      "visualizations": [
        {
          "type": "bar",
          "data": {
            "traces": [...]  // ✅ Wrapped in dict
          },
          "layout": {...}
        }
      ]
    }
  ]
}
```

## ⚠️ Common Issues

### Charts not showing?
- Check: `data.traces` exists (not just `data`)
- Check: Backend returns array of visualizations
- Check: Chart type is valid enum value

### Thumbnails not appearing?
- Need at least 2 charts for thumbnails
- Single chart displays without thumbnails

### TypeScript errors?
- Run: `npm install` to ensure types are installed
- Restart TypeScript server in your IDE

## 📚 Documentation

- **VISUALIZATION_FEATURE.md** - Full feature documentation
- **VISUALIZATION_COMPONENT_GUIDE.md** - Technical details
- **VISUALIZATION_TEST_DATA.md** - Testing guide
- **VISUALIZATION_SUMMARY.md** - Implementation summary

## 🎨 Customization

### Change chart height:
```tsx
// In VisualizationPanel.tsx, line ~60
<div className="h-[500px]">  // Change 500px to your preference
```

### Change thumbnail style:
```tsx
// In VisualizationPanel.tsx, line ~40-50
className={`... ${isSelected ? 'bg-blue-50 ...' : '...'}`}
```

### Add more chart types:
```tsx
// In VisualizationPanel.tsx, line ~12
const CHART_ICONS: Record<string, any> = {
  bar: BarChart3,
  line: TrendingUp,
  pie: PieChart,
  scatter: ScatterChart,
  box: BarChart3,
  heatmap: BarChart3,
  // Add your custom types here
};
```

## ✨ Features

✅ Multiple chart display (up to 3)
✅ Thumbnail switching
✅ Full Plotly interactivity
✅ Responsive design
✅ Dark theme compatible
✅ All chart types supported
✅ TypeScript type-safe
✅ No breaking changes

## 🐛 Debugging

Add console logs to check data:
```tsx
console.log('Visualizations:', visualizations);
console.log('Selected chart:', selectedChart);
console.log('Chart data:', selectedChart?.data);
```

## 📞 Need Help?

1. Check browser console for errors
2. Verify backend response format
3. Review documentation files
4. Check component code for comments

## 🎉 You're Ready!

The visualization system is fully integrated and ready to use. Just ensure your backend returns data in the correct format and you'll see beautiful, interactive charts with thumbnail switching!
