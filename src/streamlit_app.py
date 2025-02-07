# src/streamlit_app.py
import streamlit as st
from components.sidebar import show_sidebar
from components.main_display import show_main_display

def main():
    # Configure the page
    st.set_page_config(
        page_title="YouTube Thumbnail Analysis",
        page_icon="🎥",
        layout="wide"
    )

    # Get sidebar state
    sidebar_state = show_sidebar()
    
    # Show main display with sidebar state
    show_main_display(sidebar_state)

if __name__ == "__main__":
    main()