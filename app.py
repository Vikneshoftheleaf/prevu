from flask import Flask, render_template, request
import requests
from datetime import datetime, timezone
from dateutil import parser
import isodate

app = Flask(__name__)


def parse_duration(duration):
    # Parse the ISO 8601 duration
    parsed_duration = isodate.parse_duration(duration)
    
    # Extract minutes and seconds
    total_seconds = int(parsed_duration.total_seconds())
    minutes, seconds = divmod(total_seconds, 60)
    
    return f"{minutes}:{seconds}"

# Replace with your YouTube API key
YOUTUBE_API_KEY = "AIzaSyCO8M4SLI9wAFwuz7O77ho3y2GBCl2gtaw"

@app.route('/')
def index():
    search_query = request.args.get('q', 'YOUR_SEARCH_QUERY')
    
    # YouTube API URL for search
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={search_query}&type=video&key={YOUTUBE_API_KEY}&maxResults=10"
    
    response = requests.get(search_url)
    videos = response.json().get('items', [])
    
    # List to hold non-short videos
    video_data = []
    
    # Collect video IDs to check details later
    video_ids = [video['id']['videoId'] for video in videos]
    
    # Fetch video details to get content details (to filter out Shorts) and statistics (to get view count)
    video_details_url = f"https://www.googleapis.com/youtube/v3/videos?part=contentDetails,snippet,statistics&id={','.join(video_ids)}&key={YOUTUBE_API_KEY}"
    details_response = requests.get(video_details_url)
    video_details = details_response.json().get('items', [])
    
    for video in video_details:
        duration = video['contentDetails']['duration']
        
        # Filtering out Shorts (videos shorter than 60 seconds)
        if 'M' in duration or 'H' in duration:  # Check if the duration contains minutes (M) or hours (H)
            video_info = {
                "title": video['snippet']['title'],
                "thumbnail": video['snippet']['thumbnails']['high']['url'],
                "channel_title": video['snippet']['channelTitle'],
                "channel_id": video['snippet']['channelId'],
                "published_at": format_published_at(video['snippet']['publishedAt']),
                "video_id": video['id'],
                "views": format_views(video['statistics']['viewCount']),
                "duration" : parse_duration(video['contentDetails']['duration'])
            }
            
            # Get channel details (channel image)
            channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={video_info['channel_id']}&key={YOUTUBE_API_KEY}"
            channel_response = requests.get(channel_url)
            channel_info = channel_response.json().get('items', [])[0]
            video_info["channel_image"] = channel_info['snippet']['thumbnails']['default']['url']
            
            video_data.append(video_info)

            if len(video_data) >= 10:
                break

    return render_template('index.html', videos=video_data)


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


if __name__ == '__main__':
    app.run(debug=True)
