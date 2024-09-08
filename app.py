from flask import Flask, render_template, request
import json

app = Flask(__name__)

def load_and_clean_json(filename="videos.json"):
    # Read existing data from file
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    
    # Track unique video IDs to remove duplicates
    seen = set()
    unique_data = []

    for item in data:
        video_id = item.get('video_id')
        if video_id not in seen:
            unique_data.append(item)
            seen.add(video_id)

    return unique_data

def filter_videos(data, keyword):
    # Filter videos based on the keyword in the title
    filtered_data = [video for video in data if keyword.lower() in video['title'].lower()]
    return filtered_data

@app.route('/')
def index():
    keyword = request.args.get('q', '')  # Get the keyword from query parameter
    data = load_and_clean_json()
    if keyword:
        data = filter_videos(data, keyword)
    else:
        data = filter_videos(data, 'html')

    return render_template('index.html', videos=data, keyword=keyword)

if __name__ == '__main__':
    app.run(debug=True)
