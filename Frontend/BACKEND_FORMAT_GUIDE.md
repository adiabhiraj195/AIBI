# Backend Format Guide for Visualization Agent

## Critical Format Requirements

Your Python Visualization Agent **MUST** return data in this exact format for the frontend to work correctly.

## ✅ Correct Format

### Python Code (Your Visualization Agent)

```python
import json
import plotly.express as px
import plotly.graph_objects as go

def _create_primary_chart(self, df, numeric_cols, categorical_cols, query):
    """Create a chart and return in correct format"""
    
    # Create Plotly figure
    fig = px.bar(
        df, 
        x='state', 
        y='total_wtg_count_deviation',
        title='Total WTG Count Deviation by State'
    )
    
    # Convert to JSON
    fig_json = json.loads(fig.to_json())
    
    # ✅ CORRECT: Return with "traces" wrapper
    return {
        "chart_type": "bar",  # Must match ChartType enum
        "data": {
            "traces": fig_json.get("data", [])  # ⚠️ Wrap in dict with "traces" key!
        },
        "layout": fig_json.get("layout", {}),
        "config": {}
    }
```

### JSON Response Format

```json
{
  "agent_responses": [
    {
      "agent_name": "Visualization",
      "content": "📊 **Generated 3 Visualizations**...",
      "visualizations": [
        {
          "type": "bar",
          "data": {
            "traces": [
              {
                "x": ["Gujarat", "Tamil Nadu", "Karnataka"],
                "y": [234, 123, 89],
                "type": "bar",
                "name": "Deviation Count",
                "marker": {
                  "color": "#10b981"
                }
              }
            ]
          },
          "layout": {
            "title": {
              "text": "Total WTG Count Deviation by State"
            },
            "xaxis": {
              "title": "State"
            },
            "yaxis": {
              "title": "Deviation Count"
            }
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
            "title": {
              "text": "Distribution of Deviation"
            }
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
            "title": {
              "text": "Correlation Analysis"
            }
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

## ❌ Incorrect Formats (Will NOT Work)

### Wrong: Missing "traces" wrapper
```python
# ❌ DON'T DO THIS
return {
    "chart_type": "bar",
    "data": fig_json.get("data", []),  # Missing "traces" wrapper
    "layout": fig_json.get("layout", {}),
    "config": {}
}
```

### Wrong: Title as string instead of object
```python
# ❌ DON'T DO THIS
return {
    "chart_type": "bar",
    "data": {"traces": [...]},
    "layout": {
        "title": "My Chart"  # Should be {"text": "My Chart"}
    }
}
```

### Wrong: Invalid chart type
```python
# ❌ DON'T DO THIS
return {
    "chart_type": "barchart",  # Should be "bar" (must match enum)
    "data": {"traces": [...]},
    "layout": {}
}
```

## Valid Chart Types

Your `chart_type` field must be one of these exact values:

```python
VALID_CHART_TYPES = [
    "bar",
    "stacked_bar",
    "line",
    "heatmap",
    "choropleth",
    "scatter",
    "bubble",
    "pie",
    "donut",
    "waterfall",
    "treemap",
    "box",
    "funnel",
    "sankey"
]
```

## Complete Example: All 3 Chart Methods

### Method 1: Bar Chart
```python
def _create_primary_chart(self, df, numeric_cols, categorical_cols, query):
    try:
        value_col = self._select_primary_metric(numeric_cols, df)
        group_col = self._select_grouping_column(categorical_cols, df)
        
        # Aggregate data
        agg_df = df.groupby(group_col)[value_col].sum().reset_index()
        agg_df = agg_df.nlargest(15, value_col)
        
        # Create figure
        fig = px.bar(
            agg_df, 
            x=group_col, 
            y=value_col,
            title=f"{value_col.replace('_', ' ').title()} by {group_col.replace('_', ' ').title()}"
        )
        
        # Enhance layout
        fig.update_layout(
            xaxis_title=group_col.replace('_', ' ').title(),
            yaxis_title=value_col.replace('_', ' ').title(),
            hovermode='x unified',
            template='plotly_white'
        )
        
        # Convert to proper format
        fig_json = json.loads(fig.to_json())
        return {
            "chart_type": "bar",
            "data": {
                "traces": fig_json.get("data", [])  # ✅ Correct wrapper
            },
            "layout": fig_json.get("layout", {}),
            "config": {}
        }
    except Exception as e:
        logger.error(f"Primary chart creation failed: {str(e)}")
        return None
