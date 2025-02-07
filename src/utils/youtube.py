# utils/youtube.py (excerpt)
import re
import requests
from PIL import Image
from io import BytesIO

def extract_video_id(url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu.be\/)([^&\n?]*)',
        r'(?:youtube\.com\/embed\/)([^&\n?]*)',
        r'(?:youtube\.com\/v\/)([^&\n?]*)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_thumbnail(video_id):
    url = f"http://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
    response = requests.get(url)
    if response.status_code == 404:
        url = f"http://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        response = requests.get(url)
    return Image.open(BytesIO(response.content))
