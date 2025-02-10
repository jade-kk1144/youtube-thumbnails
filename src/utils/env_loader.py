import os
from dotenv import load_dotenv
import streamlit as st

def load_environment():
    """Load environment variables from .env file or streamlit secrets"""
    # Try loading from .env file first
    # load_dotenv()
    
    # Get API keys with fallbacks
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    # Check if we're running in Streamlit Cloud (which uses secrets.toml)
    # if not youtube_key and hasattr(st, 'secrets'):
        # youtube_key = st.secrets.get('YOUTUBE_API_KEY')
    # if not gemini_key and hasattr(st, 'secrets'):
        # gemini_key = st.secrets.get('GEMINI_API_KEY')
    
    if not youtube_key or not gemini_key:
        raise EnvironmentError(
            "Missing required API keys. Please set YOUTUBE_API_KEY and GEMINI_API_KEY "
            "in your .env file or Streamlit secrets."
        )
    
    return {
        'YOUTUBE_API_KEY': youtube_key,
        'GEMINI_API_KEY': gemini_key
    }