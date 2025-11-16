import streamlit as st
import pandas as pd

def initialize_session_state():
    """Initialize all required session state variables."""
    
    # Current dataset
    if 'current_dataset' not in st.session_state:
        st.session_state.current_dataset = None
    
    if 'dataset_name' not in st.session_state:
        st.session_state.dataset_name = ""
    
    # Dashboard builder
    if 'dashboard_charts' not in st.session_state:
        st.session_state.dashboard_charts = []
    
    if 'current_dashboard' not in st.session_state:
        st.session_state.current_dashboard = None
    
    # Saved dashboards
    if 'saved_dashboards' not in st.session_state:
        st.session_state.saved_dashboards = []
    
    # Chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def format_price(price):
    """Format price with appropriate precision based on value."""
    if pd.isna(price) or price is None:
        return "N/A"
    
    if not isinstance(price, (int, float)):
        return str(price)
    
    # Use variable precision based on price range
    if price >= 1.0:
        return f"${price:.2f}"
    elif price >= 0.01:
        return f"${price:.4f}"
    elif price >= 0.0001:
        return f"${price:.6f}"
    else:
        return f"${price:.8f}"

def format_number(value):
    """Format numbers for display."""
    if pd.isna(value):
        return "N/A"
    
    if isinstance(value, (int, float)):
        if abs(value) >= 1000000:
            return f"{value/1000000:.1f}M"
        elif abs(value) >= 1000:
            return f"{value/1000:.1f}K"
        else:
            return f"{value:.2f}"
    
    return str(value)

def validate_dataframe(df):
    """Validate dataframe for dashboard creation."""
    if df is None or df.empty:
        return False, "Dataset is empty"
    
    if len(df.columns) < 2:
        return False, "Dataset must have at least 2 columns"
    
    return True, "Valid"

def get_sample_data():
    """Generate sample data for testing (only use if explicitly requested)."""
    # This function should only be used for testing purposes
    import numpy as np
    
    np.random.seed(42)
    
    data = {
        'Category': ['A', 'B', 'C', 'D', 'E'] * 20,
        'Value': np.random.randint(10, 100, 100),
        'Date': pd.date_range('2023-01-01', periods=100, freq='D'),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
        'Sales': np.random.randint(1000, 10000, 100)
    }
    
    return pd.DataFrame(data)

def export_dashboard_config(dashboard):
    """Export dashboard configuration as JSON."""
    import json
    
    config = {
        'name': dashboard['name'],
        'charts': dashboard['charts'],
        'created_at': dashboard['created_at'],
        'version': '1.0'
    }
    
    return json.dumps(config, indent=2)

def clean_column_name(column_name):
    """Clean column names for better display."""
    # Replace underscores with spaces and title case
    return column_name.replace('_', ' ').title()

def get_chart_suggestions(df):
    """Suggest appropriate chart types based on data characteristics."""
    suggestions = []
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    if len(numeric_cols) >= 2:
        suggestions.append("Scatter Plot - Compare two numeric variables")
    
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        suggestions.append("Bar Chart - Show numeric values by category")
        suggestions.append("Pie Chart - Show distribution of categories")
    
    if len(numeric_cols) >= 1:
        suggestions.append("Histogram - Show distribution of numeric values")
        suggestions.append("Box Plot - Show statistical summary")
    
    # Check for time series data
    date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    if date_cols and numeric_cols:
        suggestions.append("Line Chart - Show trends over time")
    
    return suggestions
