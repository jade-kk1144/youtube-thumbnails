# utils/youtube.py (excerpt)
import re
import requests
from PIL import Image
from io import BytesIO
from pytube import YouTube, Channel
import pandas as pd
from typing import List, Dict
import re

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



def extract_channel_id(url: str) -> str:
    """Extract channel ID from a YouTube video or channel URL."""
    if 'youtube.com/watch' in url:
        # If it's a video URL, first get the video object
        yt = YouTube(url)
        # Then get the channel URL from the video
        channel_url = yt.channel_url
    else:
        channel_url = url
    
    try:
        c = Channel(channel_url)
        return c.channel_id
    except Exception as e:
        print(f"Error extracting channel ID: {e}")
        return None

def get_channel_videos(url: str, limit: int = 10) -> List[Dict]:
    """
    Get the latest videos from a YouTube channel.
    
    Args:
        url (str): YouTube video or channel URL
        limit (int): Number of latest videos to fetch (default: 10)
    
    Returns:
        List[Dict]: List of video information dictionaries
    """
    channel_id = extract_channel_id(url)
    if not channel_id:
        return []
    
    channel = Channel(f"https://www.youtube.com/channel/{channel_id}")
    videos_data = []
    
    try:
        # Get video URLs from channel
        video_urls = list(channel.video_urls[:limit])
        
        # Fetch detailed information for each video
        for video_url in video_urls:
            try:
                yt = YouTube(video_url)
                video_info = {
                    'title': yt.title,
                    'views': yt.views,
                    'thumbnail_url': yt.thumbnail_url,
                    'video_id': yt.video_id,
                    'url': video_url,
                    'publish_date': yt.publish_date
                }
                videos_data.append(video_info)
            except Exception as e:
                print(f"Error processing video {video_url}: {e}")
                continue
                
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(videos_data)
        if not df.empty:
            df['publish_date'] = pd.to_datetime(df['publish_date'])
            df = df.sort_values('publish_date', ascending=False)
            
        return df.to_dict('records')
        
    except Exception as e:
        print(f"Error fetching channel videos: {e}")
        return []

def analyze_video_performance(videos_data: List[Dict]) -> Dict:
    """
    Analyze video performance metrics.
    
    Args:
        videos_data (List[Dict]): List of video information dictionaries
    
    Returns:
        Dict: Analysis results
    """
    if not videos_data:
        return {}
    
    df = pd.DataFrame(videos_data)
    
    analysis = {
        'total_views': df['views'].sum(),
        'average_views': df['views'].mean(),
        'most_viewed': df.loc[df['views'].idxmax()]['title'],
        'least_viewed': df.loc[df['views'].idxmin()]['title'],
        'total_videos': len(df)
    }
    
    return analysis

# Example usage in your Streamlit app:
def display_channel_analysis(url: str):
    videos = get_channel_videos(url)
    if videos:
        analysis = analyze_video_performance(videos)
        return videos, analysis
    return None, None