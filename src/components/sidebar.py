import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.title("Navigation")
        
        if st.button("Home"):
            st.session_state.current_page = 'home'
        
        if st.button("Trend Analysis"):
            st.session_state.current_page = 'trend_analysis'
            
        if st.button("Comparison"):
            st.session_state.current_page = 'comparison'
        
        st.divider()
        
        with st.expander("Settings"):
            st.slider("Analysis Depth", 0, 100, 50)
            st.checkbox("Enable Advanced Features")
