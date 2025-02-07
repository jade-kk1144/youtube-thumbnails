import streamlit as st
from components.sidebar import render_sidebar
from components.header import render_header
from pages import home, trend_analysis, comparison

def main():
    st.set_page_config(layout="wide", page_title="YouTube Thumbnail Analysis")
    
    # Initialize session state if needed
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Render sidebar
    render_sidebar()
    
    # Render header
    render_header()
    
    # Route to correct page based on selection
    if st.session_state.current_page == 'home':
        home.render()
    elif st.session_state.current_page == 'trend_analysis':
        trend_analysis.render()
    elif st.session_state.current_page == 'comparison':
        comparison.render()

if __name__ == "__main__":
    main()