```

### Method 2: Pie Chart
```python
def _create_distribution_chart(self, df, numeric_cols, categorical_cols):
    try:
        value_col = self._select_primary_metric(numeric_cols, df)
        group_col = self._select_grouping_column(categorical_cols, df)
        
        # Aggregate for pie chart
        agg_df = df.groupby(group_col)[value_col].sum().reset_index()
        agg_df = agg_df.nlargest(8, value_col)
        
        # Create pie chart
        fig = px.pie(
            agg_df,
            values=value_col,
            names=group_col,
            title=f"Distribution of {value_col.replace('_', ' ').title()}"
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        # Convert to proper format
        fig_json = json.loads(fig.to_json())
        return {
            "chart_type": "pie",
            "data": {
                "traces": fig_json.get("data", [])  # ✅ Correct wrapper
            },
            "layout": fig_json.get("layout", {}),
            "config": {}
        }
    except Exception as e:
        logger.error(f"Distribution chart creation failed: {str(e)}")
        return None
```

### Method 3: Scatter Plot
```python
def _create_trend_chart(self, df, numeric_cols, categorical_cols):
    try:
        x_col = numeric_cols[0]
        y_col = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
        color_col = categorical_cols[0] if categorical_cols else None
        
        # Limit data points
        plot_df = df.head(100) if len(df) > 100 else df
        
        # Create scatter plot
        if color_col and plot_df[color_col].nunique() <= 10:
            fig = px.scatter(
                plot_df,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{y_col.replace('_', ' ').title()} vs {x_col.replace('_', ' ').title()}"
            )
        else:
            fig = px.scatter(
                plot_df,
                x=x_col,
                y=y_col,
                title=f"{y_col.replace('_', ' ').title()} vs {x_col.replace('_', ' ').title()}"
            )
        
        fig.update_layout(
            xaxis_title=x_col.replace('_', ' ').title(),
            yaxis_title=y_col.replace('_', ' ').title(),
            template='plotly_white'
        )
        
        # Convert to proper format
        fig_json = json.loads(fig.to_json())
        return {
            "chart_type": "scatter",
            "data": {
                "traces": fig_json.get("data", [])  # ✅ Correct wrapper
            },
            "layout": fig_json.get("layout", {}),
            "config": {}
        }
    except Exception as e:
        logger.error(f"Trend chart creation failed: {str(e)}")
        return None
```

## Testing Your Backend Format

### Quick Test Script

```python
import json

def test_chart_format(chart):
    """Test if chart format is correct"""
    
    # Check required fields
    assert "chart_type" in chart, "Missing chart_type"
    assert "data" in chart, "Missing data"
    assert "layout" in chart, "Missing layout"
    
    # Check data structure
    assert isinstance(chart["data"], dict), "data must be a dict"
    assert "traces" in chart["data"], "data must have 'traces' key"
    assert isinstance(chart["data"]["traces"], list), "traces must be a list"
    
    # Check chart type is valid
    valid_types = ["bar", "line", "pie", "scatter", "box", "heatmap"]
    assert chart["chart_type"] in valid_types, f"Invalid chart_type: {chart['chart_type']}"
    
    # Check layout
    assert isinstance(chart["layout"], dict), "layout must be a dict"
    
    print("✅ Chart format is correct!")
    return True

# Test your chart
chart = _create_primary_chart(df, numeric_cols, categorical_cols, query)
test_chart_format(chart)
```

### Debugging Tips

```python
# Print chart structure to debug
def debug_chart(chart):
    print("Chart Type:", chart.get("chart_type"))
    print("Data Keys:", chart.get("data", {}).keys())
    print("Has Traces:", "traces" in chart.get("data", {}))
    print("Trace Count:", len(chart.get("data", {}).get("traces", [])))
    print("Layout Keys:", chart.get("layout", {}).keys())
    print("Title:", chart.get("layout", {}).get("title"))
```

## Common Mistakes to Avoid

### 1. Forgetting "traces" wrapper
```python
# ❌ Wrong
"data": fig_json.get("data", [])

# ✅ Correct
"data": {"traces": fig_json.get("data", [])}
```

### 2. Wrong title format
```python
# ❌ Wrong
"layout": {"title": "My Chart"}

# ✅ Correct
"layout": {"title": {"text": "My Chart"}}
```

### 3. Invalid chart type
```python
# ❌ Wrong
"chart_type": "barchart"

# ✅ Correct
"chart_type": "bar"
```

### 4. Missing data array
```python
# ❌ Wrong
"data": {"traces": None}

# ✅ Correct
"data": {"traces": []}
```

## Validation Checklist

Before sending response to frontend, verify:

- [ ] `chart_type` is a valid enum value
- [ ] `data` is a dictionary (not array)
- [ ] `data` contains `traces` key
- [ ] `traces` is an array of trace objects
- [ ] `layout` is a dictionary
- [ ] `layout.title` is an object with `text` key (or string)
- [ ] All 3 charts are included in response
- [ ] No null/None values in required fields

## Example Response Validator

```python
def validate_visualization_response(response):
    """Validate entire visualization response"""
    
    # Check agent response structure
    assert "agent_responses" in response
    
    # Find visualization agent
    viz_agent = next(
        (r for r in response["agent_responses"] if r["agent_name"] == "Visualization"),
        None
    )
    assert viz_agent is not None, "Visualization agent not found"
    
    # Check visualizations
    assert "visualizations" in viz_agent
    visualizations = viz_agent["visualizations"]
    assert isinstance(visualizations, list)
    assert len(visualizations) > 0, "No visualizations generated"
    
    # Validate each chart
    for i, chart in enumerate(visualizations):
        print(f"Validating chart {i+1}...")
        test_chart_format(chart)
    
    print(f"✅ All {len(visualizations)} charts are valid!")
    return True
```

## Summary

**Key Requirements:**
1. Wrap traces in dict: `{"traces": [...]}`
2. Use valid chart types from enum
3. Title as object: `{"text": "..."}`
4. Return 3 charts per query
5. Include all required fields

**Your current code is almost correct!** Just ensure the `data.traces` wrapper is in place and you're good to go.
