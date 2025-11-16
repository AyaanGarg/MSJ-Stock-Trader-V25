import pandas as pd
import streamlit as st
from typing import Optional
import io

class DataManager:
    """Handles data loading, processing, and management operations."""
    
    def __init__(self):
        pass
    
    def load_csv(self, uploaded_file) -> pd.DataFrame:
        """Load CSV file and return pandas DataFrame."""
        try:
            # Read the uploaded file
            df = pd.read_csv(uploaded_file)
            
            # Basic data cleaning
            df = self._clean_dataframe(df)
            
            return df
            
        except Exception as e:
            raise Exception(f"Failed to load CSV file: {str(e)}")
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic data cleaning operations."""
        # Remove completely empty rows
        df = df.dropna(how='all')
        
        # Convert numeric columns
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                if not numeric_series.isna().all():
                    # If more than 50% of values can be converted to numeric, convert the column
                    if (numeric_series.notna().sum() / len(df)) > 0.5:
                        df[col] = numeric_series
        
        return df
    
    def get_numeric_columns(self, df: pd.DataFrame) -> list:
        """Get list of numeric columns."""
        return df.select_dtypes(include=['number']).columns.tolist()
    
    def get_categorical_columns(self, df: pd.DataFrame) -> list:
        """Get list of categorical columns."""
        return df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def filter_dataframe(self, df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        """Apply filters to dataframe."""
        filtered_df = df.copy()
        
        for column, filter_config in filters.items():
            if column not in df.columns:
                continue
                
            filter_type = filter_config.get('type')
            filter_value = filter_config.get('value')
            
            if filter_type == 'range' and len(filter_value) == 2:
                filtered_df = filtered_df[
                    (filtered_df[column] >= filter_value[0]) & 
                    (filtered_df[column] <= filter_value[1])
                ]
            elif filter_type == 'select' and filter_value:
                filtered_df = filtered_df[filtered_df[column].isin(filter_value)]
            elif filter_type == 'text' and filter_value:
                filtered_df = filtered_df[
                    filtered_df[column].astype(str).str.contains(filter_value, case=False, na=False)
                ]
        
        return filtered_df
    
    def aggregate_data(self, df: pd.DataFrame, group_by: str, agg_column: str, agg_function: str) -> pd.DataFrame:
        """Aggregate dataframe by specified column and function."""
        try:
            if agg_function == 'count':
                result = df.groupby(group_by).size().reset_index(name='count')
            else:
                agg_funcs = {
                    'sum': 'sum',
                    'mean': 'mean',
                    'median': 'median',
                    'min': 'min',
                    'max': 'max',
                    'std': 'std'
                }
                
                if agg_function in agg_funcs:
                    result = df.groupby(group_by)[agg_column].agg(agg_funcs[agg_function]).reset_index()
                else:
                    raise ValueError(f"Unsupported aggregation function: {agg_function}")
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to aggregate data: {str(e)}")
    
    def get_column_stats(self, df: pd.DataFrame, column: str) -> dict:
        """Get basic statistics for a column."""
        if column not in df.columns:
            return {}
        
        series = df[column]
        stats = {
            'count': len(series),
            'null_count': series.isnull().sum(),
            'unique_count': series.nunique()
        }
        
        if pd.api.types.is_numeric_dtype(series):
            stats.update({
                'mean': series.mean(),
                'median': series.median(),
                'min': series.min(),
                'max': series.max(),
                'std': series.std()
            })
        else:
            stats.update({
                'most_common': series.mode().iloc[0] if not series.mode().empty else None
            })
        
        return stats
