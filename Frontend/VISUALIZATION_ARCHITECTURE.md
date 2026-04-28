# Visualization Architecture Diagram

## Component Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                         App.tsx                              │
│  - Manages chat sessions                                     │
│  - Handles query processing                                  │
│  - Maintains message history                                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    ChatMessage.tsx                           │
│  - Renders user/assistant messages                           │
│  - Extracts visualization data from QueryResponse            │
│  - Passes visualizations to VisualizationPanel               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 VisualizationPanel.tsx                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Thumbnail Row (if multiple charts)                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │ [Icon]   │  │ [Icon]   │  │ [Icon]   │           │  │
│  │  │ Bar      │  │ Pie      │  │ Scatter  │           │  │
│  │  │ Chart 1  │  │ Chart 2  │  │ Chart 3  │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Main Chart Display (Plotly)                          │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │                                                  │  │  │
│  │  │         Interactive Plotly Chart                 │  │  │
│  │  │         - Zoom/Pan                               │  │  │
│  │  │         - Hover tooltips                         │  │  │
│  │  │         - Legend toggle                          │  │  │
│  │  │         - Download PNG                           │  │  │
│  │  │                                                  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Chart Counter: "Showing 1 of 3 visualizations"      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    Backend (Python)                           │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Visualization Agent                                   │  │
│  │  - Analyzes data                                       │  │
│  │  - Generates 3 Plotly charts                           │  │
│  │  - Returns PlotlyChart[] array                         │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────────────────────┬─────────────────────────────────┘
                             │
                             │ HTTP Response
                             │
                             ▼
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (React)                           │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  api.ts (processQuery)                                 │  │
│  │  - Sends query to backend                              │  │
│  │  - Receives QueryResponse                              │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  App.tsx                                               │  │
│  │  - Stores QueryResponse in Message                     │  │
│  │  - Adds to messages array                              │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  ChatMessage.tsx                                       │  │
│  │  - Extracts visualizations from QueryResponse          │  │
│  │  - Passes to VisualizationPanel                        │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                   │
│                           ▼                                   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  VisualizationPanel.tsx                                │  │
│  │  - Manages selectedIndex state                         │  │
│  │  - Renders thumbnails                                  │  │
│  │  - Renders Plotly chart                                │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

## State Management

```
┌─────────────────────────────────────────────────────────┐
│  VisualizationPanel Component State                     │
│                                                          │
│  const [selectedIndex, setSelectedIndex] = useState(0); │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  selectedIndex: number                             │ │
│  │  - Tracks which chart is currently displayed       │ │
│  │  - Default: 0 (first chart)                        │ │
│  │  - Updates on thumbnail click                      │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  visualizations: PlotlyChart[]                     │ │
│  │  - Passed as prop from parent                      │ │
│  │  - Array of 0-3 chart objects                      │ │
│  │  - Immutable (doesn't change after render)         │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  selectedChart: PlotlyChart                        │ │
│  │  - Computed: visualizations[selectedIndex]         │ │
│  │  - Updates when selectedIndex changes              │ │
│  │  - Passed to Plotly component                      │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## User Interaction Flow

```
┌─────────────────────────────────────────────────────────────┐
│  User Action: Click Thumbnail Button                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  onClick={() => setSelectedIndex(index))                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  State Update: selectedIndex = index                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  React Re-render                                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ├─────────────────────────────────────┐
                         │                                     │
                         ▼                                     ▼
┌──────────────────────────────────┐  ┌──────────────────────────────┐
│  Thumbnail Buttons Update        │  │  Main Chart Updates          │
│  - Previous: border-transparent  │  │  - New data loaded           │
│  - Selected: border-blue-500     │  │  - Plotly re-renders         │
└──────────────────────────────────┘  └──────────────────────────────┘
```

## Chart Type Mapping

```
┌─────────────────────────────────────────────────────────────┐
│  CHART_ICONS Mapping                                         │
│                                                              │
│  ChartType.BAR        →  BarChart3 Icon                     │
│  ChartType.LINE       →  TrendingUp Icon                    │
│  ChartType.PIE        →  PieChart Icon                      │
│  ChartType.SCATTER    →  ScatterChart Icon                  │
│  ChartType.BOX        →  BarChart3 Icon (default)           │
│  ChartType.HEATMAP    →  BarChart3 Icon (default)           │
│  Other types          →  BarChart3 Icon (fallback)          │
└─────────────────────────────────────────────────────────────┘
```

## Backend to Frontend Data Transformation

```
Backend (Python)                    Frontend (TypeScript)
─────────────────                   ─────────────────────

fig = px.bar(...)                   interface PlotlyChart {
fig_json = fig.to_json()              type: ChartType;
                                      data: {
return {                                traces: any[];
  "chart_type": "bar",                };
  "data": {                           layout: any;
    "traces": [                       config?: any;
      {                             }
        "x": [...],
        "y": [...],
        "type": "bar"
      }
    ]
  },
  "layout": {
    "title": {
      "text": "Chart Title"
    }
  },
  "config": {}
}
```

## Rendering Pipeline

```
1. Component Mount
   └─> Check if visualizations exist
       ├─> No: Show empty state
       └─> Yes: Continue

2. Initialize State
   └─> selectedIndex = 0
       └─> selectedChart = visualizations[0]

3. Render Thumbnails (if length > 1)
   └─> Map over visualizations array
       └─> For each chart:
           ├─> Get icon from CHART_ICONS
           ├─> Extract title from layout
           ├─> Apply selected/unselected styles
           └─> Attach onClick handler

4. Render Main Chart
   └─> Pass to Plotly component:
       ├─> data: selectedChart.data.traces
       ├─> layout: selectedChart.layout + custom styles
       └─> config: responsive + displayModeBar settings

5. User Interaction
   └─> Click thumbnail
       └─> Update selectedIndex
           └─> Trigger re-render (step 4)
```

## Performance Optimization

```
┌─────────────────────────────────────────────────────────────┐
│  Optimization Strategy                                       │
│                                                              │
│  1. Lazy Rendering                                          │
│     - Only render selected chart                            │
│     - Don't render all 3 charts simultaneously              │
│                                                              │
│  2. State Management                                        │
│     - Single state variable (selectedIndex)                 │
│     - No complex state updates                              │
│                                                              │
│  3. Plotly Optimization                                     │
│     - Plotly handles internal caching                       │
│     - Responsive mode for efficient resizing                │
│                                                              │
│  4. React Optimization                                      │
│     - Functional component (no class overhead)              │
│     - Minimal re-renders                                    │
│     - No unnecessary useEffect hooks                        │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling

```
┌─────────────────────────────────────────────────────────────┐
│  Error Scenarios                                             │
│                                                              │
│  1. No Visualizations                                       │
│     if (!visualizations || length === 0)                    │
│     └─> Show empty state with icon                          │
│                                                              │
│  2. Missing Chart Data                                      │
│     data?.traces || data || []                              │
│     └─> Fallback to empty array                             │
│                                                              │
│  3. Missing Chart Title                                     │
│     layout?.title?.text || layout?.title || `Chart ${i+1}`  │
│     └─> Use fallback title                                  │
│                                                              │
│  4. Invalid Chart Type                                      │
│     CHART_ICONS[type] || BarChart3                          │
│     └─> Use default icon                                    │
└─────────────────────────────────────────────────────────────┘
```
