# Project structure:
'''
YT-IMG-APP/
│
├── .devcontainer/
│   ├── devcontainer.json    # Development container configuration
│   └── Dockerfile          # Custom Dockerfile for development
│
├── .streamlit/
│   └── config.toml         # Streamlit configuration
│
├── src/                    # Source code directory
│   ├── components/         # UI Components
│   │   ├── __init__.py
│   │   ├── sidebar.py
│   │   ├── header.py
│   │   └── analysis_panels.py
│   │
│   ├── utils/             # Utility functions
│   │   ├── __init__.py
│   │   ├── youtube.py
│   │   ├── image_analysis.py
│   │   └── data_storage.py
│   │
│   ├── pages/            # Different pages/sections
│   │   ├── __init__.py
│   │   ├── home.py
│   │   ├── trend_analysis.py
│   │   └── comparison.py
│   │
│   └── streamlit_app.py   # Main application file
│
├── requirements.txt        # Python dependencies
└── README.md              # Project documentation
'''

# .devcontainer/devcontainer.json
{
    "name": "Streamlit Development",
    "dockerFile": "Dockerfile",
    "forwardPorts": [8501],
    "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python",
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "python.formatting.provider": "black"
    },
    "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-azuretools.vscode-docker"
    ],
    "postCreateCommand": "pip install -r requirements.txt"
}

# .devcontainer/Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    tesseract-ocr \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# .streamlit/config.toml
[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
address = "0.0.0.0"

# requirements.txt
streamlit>=1.24.0
pillow>=9.0.0
numpy>=1.21.0
scikit-learn>=1.0.0
opencv-python>=4.5.0
face_recognition>=1.3.0
pytesseract>=0.3.8
matplotlib>=3.4.0
seaborn>=0.11.0
requests>=2.26.0

# README.md
'''
# YouTube Thumbnail Analysis App

## Development Setup

1. Open in GitHub Codespaces or local VS Code with Dev Containers
2. The development container will automatically:
   - Set up Python environment
   - Install required dependencies
   - Configure VS Code extensions
   - Forward port 8501 for Streamlit

3. Run the app:
```bash
streamlit run src/streamlit_app.py
```

## Project Structure

- `src/components/`: UI components
- `src/utils/`: Utility functions
- `src/pages/`: App pages/sections
- `src/streamlit_app.py`: Main application

## Adding New Features

1. Create new components in `src/components/`
2. Add utility functions in `src/utils/`
3. Create new pages in `src/pages/`
4. Update main app in `src/streamlit_app.py`
'''