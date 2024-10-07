import requests
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()


def get_youtube_playlist_items(playlist_id, api_key):
    url = f'https://youtube.googleapis.com/youtube/v3/playlistItems'
    params = {
        'part': 'snippet,contentDetails',
        'maxResults': 50,  # You can increase this if you want to retrieve more items per request
        'playlistId': playlist_id,
        'key': api_key
    }

    video_ids = []  # List to hold all video IDs

    while True:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

            # Extract video IDs from the items
            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            # Check if there are more pages of results
            if 'nextPageToken' in data:
                params['pageToken'] = data['nextPageToken']  # Get next page
            else:
                break  # No more pages, exit the loop
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    return video_ids  # Return the list of video IDs


if __name__ == "__main__":
    # API_KEY = os.getenv('API_KEY')
    # PLAYLIST_ID = 'PLJwa8GA7pXCWAnIeTQyw_mvy1L7ryxxPH'

    # video_ids = get_youtube_playlist_items(PLAYLIST_ID, API_KEY)

    # if video_ids:
    #     print(video_ids)  # Print the list of video IDs
    script = YouTubeTranscriptApi.get_transcript("Gg1L-sBIxnY")
    print(script)
