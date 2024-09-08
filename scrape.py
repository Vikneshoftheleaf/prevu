import json
from googleapiclient.discovery import build
from datetime import datetime, timezone
from dateutil import parser
import isodate


def parse_duration(duration):
    # Parse the ISO 8601 duration
    parsed_duration = isodate.parse_duration(duration)
    
    # Extract minutes and seconds
    total_seconds = int(parsed_duration.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    
    return f"{minutes}:{seconds}"



# Function to format view count
def format_views(view_count):
    view_count = int(view_count)
    if view_count >= 1_000_000_000:
        return f"{view_count / 1_000_000_000:.1f}B"
    elif view_count >= 1_000_000:
        return f"{view_count / 1_000_000:.1f}M"
    elif view_count >= 1_000:
        return f"{view_count / 1_000:.1f}K"
    else:
        return str(view_count)


# Function to format published date
def format_published_at(published_at):
    published_date = parser.parse(published_at)
    now = datetime.now(timezone.utc)
    delta = now - published_date

    if delta.days >= 365:
        years = delta.days // 365
        return f"{years} years ago" if years > 1 else "1 year ago"
    elif delta.days >= 30:
        months = delta.days // 30
        return f"{months} months ago" if months > 1 else "1 month ago"
    elif delta.days >= 1:
        return f"{delta.days} days ago" if delta.days > 1 else "1 day ago"
    else:
        hours = delta.seconds // 3600
        if hours >= 1:
            return f"{hours} hours ago" if hours > 1 else "1 hour ago"
        else:
            minutes = delta.seconds // 60
            return f"{minutes} minutes ago" if minutes > 1 else "1 minute ago"

# Set up the YouTube Data API client
def get_youtube_data(api_key, search_query, max_results=10):
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Make a search request
    search_response = youtube.search().list(
        q=search_query,
        part='snippet',
        type='video',  # Fetch only videos, not channels or playlists
        maxResults=max_results
    ).execute()

    # Store results in a list
    video_data_list = []
    for item in search_response.get('items', []):
        video_data = {
            'video_id': item['id']['videoId'],
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'thumbnail_url': item['snippet']['thumbnails']['high']['url'],
            'channel_title': item['snippet']['channelTitle'],
            'published_at': format_published_at(item['snippet']['publishedAt']),
            "views": format_views(item['statistics']['viewCount']),
            "duration" : parse_duration(item['contentDetails']['duration'])
        }
        video_data_list.append(video_data)

    return video_data_list

# Function to save data to a JSON file
def save_to_json(data, filename="videos.json"):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Example Usage
API_KEY = 'AIzaSyDjYqKDb0CfwYiMrV0O4bm114EJOgi2tV0'
search_query = 'Python programming tutorials'
video_data_list = get_youtube_data(API_KEY, search_query)

# Save the video data to a JSON file
save_to_json(video_data_list)

print(f"Data saved to videos.json")
