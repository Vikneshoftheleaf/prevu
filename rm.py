import json

def remove_duplicates_from_json(filename="videos.json"):
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

    # Write the deduplicated data back to the file
    with open(filename, 'w') as json_file:
        json.dump(unique_data, json_file, indent=4)

    print(f"Removed duplicates from {filename}")

# Example Usage
remove_duplicates_from_json()
