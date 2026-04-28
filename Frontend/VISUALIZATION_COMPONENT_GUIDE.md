# Visualization Component Architecture

## Component Structure

```
ChatMessage
  └── VisualizationPanel
        ├── Chart Thumbnails (if multiple charts)
        │     ├── Thumbnail 1 (Bar Chart)
        │     ├── Thumbnail 2 (Pie Chart)
        │     └── Thumbnail 3 (Scatter Chart)
        │
        ├── Main Chart Display (Plotly)
        │     └── Interactive Plotly Chart
        │
        └── Chart Counter (if multiple charts)
```

## Data Flow

```
Backend Visualization Agent
  ↓
  Generates 3 PlotlyChart objects
  ↓
QueryResponse.agent_responses[].visualizations[]
  ↓
ChatMessage extracts visualizations
  ↓
VisualizationPanel receives visualizations prop
  ↓
User clicks thumbnail
  ↓
selectedIndex state updates
  ↓
Main chart re-renders with new data
```

## Key State Management

```tsx
const [selectedIndex, setSelectedIndex] = useState(0);
// Tracks which chart is currently displayed

const selectedChart = visualizations[selectedIndex];
// Gets the currently selected chart data
```

## Thumbnail Button Logic

```tsx
{visualizations.map((chart, index) => {
  const Icon = CHART_ICONS[chart.type] || BarChart3;
  const chartTitle = chart.layout?.title?.text || chart.layout?.title || `Chart ${index + 1}`;
  const isSelected = index === selectedIndex;
  
  return (
    <button onClick={() => setSelectedIndex(index)}>
      {/* Icon + Title + Type */}
    </button>
  );
})}
```

## Plotly Integration

```tsx
<Plot
  data={selectedChart.data?.traces || selectedChart.data || []}
  layout={{
    ...selectedChart.layout,
    // Custom styling overrides
  }}
  config={{
    responsive: true,
    displayModeBar: true,
    // ... other config
  }}
/>
```

## Backend Format Requirements

### ✅ Correct Format (What your agent returns)
```python
{
    "chart_type": "bar",
    "data": {
        "traces": [
            {
                "x": ["State A", "State B"],
                "y": [100, 200],
                "type": "bar",
                "name": "Revenue"
            }
        ]
    },
    "layout": {
        "title": {"text": "Revenue by State"},
        "xaxis": {"title": "State"},
        "yaxis": {"title": "Revenue"}
    },
    "config": {}
}
```

### ❌ Incorrect Format (Will not work)
```python
{
    "chart_type": "bar",
    "data": [  # Missing "traces" wrapper
        {"x": [...], "y": [...]}
    ]
}
```

## Styling Classes

### Thumbnail Button States
- **Selected**: `bg-blue-50 border-2 border-blue-500 text-blue-700`
- **Unselected**: `bg-slate-50 border-2 border-transparent text-slate-600 hover:bg-slate-100`

### Chart Container
- Height: `h-[500px]` (500px fixed height)
- Responsive: Plotly handles internal responsiveness

### Card Wrapper
- Padding: `p-6`
- Background: Inherits from Card component

## Responsive Behavior

1. **Desktop (>1024px)**
   - Thumbnails display in horizontal row
   - Full chart width
   - All interactive features enabled

2. **Tablet (768px-1024px)**
   - Thumbnails may wrap to multiple rows
   - Chart scales proportionally
   - Touch-friendly thumbnail buttons

3. **Mobile (<768px)**
   - Thumbnails stack or scroll horizontally
   - Chart maintains aspect ratio
   - Simplified Plotly controls

## Performance Considerations

- Only renders selected chart (not all 3 simultaneously)
- Plotly handles internal optimization
- State updates are instant (no loading states needed)
- Chart data is memoized by React

## Accessibility

- Keyboard navigation: Tab through thumbnails
- Screen readers: Announce chart type and title
- Focus indicators: Visible on thumbnail buttons
- ARIA labels: Added to interactive elements

## Error Handling

```tsx
if (!visualizations || visualizations.length === 0) {
  return (
    <Card className="p-6">
      <div className="h-96 flex items-center justify-center text-slate-400">
        <div className="text-center">
          <BarChart3 className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>Visualization will appear here</p>
        </div>
      </div>
    </Card>
  );
}
```

## Testing Checklist

- [ ] Single chart displays without thumbnails
- [ ] Multiple charts show thumbnail row
- [ ] Clicking thumbnails switches main chart
- [ ] Selected thumbnail has blue highlight
- [ ] Chart titles display correctly
- [ ] All chart types render (bar, line, pie, scatter, box)
- [ ] Plotly interactions work (zoom, pan, hover)
- [ ] Responsive on different screen sizes
- [ ] No console errors
- [ ] Backend data format matches expected structure
