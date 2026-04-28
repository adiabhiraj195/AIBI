"""
Visualization Agent for Multi-Agent Chatbot Copilot
Generates dynamic Plotly charts from raw data using intelligent chart selection
"""

import logging
import json
from typing import Dict, Any, List, Optional, Union
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from enum import Enum

from agents.base import BaseAgent, AgentResponse, QueryContext

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """Supported chart types"""
    BAR = "bar"
    LINE = "line"
    SCATTER = "scatter"
    PIE = "pie"
    HEATMAP = "heatmap"
    BOX = "box"
    HISTOGRAM = "histogram"
    AREA = "area"


class VisualizationAgent(BaseAgent):
    """
    Visualization Agent that generates Plotly charts from raw data
    Automatically selects appropriate chart types based on data characteristics
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("visualization", config)
        self.max_charts = 3  # Generate up to 3 charts per query
    
    async def _initialize_impl(self) -> None:
        """Initialize visualization agent resources"""
        logger.info("Visualization Agent initialized successfully")
    
    async def _process_impl(self, context: QueryContext) -> AgentResponse:
        """
        Process query and generate appropriate visualizations
        Takes raw data from context metadata and creates 3 relevant charts
        """
        try:
            # Extract data from context metadata (provided by orchestrator)
            data = context.metadata.get('processed_data', [])
            handler_type = context.metadata.get('handler', 'unknown')
            
            if not data or (isinstance(data, list) and len(data) == 0):
                return AgentResponse(
                    agent_name=self.name,
                    content="No data available for visualization",
                    confidence=0.0,
                    visualizations=[]
                )
            
            # Convert data to DataFrame for easier processing
            df = self._prepare_dataframe(data)
            
            if df.empty:
                return AgentResponse(
                    agent_name=self.name,
                    content="Unable to create visualizations from provided data",
                    confidence=0.0,
                    visualizations=[]
                )
            
            # Generate 3 appropriate charts based on data characteristics
            charts = self._generate_charts(df, context.query)
            
            # Create response content
            content = self._create_visualization_summary(charts, df)
            
            return AgentResponse(
                agent_name=self.name,
                content=content,
                visualizations=charts,
                confidence=0.95,
                metadata={
                    "data_source": handler_type,
                    "chart_count": len(charts),
                    "data_rows": len(df)
                }
            )
            
        except Exception as e:
            logger.error(f"Visualization agent processing failed: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                content=f"Unable to generate visualizations: {str(e)}",
                confidence=0.0,
                visualizations=[],
                metadata={"error": str(e)}
            )
    
    def _prepare_dataframe(self, data: Union[List[Dict], Dict]) -> pd.DataFrame:
        """Convert raw data to pandas DataFrame"""
        try:
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # If single record, convert to list
                df = pd.DataFrame([data])
            else:
                logger.warning(f"Unexpected data type: {type(data)}")
                return pd.DataFrame()
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Convert numeric columns
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        df[col] = pd.to_numeric(df[col], errors='ignore')
                    except:
                        pass
            
            return df
            
        except Exception as e:
            logger.error(f"DataFrame preparation failed: {str(e)}")
            return pd.DataFrame()
    
    def _generate_charts(self, df: pd.DataFrame, query: str) -> List[Dict[str, Any]]:
        """
        Generate 3 appropriate charts based on data characteristics
        Intelligently selects chart types based on data dimensions and query context
        """
        charts = []
        
        # Identify numeric and categorical columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Remove ID columns and very long text columns
        categorical_cols = [col for col in categorical_cols 
                           if not col.lower().endswith('_id') 
                           and not col.lower() == 'content'
                           and df[col].astype(str).str.len().mean() < 100]
        
        logger.info(f"Data analysis: {len(numeric_cols)} numeric cols, {len(categorical_cols)} categorical cols")
        
        # Chart 1: Primary metric visualization (Bar or Line chart)
        if numeric_cols and categorical_cols:
            chart1 = self._create_primary_chart(df, numeric_cols, categorical_cols, query)
            if chart1:
                charts.append(chart1)
        
        # Chart 2: Distribution or comparison (Pie or Box plot)
        if len(charts) < self.max_charts and numeric_cols and categorical_cols:
            chart2 = self._create_distribution_chart(df, numeric_cols, categorical_cols)
            if chart2:
                charts.append(chart2)
        
        # Chart 3: Trend or correlation (Line or Scatter)
        if len(charts) < self.max_charts and len(numeric_cols) >= 2:
            chart3 = self._create_trend_chart(df, numeric_cols, categorical_cols)
            if chart3:
                charts.append(chart3)
        
        # Note: Summary table removed as 'table' is not in ChartType enum
        # If we need a 3rd chart and don't have one, we'll just return what we have
        
        return charts[:self.max_charts]  # Ensure max 3 charts
    
    def _create_primary_chart(
        self, 
        df: pd.DataFrame, 
        numeric_cols: List[str], 
        categorical_cols: List[str],
        query: str
    ) -> Optional[Dict[str, Any]]:
        """Create primary chart (Bar or Line) based on data"""
        try:
            # Select best numeric column (prefer aggregated metrics)
            value_col = self._select_primary_metric(numeric_cols, df)
            
            # Select best categorical column for grouping
            group_col = self._select_grouping_column(categorical_cols, df)
            
            if not value_col or not group_col:
                return None
            
            # Check if we have a second categorical dimension for color/grouping
            color_col = None
            if len(categorical_cols) >= 2:
                # Find a second categorical column that's different from group_col
                remaining_cats = [col for col in categorical_cols if col != group_col]
                if remaining_cats:
                    # Select the best secondary grouping column
                    color_col = self._select_secondary_grouping_column(remaining_cats, df)
            
            # Determine if line or bar chart
            is_temporal = self._is_temporal_column(group_col, df)
            
            # Prepare data - use all rows if we have multiple dimensions
            if color_col:
                # Don't aggregate - show all combinations
                plot_df = df[[group_col, value_col, color_col]].copy()
                # Sort by temporal column if applicable
                if is_temporal:
                    plot_df = plot_df.sort_values(group_col)
            else:
                # Aggregate data if needed (single dimension)
                if len(df) > 20:
                    plot_df = df.groupby(group_col)[value_col].sum().reset_index()
                    plot_df = plot_df.nlargest(15, value_col)  # Top 15 for readability
                else:
                    plot_df = df[[group_col, value_col]].copy()
            
            # Create chart with color dimension if available
            if is_temporal:
                fig = px.line(
                    plot_df, 
                    x=group_col, 
                    y=value_col,
                    color=color_col,
                    title=f"{value_col.replace('_', ' ').title()} Over Time" + (f" by {color_col.replace('_', ' ').title()}" if color_col else ""),
                    markers=True
                )
            else:
                fig = px.bar(
                    plot_df, 
                    x=group_col, 
                    y=value_col,
                    color=color_col,
                    title=f"{value_col.replace('_', ' ').title()} by {group_col.replace('_', ' ').title()}" + (f" and {color_col.replace('_', ' ').title()}" if color_col else ""),
                    barmode='group' if color_col else 'relative'
                )
            
            # Enhance layout
            fig.update_layout(
                xaxis_title=group_col.replace('_', ' ').title(),
                yaxis_title=value_col.replace('_', ' ').title(),
                hovermode='x unified',
                template='plotly_white',
                legend_title=color_col.replace('_', ' ').title() if color_col else None
            )
            
            # Convert to proper format for frontend
            fig_json = json.loads(fig.to_json())
            return {
                "type": "line" if is_temporal else "bar",
                "data": {"traces": fig_json.get("data", [])},
                "layout": fig_json.get("layout", {}),
                "config": {}
            }
            
        except Exception as e:
            logger.error(f"Primary chart creation failed: {str(e)}")
            return None
    
    def _create_distribution_chart(
        self, 
        df: pd.DataFrame, 
        numeric_cols: List[str], 
        categorical_cols: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Create distribution chart (Pie or Box plot)"""
        try:
            value_col = self._select_primary_metric(numeric_cols, df)
            
            # For distribution chart, prefer non-temporal categorical columns
            non_temporal_cats = [col for col in categorical_cols 
                                if not self._is_temporal_column(col, df)]
            
            # If we have non-temporal categories, use them; otherwise use any categorical
            group_col = None
            if non_temporal_cats:
                group_col = self._select_secondary_grouping_column(non_temporal_cats, df)
                if not group_col:
                    group_col = non_temporal_cats[0] if non_temporal_cats else None
            
            if not group_col and categorical_cols:
                group_col = categorical_cols[0]
            
            if not value_col or not group_col:
                return None
            
            # Check if pie chart is appropriate (limited categories)
            unique_categories = df[group_col].nunique()
            
            if unique_categories <= 10:
                # Create pie chart
                agg_df = df.groupby(group_col)[value_col].sum().reset_index()
                agg_df = agg_df.nlargest(8, value_col)  # Top 8 for pie chart
                
                fig = px.pie(
                    agg_df,
                    values=value_col,
                    names=group_col,
                    title=f"Distribution of {value_col.replace('_', ' ').title()}"
                )
                
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                # Convert to proper format for frontend
                fig_json = json.loads(fig.to_json())
                return {
                    "type": "pie",
                    "data": {"traces": fig_json.get("data", [])},
                    "layout": fig_json.get("layout", {}),
                    "config": {}
                }
            else:
                # Create box plot for distribution
                fig = px.box(
                    df,
                    y=value_col,
                    x=group_col,
                    title=f"Distribution of {value_col.replace('_', ' ').title()}"
                )
                
                fig.update_layout(
                    xaxis_title=group_col.replace('_', ' ').title(),
                    yaxis_title=value_col.replace('_', ' ').title(),
                    template='plotly_white'
                )
                
                # Convert to proper format for frontend
                fig_json = json.loads(fig.to_json())
                return {
                    "type": "box",
                    "data": {"traces": fig_json.get("data", [])},
                    "layout": fig_json.get("layout", {}),
                    "config": {}
                }
            
        except Exception as e:
            logger.error(f"Distribution chart creation failed: {str(e)}")
            return None
    
    def _create_trend_chart(
        self, 
        df: pd.DataFrame, 
        numeric_cols: List[str],
        categorical_cols: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Create trend or correlation chart (Scatter or Line)"""
        try:
            # Select two numeric columns for comparison
            if len(numeric_cols) < 2:
                return None
            
            # Prefer columns with different scales/meanings
            x_col = numeric_cols[0]
            y_col = numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0]
            
            # If we have a categorical column, use it for color
            color_col = categorical_cols[0] if categorical_cols else None
            
            # Limit data points for scatter plot
            plot_df = df.head(100) if len(df) > 100 else df
            
            if color_col and plot_df[color_col].nunique() <= 10:
                fig = px.scatter(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    title=f"{y_col.replace('_', ' ').title()} vs {x_col.replace('_', ' ').title()}",
                    size=y_col if y_col != x_col else None
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
            
            # Convert to proper format for frontend
            fig_json = json.loads(fig.to_json())
            return {
                "type": "scatter",
                "data": {"traces": fig_json.get("data", [])},
                "layout": fig_json.get("layout", {}),
                "config": {}
            }
            
        except Exception as e:
            logger.error(f"Trend chart creation failed: {str(e)}")
            return None
    
    def _create_summary_table(
        self, 
        df: pd.DataFrame, 
        numeric_cols: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Create summary statistics table as a chart"""
        try:
            if not numeric_cols:
                return None
            
            # Calculate summary statistics
            summary = df[numeric_cols].describe().round(2)
            
            # Create table visualization
            fig = go.Figure(data=[go.Table(
                header=dict(
                    values=['Statistic'] + list(summary.columns),
                    fill_color='paleturquoise',
                    align='left'
                ),
                cells=dict(
                    values=[summary.index] + [summary[col] for col in summary.columns],
                    fill_color='lavender',
                    align='left'
                )
            )])
            
            fig.update_layout(
                title="Summary Statistics",
                template='plotly_white'
            )
            
            # Convert to proper format for API
            fig_json = json.loads(fig.to_json())
            return {
                "chart_type": "table",
                "data": fig_json.get("data", []),
                "layout": fig_json.get("layout", {}),
                "config": {}
            }
            
        except Exception as e:
            logger.error(f"Summary table creation failed: {str(e)}")
            return None
    
    def _select_primary_metric(self, numeric_cols: List[str], df: pd.DataFrame) -> Optional[str]:
        """Select the most important numeric column for visualization"""
        if not numeric_cols:
            return None
        
        # Priority order for metric selection
        priority_keywords = [
            'total', 'sum', 'capacity', 'mwg', 'count', 'revenue', 
            'amount', 'value', 'avg', 'mean'
        ]
        
        # Check for priority keywords
        for keyword in priority_keywords:
            for col in numeric_cols:
                if keyword in col.lower():
                    return col
        
        # Return column with highest variance (most interesting)
        variances = {col: df[col].var() for col in numeric_cols}
        return max(variances, key=variances.get)
    
    def _select_grouping_column(self, categorical_cols: List[str], df: pd.DataFrame) -> Optional[str]:
        """Select the best categorical column for grouping (primary x-axis)"""
        if not categorical_cols:
            return None
        
        # Priority 1: Temporal columns (for x-axis)
        temporal_keywords = ['date', 'time', 'period', 'year', 'month', 'quarter', 'fiscal']
        for col in categorical_cols:
            if any(keyword in col.lower() for keyword in temporal_keywords):
                if 2 <= df[col].nunique() <= 100:
                    return col
        
        # Priority 2: Other grouping columns
        priority_keywords = [
            'state', 'customer', 'business_module', 'project', 
            'phase', 'category', 'type', 'name'
        ]
        
        # Check for priority keywords
        for keyword in priority_keywords:
            for col in categorical_cols:
                if keyword in col.lower():
                    # Ensure reasonable number of unique values
                    if 2 <= df[col].nunique() <= 50:
                        return col
        
        # Return column with reasonable cardinality
        for col in categorical_cols:
            unique_count = df[col].nunique()
            if 2 <= unique_count <= 50:
                return col
        
        return categorical_cols[0] if categorical_cols else None
    
    def _select_secondary_grouping_column(self, categorical_cols: List[str], df: pd.DataFrame) -> Optional[str]:
        """Select the best secondary categorical column for color/grouping"""
        if not categorical_cols:
            return None
        
        # Priority order for secondary grouping (color dimension)
        priority_keywords = [
            'phase', 'category', 'type', 'status', 'state',
            'project', 'business_module', 'customer', 'name'
        ]
        
        # Check for priority keywords
        for keyword in priority_keywords:
            for col in categorical_cols:
                if keyword in col.lower():
                    # Ensure reasonable number of unique values (good for color coding)
                    unique_count = df[col].nunique()
                    if 2 <= unique_count <= 10:
                        return col
        
        # Return column with reasonable cardinality for color coding
        for col in categorical_cols:
            unique_count = df[col].nunique()
            if 2 <= unique_count <= 10:
                return col
        
        return None  # Don't force a secondary dimension if not suitable
    
    def _is_temporal_column(self, col: str, df: pd.DataFrame) -> bool:
        """Check if column represents temporal data"""
        temporal_keywords = ['date', 'time', 'period', 'year', 'month', 'quarter', 'fiscal']
        
        # Check column name
        if any(keyword in col.lower() for keyword in temporal_keywords):
            return True
        
        # Check if values look like dates
        try:
            sample = df[col].astype(str).head(5)
            if any('-' in str(val) or '/' in str(val) for val in sample):
                return True
        except:
            pass
        
        return False
    
    def _create_visualization_summary(self, charts: List[Dict[str, Any]], df: pd.DataFrame) -> str:
        """Create summary text for visualizations"""
        # Return empty string - no textual summary needed
        return ""
    
    def _calculate_confidence(self, query: str, context: QueryContext = None) -> float:
        """Calculate confidence score for handling this query"""
        if not context or not context.metadata.get('processed_data'):
            return 0.0
        
        # Check if query mentions visualization keywords
        viz_keywords = ['chart', 'graph', 'plot', 'visualize', 'show', 'display']
        if any(keyword in query.lower() for keyword in viz_keywords):
            return 0.95
        
        return 0.7  # Default confidence if data is available


# Global visualization agent instance
visualization_agent = VisualizationAgent()
