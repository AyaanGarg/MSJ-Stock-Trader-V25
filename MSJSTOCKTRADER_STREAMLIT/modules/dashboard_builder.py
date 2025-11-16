import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from modules.chart_components import ChartComponents
from modules.data_manager import DataManager

class DashboardBuilder:
    """Handles dashboard building functionality."""
    
    def __init__(self):
        self.chart_components = ChartComponents()
        self.data_manager = DataManager()
    
    def render_dashboard_builder(self):
        """Render the main dashboard builder interface."""
        df = st.session_state.current_dataset
        
        # Dashboard controls
        st.subheader("⚙️ Dashboard Controls")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            dashboard_name = st.text_input("Dashboard Name", value="My Dashboard")
        
        with col2:
            if st.button("💾 Save Dashboard", type="primary"):
                self._save_dashboard(dashboard_name)
        
        with col3:
            if st.button("🗑️ Clear All Charts"):
                st.session_state.dashboard_charts = []
                st.rerun()
        
        st.markdown("---")
        
        # Chart builder section
        st.subheader("➕ Add New Chart")
        
        with st.expander("Chart Configuration", expanded=True):
            self._render_chart_builder()
        
        st.markdown("---")
        
        # Display current dashboard
        st.subheader("📊 Current Dashboard")
        
        if not st.session_state.dashboard_charts:
            st.info("No charts added yet. Create your first chart above!")
        else:
            self._render_dashboard()
    
    def _render_chart_builder(self):
        """Render the chart builder interface."""
        df = st.session_state.current_dataset
        
        col1, col2 = st.columns(2)
        
        with col1:
            chart_type = st.selectbox(
                "Chart Type",
                ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart", "Histogram", "Box Plot"]
            )
            
            # Data filters
            st.markdown("**Data Filters**")
            filters = self._render_filter_controls(df)
        
        with col2:
            # Chart configuration based on type
            chart_config = self._render_chart_config(chart_type, df)
        
        # Preview and add button
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("👁️ Preview Chart", use_container_width=True):
                try:
                    filtered_df = self.data_manager.filter_dataframe(df, filters)
                    fig = self.chart_components.create_chart(chart_type, filtered_df, chart_config)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Error creating chart: {str(e)}")
        
        with col2:
            if st.button("➕ Add to Dashboard", use_container_width=True):
                try:
                    chart_data = {
                        'type': chart_type,
                        'config': chart_config,
                        'filters': filters,
                        'id': len(st.session_state.dashboard_charts)
                    }
                    st.session_state.dashboard_charts.append(chart_data)
                    st.success("Chart added!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding chart: {str(e)}")
    
    def _render_filter_controls(self, df):
        """Render data filter controls."""
        filters = {}
        
        # Column selection for filtering
        filter_columns = st.multiselect("Filter by columns:", df.columns.tolist())
        
        for col in filter_columns:
            st.write(f"**{col}**")
            
            if pd.api.types.is_numeric_dtype(df[col]):
                # Numeric filter
                min_val, max_val = float(df[col].min()), float(df[col].max())
                filter_range = st.slider(
                    f"Range for {col}",
                    min_val, max_val, (min_val, max_val),
                    key=f"filter_{col}"
                )
                filters[col] = {'type': 'range', 'value': filter_range}
            else:
                # Categorical filter
                unique_values = df[col].unique().tolist()
                selected_values = st.multiselect(
                    f"Select {col} values:",
                    unique_values,
                    default=unique_values[:min(5, len(unique_values))],
                    key=f"filter_{col}"
                )
                filters[col] = {'type': 'select', 'value': selected_values}
        
        return filters
    
    def _render_chart_config(self, chart_type, df):
        """Render chart configuration controls."""
        config = {}
        
        numeric_cols = self.data_manager.get_numeric_columns(df)
        categorical_cols = self.data_manager.get_categorical_columns(df)
        all_cols = df.columns.tolist()
        
        if chart_type in ["Bar Chart", "Line Chart"]:
            config['x_column'] = st.selectbox("X-axis", all_cols)
            config['y_column'] = st.selectbox("Y-axis", numeric_cols)
            if categorical_cols:
                config['color_column'] = st.selectbox("Color by (optional)", [None] + categorical_cols)
            
        elif chart_type == "Scatter Plot":
            config['x_column'] = st.selectbox("X-axis", numeric_cols)
            config['y_column'] = st.selectbox("Y-axis", numeric_cols)
            config['size_column'] = st.selectbox("Size by (optional)", [None] + numeric_cols)
            if categorical_cols:
                config['color_column'] = st.selectbox("Color by (optional)", [None] + categorical_cols)
        
        elif chart_type == "Pie Chart":
            config['labels_column'] = st.selectbox("Labels", categorical_cols)
            config['values_column'] = st.selectbox("Values", numeric_cols)
        
        elif chart_type == "Histogram":
            config['column'] = st.selectbox("Column", numeric_cols)
            config['bins'] = st.slider("Number of bins", 5, 100, 20)
        
        elif chart_type == "Box Plot":
            config['y_column'] = st.selectbox("Y-axis", numeric_cols)
            if categorical_cols:
                config['x_column'] = st.selectbox("Group by (optional)", [None] + categorical_cols)
        
        # Common configurations
        config['title'] = st.text_input("Chart Title", value=f"{chart_type}")
        
        return config
    
    def _render_dashboard(self):
        """Render the complete dashboard with all charts."""
        df = st.session_state.current_dataset
        
        # Layout options
        layout = st.radio("Layout", ["Single Column", "Two Columns"], horizontal=True)
        
        if layout == "Single Column":
            for i, chart_data in enumerate(st.session_state.dashboard_charts):
                self._render_chart_with_controls(df, chart_data, i)
        else:
            # Two column layout
            for i in range(0, len(st.session_state.dashboard_charts), 2):
                col1, col2 = st.columns(2)
                
                with col1:
                    if i < len(st.session_state.dashboard_charts):
                        self._render_chart_with_controls(df, st.session_state.dashboard_charts[i], i)
                
                with col2:
                    if i + 1 < len(st.session_state.dashboard_charts):
                        self._render_chart_with_controls(df, st.session_state.dashboard_charts[i + 1], i + 1)
    
    def _render_chart_with_controls(self, df, chart_data, index):
        """Render a single chart with control buttons."""
        try:
            # Apply filters
            filtered_df = self.data_manager.filter_dataframe(df, chart_data['filters'])
            
            # Create and display chart
            fig = self.chart_components.create_chart(
                chart_data['type'], 
                filtered_df, 
                chart_data['config']
            )
            
            # Chart controls
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("**Controls**")
                if st.button("🗑️ Remove", key=f"remove_{index}"):
                    st.session_state.dashboard_charts.pop(index)
                    st.rerun()
                
                if st.button("📊 Details", key=f"details_{index}"):
                    with st.expander(f"Chart {index + 1} Details", expanded=True):
                        st.json(chart_data)
        
        except Exception as e:
            st.error(f"Error rendering chart {index + 1}: {str(e)}")
    
    def _save_dashboard(self, name):
        """Save current dashboard to session state."""
        if not st.session_state.dashboard_charts:
            st.warning("No charts to save!")
            return
        
        dashboard = {
            'name': name,
            'charts': st.session_state.dashboard_charts.copy(),
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'dataset_name': st.session_state.dataset_name
        }
        
        st.session_state.saved_dashboards.append(dashboard)
        st.success(f"Dashboard '{name}' saved successfully!")
