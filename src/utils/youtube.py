import re
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
from typing import List, Dict
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import isodate
from datetime import datetime,timezone

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

def calculate_video_metrics(video_data):
    try:
        # Validate required fields
        required_fields = ['like_count', 'view_count', 'comment_count', 'subscriber_count', 'published_date']
        if not all(field in video_data for field in required_fields):
            raise KeyError("Missing required fields in video_data")
            
        # Avoid division by zero
        if video_data['view_count'] == 0 or video_data['subscriber_count'] == 0:
            raise ValueError("View count or subscriber count cannot be zero")

        metrics = video_data.copy()  # Create a copy instead of direct reference
        
        # Calculate base metrics
        metrics.update({
            'like_ratio': (video_data['like_count'] / video_data['view_count']) * 100,
            'comment_ratio': (video_data['comment_count'] / video_data['view_count']) * 100,
            'sub_conversion': (video_data['view_count'] / video_data['subscriber_count']) * 100,
            'view_velocity': video_data['view_count'] / ((datetime.now() - datetime.strptime(video_data['published_date'], '%B %d, %Y')).days or 1)
        })

        # Calculate derived metrics
        metrics.update({
            'engagement_score': min((metrics['like_ratio'] * 20) + (metrics['comment_ratio'] * 30) + (metrics['sub_conversion'] * 0.3), 100),
            'performance': {
                'like_ratio': 'Good' if metrics['like_ratio'] > 4 else 'Average' if metrics['like_ratio'] > 1 else 'Poor',
                'comment_ratio': 'Good' if metrics['comment_ratio'] > 0.5 else 'Average' if metrics['comment_ratio'] > 0.1 else 'Poor'
            }
        })
        
        return metrics
        
    except Exception as e:
        print(f"Error calculating metrics: {str(e)}")
        return None
            

def get_video_details(video_id: str, api_key: str) -> Dict:
    """
    Get comprehensive video details using YouTube API.
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    try:
        video_response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=video_id
        ).execute()
        
        if not video_response.get('items'):
            return None
            
        video_data = video_response['items'][0]
        snippet = video_data['snippet']
        statistics = video_data['statistics']
        
        # Get channel info
        channel_response = youtube.channels().list(
            part="snippet,statistics",
            id=snippet['channelId']
        ).execute()
        channel_data = channel_response['items'][0]
        
        # Parse duration and date
        duration = isodate.parse_duration(video_data['contentDetails']['duration'])
        published_date = datetime.strptime(snippet['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
        
        return {
            'title': snippet['title'],
            'description': snippet['description'],
            'published_date': published_date.strftime("%B %d, %Y"),
            'duration': str(duration).split('.')[0],
            'view_count': int(statistics.get('viewCount', 0)),
            'like_count': int(statistics.get('likeCount', 0)),
            'comment_count': int(statistics.get('commentCount', 0)),
            'thumbnail_url': snippet['thumbnails'].get('maxres', 
                           snippet['thumbnails'].get('high', 
                           snippet['thumbnails'].get('default')))['url'],
            'channel_name': snippet['channelTitle'],
            'channel_id': snippet['channelId'],
            'channel_thumbnail': channel_data['snippet']['thumbnails']['default']['url'],
            'subscriber_count': int(channel_data['statistics'].get('subscriberCount', 0)),
            'tags': snippet.get('tags', []),
            'category_id': snippet.get('categoryId'),
            'is_live': snippet.get('liveBroadcastContent') == 'live'
        }
        
    except HttpError as e:
        print(f"YouTube API error: {e}")
        return None


def get_video_stats(channel_id, api_key):
   youtube = build('youtube', 'v3', developerKey=api_key)
   videos_request = youtube.search().list(
    part='snippet',
    channelId=channel_id,
    order='date',
    maxResults=5
    )
   videos_response = videos_request.execute()
   st.write(videos_response)
   
   # Get stats for each video
   video_stats = []
   for video in videos_response['items']:
       video_id = video['id']['videoId']
       stats_request = youtube.videos().list(
           part='statistics',
           id=video_id
       )
       stats_response = stats_request.execute()
       
       if stats_response['items']:
           stats = stats_response['items'][0]['statistics']
           video_stats.append({
               'title': video['snippet']['title'],
               'published_at': video['snippet']['publishedAt'],
               'views': int(stats.get('viewCount', 0)),
               'likes': int(stats.get('likeCount', 0)), 
               'comments': int(stats.get('commentCount', 0))
           })
   
   return pd.DataFrame(video_stats)


def analyze_video_performance(videos_data: List[Dict]) -> Dict:
    """
    Analyze video performance metrics.
    """
    if not videos_data:
        return {}
    
    df = pd.DataFrame(videos_data)
    df['publish_date'] = pd.to_datetime(df['publish_date'])
    
    analysis = {
        'total_views': df['views'].sum(),
        'average_views': df['views'].mean(),
        'most_viewed': df.loc[df['views'].idxmax()]['title'],
        'least_viewed': df.loc[df['views'].idxmin()]['title'],
        'total_videos': len(df),
        'average_likes': df['likes'].mean(),
        'average_comments': df['comments'].mean(),
        'engagement_rate': (df['likes'].sum() + df['comments'].sum()) / df['views'].sum() * 100
    }
    
    return analysis

def format_view_counts(num: int) -> str:
    """Format large numbers to K, M, B format"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)

