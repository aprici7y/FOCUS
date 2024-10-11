from flask import Flask, jsonify, request
import requests
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
from mistralai import Mistral


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# client = OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY"),
# )
api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"
client = Mistral(api_key=api_key)


# Function to get YouTube playlist items


def get_youtube_playlist_items(playlist_id, api_key):
    url = 'https://youtube.googleapis.com/youtube/v3/playlistItems'
    params = {
        'part': 'snippet,contentDetails',
        'maxResults': 50,
        'playlistId': playlist_id,
        'key': api_key
    }

    videos = []

    while True:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                title = item['snippet']['title']
                videos.append({'id': video_id, 'title': title})

            if 'nextPageToken' in data:
                params['pageToken'] = data['nextPageToken']
            else:
                break
        else:
            print(f"Error: {response.status_code}")
            return None

    return videos

# Endpoint to get video IDs from a YouTube playlist


@app.route('/api/playlist', methods=['GET'])
def playlist():
    playlist_id = request.args.get('playlist_id')
    api_key = os.getenv('API_KEY')

    if not playlist_id or not api_key:
        return jsonify({"error": "Missing playlist_id or API key"}), 400

    videos = get_youtube_playlist_items(playlist_id, api_key)

    if videos is None:
        return jsonify({"error": "Failed to fetch video IDs"}), 500

    return jsonify(videos)

# Endpoint to get transcript of a video


@app.route('/api/transcript', methods=['GET'])
def transcript():
    video_id = request.args.get('video_id')

    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400

    try:
        script = YouTubeTranscriptApi.get_transcript(video_id)
        return jsonify(script)
    except Exception as e:
        print(f"Error retrieving transcript: {e}")
        return jsonify({"error": "Failed to fetch transcript"}), 500

# New endpoint to get transcripts of the first two videos from a playlist


@app.route('/api/playlist_transcripts', methods=['GET'])
def playlist_transcripts():
    playlist_id = request.args.get('playlist_id')
    api_key = os.getenv('API_KEY')
    # Get the action flag (summarize or enrich)
    action_flag = request.args.get('action')

    if not playlist_id or not api_key or not action_flag:
        return jsonify({"error": "Missing playlist_id, API key, or action flag"}), 400

    # Get the video details including titles and IDs
    videos = get_youtube_playlist_items(playlist_id, api_key)

    if videos is None or len(videos) < 2:
        return jsonify({"error": "Not enough videos in the playlist or failed to fetch video IDs"}), 500

    # Step 1: Get transcripts for the first two videos
    transcripts = {}
    for video in videos[:1]:
        video_id = video['id']
        title = video['title']
        try:
            # Fetch the transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            # Concatenate the text for each entry in the transcript
            full_transcript = " ".join([entry['text'] for entry in transcript])

            # Store the transcript with the video title
            transcripts[video_id] = {
                'title': title,
                'transcript': full_transcript
            }

        except Exception as e:
            print(f"Error retrieving transcript for {video_id}: {e}")
            transcripts[video_id] = {
                'title': title,
                'error': "Failed to fetch transcript"
            }

    # Step 2: Process each transcript with ChatGPT
    for video_id, data in transcripts.items():
        if 'transcript' in data:  # Only process videos that have transcripts
            full_transcript = data['transcript']
            # Prepare the prompt for ChatGPT based on action flag
            if action_flag == 'summarize':
                prompt = f"Please summarize the following transcript for a Notion page:\n\n{full_transcript}"
            elif action_flag == 'enrich':
                prompt = f"Please enrich the following transcript with further details for a Notion page:\n\n{full_transcript}"
            else:
                return jsonify({"error": "Invalid action flag. Use 'summarize' or 'enrich'."}), 400

            try:
                # # Call ChatGPT API
                # response = client.chat.completions.create(
                #     model="gpt-3.5-turbo",
                #     messages=[{"role": "user", "content": prompt}]
                # )
                # chatgpt_response = response['choices'][0]['message']['content']

                # # Store ChatGPT response
                # transcripts[video_id]['chatgpt_response'] = chatgpt_response

                chat_response = client.chat.complete(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ]
                )
                print(chat_response)
                transcripts[video_id]['chatgpt_response'] = chat_response
            except Exception as e:
                print(f"Error processing with ChatGPT for {video_id}: {e}")
                transcripts[video_id]['chatgpt_response'] = {
                    "error": "Failed to process with ChatGPT"
                }

    return jsonify("ok")


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
