# utils/youtube.py (excerpt)
import re
import requests
from PIL import Image
from io import BytesIO
# from pytube import YouTube, Channel
import pandas as pd
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate

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

def get_video_details(video_id):
    """
    Get video details using YouTube API.
    
    Args:
        video_id (str): YouTube video ID
    Returns:
        dict: Video details including channel info and engagement metrics
    """
    try:
         # Build the YouTube service
        youtube = build('youtube', 'v3', developerKey = st.secrets["YOUTUBE_API_KEY"])
         # Access the API key from secrets
        video_request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        )
        video_response = video_request.execute()
        st.write(video_response)
        if not video_response.get('items'):
            st.error("Video not found")
            return None
            
        video_data = video_response['items'][0]
        snippet = video_data['snippet']
        statistics = video_data['statistics']
        
        # Get channel info
        # channel_request = youtube.channels().list(
            # part="snippet,statistics",
            # id=snippet['channelId']
        # )
        # channel_response = channel_request.execute()
        # channel_data = channel_response['items'][0]
        
        # Parse duration
        duration = isodate.parse_duration(video_data['contentDetails']['duration'])
        duration_str = str(duration).split('.')[0]  # Remove microseconds
        
        # Format date
        published_at = snippet['publishedAt']
        published_date = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = published_date.strftime("%B %d, %Y")
        
        video_details = {
            # Video info
            'title': snippet['title'],
            'description': snippet['description'],
            'published_date': formatted_date,
            'duration': duration_str,
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'thumbnail_url': snippet['thumbnails'].get('maxres', 
                            snippet['thumbnails'].get('high', 
                            snippet['thumbnails'].get('default')))['url'],
            
            # Channel info
            # 'channel_name': snippet['channelTitle'],
            # 'channel_id': snippet['channelId'],
            # 'channel_thumbnail': channel_data['snippet']['thumbnails']['default']['url'],
            # 'subscriber_count': int(channel_data['statistics'].get('subscriberCount', 0)),
            
            # Additional metadata
            'tags': snippet.get('tags', []),
            'category_id': snippet.get('categoryId'),
            'is_live': snippet.get('liveBroadcastContent') == 'live'
        }
        
        return video_details
        
    except HttpError as e:
        st.error(f"YouTube API error: {e.resp.status} - {e.content}")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def format_counts(num):
    """Format large numbers to K, M, B format"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)
