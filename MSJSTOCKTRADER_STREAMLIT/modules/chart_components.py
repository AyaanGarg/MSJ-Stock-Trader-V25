import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

class ChartComponents:
    """Handles creation of different chart types using Plotly."""
    
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
    
    def create_chart(self, chart_type: str, df: pd.DataFrame, config: dict):
        """Create chart based on type and configuration."""
        try:
            if chart_type == "Bar Chart":
                return self._create_bar_chart(df, config)
            elif chart_type == "Line Chart":
                return self._create_line_chart(df, config)
            elif chart_type == "Scatter Plot":
                return self._create_scatter_plot(df, config)
            elif chart_type == "Pie Chart":
                return self._create_pie_chart(df, config)
            elif chart_type == "Histogram":
                return self._create_histogram(df, config)
            elif chart_type == "Box Plot":
                return self._create_box_plot(df, config)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")
                
        except Exception as e:
            # Return error chart
            return self._create_error_chart(str(e))
    
    def _create_bar_chart(self, df: pd.DataFrame, config: dict):
        """Create bar chart."""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        color_col = config.get('color_column')
        title = config.get('title', 'Bar Chart')
        
        if not x_col or not y_col:
            raise ValueError("X and Y columns are required for bar chart")
        
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            color_discrete_sequence=self.color_palette
        )
        
        self._apply_common_styling(fig)
        return fig
    
    def _create_line_chart(self, df: pd.DataFrame, config: dict):
        """Create line chart."""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        color_col = config.get('color_column')
        title = config.get('title', 'Line Chart')
        
        if not x_col or not y_col:
            raise ValueError("X and Y columns are required for line chart")
        
        fig = px.line(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            color_discrete_sequence=self.color_palette
        )
        
        self._apply_common_styling(fig)
        return fig
    
    def _create_scatter_plot(self, df: pd.DataFrame, config: dict):
        """Create scatter plot."""
        x_col = config.get('x_column')
        y_col = config.get('y_column')
        color_col = config.get('color_column')
        size_col = config.get('size_column')
        title = config.get('title', 'Scatter Plot')
        
        if not x_col or not y_col:
            raise ValueError("X and Y columns are required for scatter plot")
        
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            size=size_col,
            title=title,
            color_discrete_sequence=self.color_palette
        )
        
        self._apply_common_styling(fig)
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, config: dict):
        """Create pie chart."""
        labels_col = config.get('labels_column')
        values_col = config.get('values_column')
        title = config.get('title', 'Pie Chart')
        
        if not labels_col or not values_col:
            raise ValueError("Labels and values columns are required for pie chart")
        
        # Aggregate data for pie chart
        pie_data = df.groupby(labels_col)[values_col].sum().reset_index()
        
        fig = px.pie(
            pie_data,
            values=values_col,
            names=labels_col,
            title=title,
            color_discrete_sequence=self.color_palette
        )
        
        self._apply_common_styling(fig)
        return fig
    
    def _create_histogram(self, df: pd.DataFrame, config: dict):
        """Create histogram."""
        column = config.get('column')
        bins = config.get('bins', 20)
        title = config.get('title', 'Histogram')
        
        if not column:
            raise ValueError("Column is required for histogram")
        
        fig = px.histogram(
            df,
            x=column,
            nbins=bins,
            title=title,
            color_discrete_sequence=self.color_palette
        )
        
        self._apply_common_styling(fig)
        return fig
    
    def _create_box_plot(self, df: pd.DataFrame, config: dict):
        """Create box plot."""
        y_col = config.get('y_column')
        x_col = config.get('x_column')  # Optional grouping column
        title = config.get('title', 'Box Plot')
        
        if not y_col:
            raise ValueError("Y column is required for box plot")
        
        fig = px.box(
            df,
            y=y_col,
            x=x_col,
            title=title,
            color_discrete_sequence=self.color_palette
        )
        
        self._apply_common_styling(fig)
        return fig
    
    def _apply_common_styling(self, fig):
        """Apply common styling to all charts."""
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=12),
            title=dict(
                font=dict(size=16, color='#1f77b4'),
                x=0.5,
                xanchor='center'
            ),
            margin=dict(l=50, r=50, t=80, b=50),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Update axes styling
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='gray'
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='gray'
        )
    
    def _create_error_chart(self, error_message: str):
        """Create an error chart when chart creation fails."""
        fig = go.Figure()
        
        fig.add_annotation(
            text=f"Error creating chart:<br>{error_message}",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="red")
        )
        
        fig.update_layout(
            title="Chart Error",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
