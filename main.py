import requests

# Function to retrieve video IDs from a playlist


def get_video_ids_from_playlist(api_key, playlist_id):
    base_url = 'https://www.googleapis.com/youtube/v3/playlistItems'
    video_ids = []
    next_page_token = None

    while True:
        # Prepare request parameters
        params = {
            'part': 'snippet',
            'playlistId': playlist_id,
            'key': api_key,
            'maxResults': 50,
            'pageToken': next_page_token
        }

        # Send the request
        response = requests.get(base_url, params=params)
        data = response.json()

        # Check if response contains items
        if 'items' not in data:
            print(f"Error fetching playlist data: {data}")
            return []

        # Extract video IDs from response
        video_ids += [item['snippet']['resourceId']['videoId']
                      for item in data['items']]

        # Check if there's another page of results
        next_page_token = data.get('nextPageToken')
        if not next_page_token:
            break

    return video_ids


# Main function
def main():
    # Replace with your YouTube API key and Playlist ID
    api_key = 'YOUR_API_KEY'
    playlist_id = 'YOUR_PLAYLIST_ID'

    print(f"Fetching video IDs from playlist {playlist_id}...")

    # Call the function to get video IDs
    video_ids = get_video_ids_from_playlist(api_key, playlist_id)

    # Check if video IDs were fetched successfully
    if video_ids:
        print(f"Successfully fetched {len(video_ids)} video IDs.")
        print("Video IDs:", video_ids)
    else:
        print("No video IDs found or an error occurred.")


# Entry point of the script
if __name__ == '__main__':
    main()
