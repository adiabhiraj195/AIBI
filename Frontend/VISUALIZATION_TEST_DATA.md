# Testing the Visualization Panel

## Sample Test Data

Use this sample data to test the visualization panel without backend connection.

### Test Data Structure

```typescript
import { PlotlyChart, ChartType } from './types';

const sampleVisualizations: PlotlyChart[] = [
  // Chart 1: Bar Chart
  {
    type: ChartType.BAR,
    data: {
      traces: [
        {
          x: ['Gujarat', 'Tamil Nadu', 'Karnataka', 'Maharashtra', 'Rajasthan'],
          y: [234, 123, 89, 67, 45],
          type: 'bar',
          name: 'Total WTG Count Deviation',
          marker: {
            color: '#10b981'
          }
        }
      ]
    },
    layout: {
      title: {
        text: 'Total WTG Count Deviation by State'
      },
      xaxis: {
        title: 'State'
      },
      yaxis: {
        title: 'Deviation Count'
      }
    },
    config: {}
  },

  // Chart 2: Pie Chart
  {
    type: ChartType.PIE,
    data: {
      traces: [
        {
          labels: ['Gujarat', 'Tamil Nadu', 'Karnataka', 'Maharashtra', 'Rajasthan', 'Others'],
          values: [234, 123, 89, 67, 45, 32],
          type: 'pie',
          marker: {
            colors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
          }
        }
      ]
    },
    layout: {
      title: {
        text: 'Distribution of Total WTG Count Deviation'
      }
    },
    config: {}
  },

  // Chart 3: Scatter Plot
  {
    type: ChartType.SCATTER,
    data: {
      traces: [
        {
          x: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
          y: [234, 123, 89, 67, 45, 32, 28, 15, 12, 8],
          mode: 'markers',
          type: 'scatter',
          name: 'WTG Deviation',
          marker: {
            size: 12,
            color: '#3b82f6',
            opacity: 0.7
          }
        }
      ]
    },
    layout: {
      title: {
        text: 'Total WTG Count Deviation vs Project Count'
      },
      xaxis: {
        title: 'Number of Projects'
      },
      yaxis: {
        title: 'Total Deviation'
      }
    },
    config: {}
  }
];
```

## Testing in Your App

### Option 1: Hardcode Test Data in ChatMessage

```tsx
// In ChatMessage.tsx, temporarily add test data
const visualizations = visualizationAgent?.visualizations || sampleVisualizations;
```

### Option 2: Create a Test Component

```tsx
// Create src/components/VisualizationTest.tsx
import { VisualizationPanel } from './VisualizationPanel';
import { PlotlyChart, ChartType } from '../types';

const sampleVisualizations: PlotlyChart[] = [
  // ... paste sample data from above
];

export function VisualizationTest() {
  return (
    <div className="p-8 bg-gray-900 min-h-screen">
      <h1 className="text-white text-2xl mb-4">Visualization Panel Test</h1>
      <VisualizationPanel visualizations={sampleVisualizations} />
    </div>
  );
}
```

### Option 3: Add to Storybook (if using)

```tsx
// VisualizationPanel.stories.tsx
import { VisualizationPanel } from './VisualizationPanel';

export default {
  title: 'Components/VisualizationPanel',
  component: VisualizationPanel,
};

export const MultipleCharts = () => (
  <VisualizationPanel visualizations={sampleVisualizations} />
);

export const SingleChart = () => (
  <VisualizationPanel visualizations={[sampleVisualizations[0]]} />
);

export const NoCharts = () => (
  <VisualizationPanel visualizations={[]} />
);
```

## Backend Response Example

When your backend returns data, it should look like this:

```json
{
  "query_intent": {
    "intent_type": "visualization",
    "confidence": 0.95,
    "entities": ["wtg", "deviation", "state"]
  },
  "agent_responses": [
    {
      "agent_name": "Visualization",
      "content": "📊 **Generated 3 Visualizations**\n\nBased on 345 data records...",
      "visualizations": [
        {
          "type": "bar",
          "data": {
            "traces": [
              {
                "x": ["Gujarat", "Tamil Nadu", "Karnataka"],
                "y": [234, 123, 89],
                "type": "bar",
                "name": "Deviation Count"
              }
            ]
          },
          "layout": {
            "title": {"text": "WTG Deviation by State"},
            "xaxis": {"title": "State"},
            "yaxis": {"title": "Count"}
          },
          "config": {}
        },
        {
          "type": "pie",
          "data": {
            "traces": [
              {
                "labels": ["Gujarat", "Tamil Nadu", "Karnataka"],
                "values": [234, 123, 89],
                "type": "pie"
              }
            ]
          },
          "layout": {
            "title": {"text": "Distribution"}
          },
          "config": {}
        },
        {
          "type": "scatter",
          "data": {
            "traces": [
              {
                "x": [10, 20, 30],
                "y": [234, 123, 89],
                "mode": "markers",
                "type": "scatter"
              }
            ]
          },
          "layout": {
            "title": {"text": "Correlation"}
          },
          "config": {}
        }
      ],
      "confidence": 0.95,
      "execution_time": 1.23,
      "follow_up_questions": []
    }
  ]
}
```

## Manual Testing Steps

1. **Start your development server**
   ```bash
   npm run dev
   ```

2. **Test with backend connected**
   - Ask a query that triggers visualization
   - Example: "Show me WTG deviation by state"
   - Verify 3 charts appear with thumbnails

3. **Test thumbnail switching**
   - Click each thumbnail button
   - Verify main chart updates instantly
   - Check selected thumbnail has blue highlight

4. **Test chart interactions**
   - Hover over data points (tooltips should appear)
   - Try zoom/pan (if chart type supports it)
   - Click legend items to toggle traces

5. **Test responsive behavior**
   - Resize browser window
   - Check thumbnails adapt
   - Verify chart scales properly

6. **Test edge cases**
   - Single chart (no thumbnails should show)
   - No charts (empty state message)
   - Very long chart titles (should truncate)

## Debugging Tips

### Charts not appearing?
```tsx
// Add console logs to debug
console.log('Visualizations:', visualizations);
console.log('Selected chart:', selectedChart);
console.log('Chart data:', selectedChart?.data);
```

### Data format issues?
```tsx
// Check if traces are wrapped correctly
const traces = selectedChart.data?.traces || selectedChart.data;
console.log('Traces:', traces);
```

### Plotly errors?
- Check browser console for Plotly warnings
- Verify data arrays have matching lengths
- Ensure trace types are valid Plotly types

### Styling issues?
- Inspect element to check applied classes
- Verify Tailwind classes are compiled
- Check z-index if elements overlap

## Performance Testing

Test with large datasets:

```typescript
// Generate 100 data points
const largeDataset = {
  type: ChartType.LINE,
  data: {
    traces: [{
      x: Array.from({length: 100}, (_, i) => i),
      y: Array.from({length: 100}, () => Math.random() * 100),
      type: 'scatter',
      mode: 'lines'
    }]
  },
  layout: {
    title: 'Large Dataset Test'
  }
};
```

Expected behavior:
- Chart should render smoothly
- Interactions remain responsive
- No lag when switching between charts
