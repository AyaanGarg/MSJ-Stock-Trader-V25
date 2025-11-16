import streamlit as st
import pandas as pd
import json
import os
from openai import OpenAI
from modules.data_manager import DataManager
from modules.chart_components import ChartComponents

class DataChatbot:
    """AI chatbot for natural language data queries."""
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "default_key"))
        self.data_manager = DataManager()
        self.chart_components = ChartComponents()
    
    def render_chat_interface(self):
        """Render the main chat interface."""
        df = st.session_state.current_dataset
        
        st.markdown("💬 Ask questions about your data in natural language!")
        st.markdown("*Examples: 'Show me sales by region', 'What's the average revenue?', 'Create a bar chart of categories'*")
        
        # Chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f"**You:** {message['content']}")
                else:
                    st.markdown(f"**AI:** {message['content']}")
                    
                    # Display chart if present
                    if 'chart' in message:
                        st.plotly_chart(message['chart'], use_container_width=True)
                    
                    # Display data if present
                    if 'data' in message:
                        st.dataframe(message['data'], use_container_width=True)
                
                st.markdown("---")
        
        # Chat input
        user_input = st.chat_input("Ask a question about your data...")
        
        if user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Process the query
            with st.spinner("Analyzing your question..."):
                response = self._process_query(user_input, df)
            
            # Add AI response to history
            st.session_state.chat_history.append(response)
            
            st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
    
    def _process_query(self, query: str, df: pd.DataFrame) -> dict:
        """Process natural language query and return response."""
        try:
            # Get data context
            data_context = self._get_data_context(df)
            
            # Create system prompt
            system_prompt = f"""You are a data analysis assistant. Analyze the user's query and provide appropriate responses.

Dataset Information:
{data_context}

Based on the user's query, determine the best response type:
1. "data_query" - for statistical questions, filtering, or data exploration
2. "visualization" - for requests to create charts or visualizations
3. "general" - for general questions about the data

Respond in JSON format with:
{{
    "response_type": "data_query|visualization|general",
    "analysis": "explanation of what you found",
    "action": {{
        "type": "filter|aggregate|visualize|info",
        "parameters": {{relevant parameters based on query}}
    }}
}}

For visualizations, include chart configuration in the action parameters.
For data queries, include filtering or aggregation parameters.
"""
            
            # Get AI response
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                response_format={"type": "json_object"}
            )
            
            ai_response = json.loads(response.choices[0].message.content)
            
            # Execute the action
            result = self._execute_action(ai_response, df)
            
            return result
            
        except Exception as e:
            return {
                'role': 'assistant',
                'content': f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question."
            }
    
    def _get_data_context(self, df: pd.DataFrame) -> str:
        """Generate context about the dataset."""
        numeric_cols = self.data_manager.get_numeric_columns(df)
        categorical_cols = self.data_manager.get_categorical_columns(df)
        
        context = f"""
Dataset: {len(df)} rows, {len(df.columns)} columns

Numeric columns: {', '.join(numeric_cols)}
Categorical columns: {', '.join(categorical_cols)}

Sample data (first 3 rows):
{df.head(3).to_string()}
"""
        return context
    
    def _execute_action(self, ai_response: dict, df: pd.DataFrame) -> dict:
        """Execute the action determined by AI."""
        response_type = ai_response.get('response_type')
        analysis = ai_response.get('analysis', '')
        action = ai_response.get('action', {})
        
        result = {
            'role': 'assistant',
            'content': analysis
        }
        
        try:
            if response_type == 'visualization':
                # Create visualization
                chart = self._create_chart_from_action(action, df)
                if chart:
                    result['chart'] = chart
            
            elif response_type == 'data_query':
                # Execute data query
                data_result = self._execute_data_query(action, df)
                if data_result is not None:
                    result['data'] = data_result
            
        except Exception as e:
            result['content'] += f"\n\nNote: I encountered an issue executing the action: {str(e)}"
        
        return result
    
    def _create_chart_from_action(self, action: dict, df: pd.DataFrame):
        """Create chart based on AI action parameters."""
        params = action.get('parameters', {})
        chart_type = params.get('chart_type', 'Bar Chart')
        
        # Map AI chart types to our chart types
        chart_type_mapping = {
            'bar': 'Bar Chart',
            'line': 'Line Chart',
            'scatter': 'Scatter Plot',
            'pie': 'Pie Chart',
            'histogram': 'Histogram',
            'box': 'Box Plot'
        }
        
        # Normalize chart type
        for key, value in chart_type_mapping.items():
            if key in chart_type.lower():
                chart_type = value
                break
        
        # Create chart configuration
        config = {
            'title': params.get('title', 'Generated Chart')
        }
        
        # Configure based on chart type
        if chart_type in ['Bar Chart', 'Line Chart']:
            config['x_column'] = params.get('x_column', df.columns[0])
            config['y_column'] = params.get('y_column', self.data_manager.get_numeric_columns(df)[0])
            config['color_column'] = params.get('color_column')
        
        elif chart_type == 'Scatter Plot':
            numeric_cols = self.data_manager.get_numeric_columns(df)
            config['x_column'] = params.get('x_column', numeric_cols[0] if len(numeric_cols) > 0 else df.columns[0])
            config['y_column'] = params.get('y_column', numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])
            config['color_column'] = params.get('color_column')
        
        elif chart_type == 'Pie Chart':
            categorical_cols = self.data_manager.get_categorical_columns(df)
            numeric_cols = self.data_manager.get_numeric_columns(df)
            config['labels_column'] = params.get('labels_column', categorical_cols[0] if categorical_cols else df.columns[0])
            config['values_column'] = params.get('values_column', numeric_cols[0] if numeric_cols else df.columns[1])
        
        elif chart_type == 'Histogram':
            numeric_cols = self.data_manager.get_numeric_columns(df)
            config['column'] = params.get('column', numeric_cols[0] if numeric_cols else df.columns[0])
            config['bins'] = params.get('bins', 20)
        
        # Create and return chart
        return self.chart_components.create_chart(chart_type, df, config)
    
    def _execute_data_query(self, action: dict, df: pd.DataFrame):
        """Execute data query action."""
        action_type = action.get('type')
        params = action.get('parameters', {})
        
        if action_type == 'filter':
            # Apply filters
            filters = params.get('filters', {})
            return self.data_manager.filter_dataframe(df, filters)
        
        elif action_type == 'aggregate':
            # Perform aggregation
            group_by = params.get('group_by')
            agg_column = params.get('agg_column')
            agg_function = params.get('agg_function', 'mean')
            
            if group_by and agg_column:
                return self.data_manager.aggregate_data(df, group_by, agg_column, agg_function)
        
        elif action_type == 'info':
            # Return basic statistics
            column = params.get('column')
            if column and column in df.columns:
                stats = self.data_manager.get_column_stats(df, column)
                return pd.DataFrame([stats])
            else:
                return df.describe()
        
        return None
