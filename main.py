from pprint import pprint
from flask import Flask, jsonify, request
from notion_client import Client
import requests
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
from mistralai import Mistral

from ai_strategy import AIProcessor, MistralStrategy


# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)


# Load API keys
NOTION_API_KEY = os.getenv('NOTION_API_KEY')

# Initialize the Notion client
notion = Client(auth=NOTION_API_KEY)

# Define your parent page ID
# Replace with your parent page's Notion ID
parent_page_id = "118d3dc2-9328-805c-b056-ea4201a8dfc9"


def get_ai_strategy():
    return MistralStrategy(api_key=os.getenv("MISTRAL_API_KEY"), model="mistral-large-latest")
    # For ChatGPT:
    # return ChatGPTStrategy(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo")


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


def get_youtube_playlist_details(playlist_id, api_key):
    url = 'https://youtube.googleapis.com/youtube/v3/playlists'
    params = {
        'part': 'snippet',
        'id': playlist_id,
        'key': api_key
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            playlist_title = data['items'][0]['snippet']['title']
            return playlist_title
        else:
            return None
    else:
        print(f"Error: {response.status_code}")
        return None


def create_notion_page(parent_id, title, content):
    # Function to split content into chunks of max 2000 characters
    def split_content(text, max_length=2000):
        words = text.split()
        chunks = []
        current_chunk = []

        for word in words:
            if len(' '.join(current_chunk + [word])) <= max_length:
                current_chunk.append(word)
            else:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    # Split the content into chunks
    content_chunks = split_content(content)

    # Prepare the children blocks
    children = []
    for chunk in content_chunks:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": chunk,
                        },
                    }
                ]
            },
        })

    # Create the page with multiple paragraph blocks
    response = notion.pages.create(
        parent={"type": "page_id", "page_id": parent_id},
        properties={
            "title": [
                {
                    "type": "text",
                    "text": {"content": title},
                }
            ]
        },
        children=children,
    )
    return response
# Example function to create the main page (playlist) and subpages (summaries of each video)


def create_playlist_page_in_notion(playlist_title, video_summaries):
    # Create the main playlist page
    main_page = create_notion_page(
        parent_page_id, playlist_title, "This page contains summaries of videos in the playlist.")

    # Create subpages for each video summary under the main page
    for video in video_summaries:
        video_title = video['title']
        video_summary = video['summary']  # Summarized content for this video
        create_notion_page(main_page["id"], video_title, video_summary)


@app.route('/api/playlist_transcripts', methods=['GET'])
def playlist_transcripts():
    playlist_id = request.args.get('playlist_id')
    api_key = os.getenv('API_KEY')
    action_flag = request.args.get('action')

    if not playlist_id or not api_key or not action_flag:
        return jsonify({"error": "Missing playlist_id, API key, or action flag"}), 400

    # Get the playlist title
    playlist_title = get_youtube_playlist_details(playlist_id, api_key)

    if not playlist_title:
        return jsonify({"error": "Failed to fetch playlist title"}), 500

    # Get the video details including titles and IDs
    videos = get_youtube_playlist_items(playlist_id, api_key)

    if videos is None or len(videos) < 2:
        return jsonify({"error": "Not enough videos in the playlist or failed to fetch video IDs"}), 500

    # Prepare a list to hold video summaries
    video_summaries = []

    # Get transcripts for the first two videos
    for video in videos[:1]:  # Fetch the first two videos
        video_id = video['id']
        title = video['title']
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_transcript = " ".join([entry['text'] for entry in transcript])
        except Exception as e:
            video_summaries.append({
                'video_id': video_id,
                'video_title': title,
                'ai_summary': "Failed to fetch transcript"
            })
            continue  # Skip to the next video if transcript fetch fails

        # Choose the AI provider strategy based on environment variable or hard-coded selection
        strategy = get_ai_strategy()
        ai_processor = AIProcessor(strategy)

        # Prepare the prompt based on the action flag
        if action_flag == 'summarize':
            prompt = f"Please summarize the following transcript for a Notion page:\n\n{full_transcript}"
        elif action_flag == 'enrich':
            prompt = f"Please enrich the following transcript with further details for a Notion page. Mark all details you added as bold, so one can distinguish between original and added content:\n\n{full_transcript}"
        else:
            return jsonify({"error": "Invalid action flag. Use 'summarize' or 'enrich'."}), 400

        # Process the transcript with the chosen AI provider
        ai_response = ai_processor.process(prompt)

        # Extract the content from the AI response object
        ai_content = ai_response.choices[0].message.content

        # Append the summary to the video_summaries list
        video_summaries.append({
            'video_id': video_id,
            'video_title': title,
            'ai_summary': ai_content
        })

    # Return the result as JSON
    return jsonify({
        'playlist_title': playlist_title,
        'video_summaries': video_summaries
    })


# Example function to integrate AI-summarized content into Notion
def process_playlist_and_write_to_notion(playlist_id, action_flag):
    # Get the playlist details from your API (replace with your API endpoint)
    api_url = f"http://localhost:5000/api/playlist_transcripts?playlist_id={playlist_id}&action={action_flag}"
    response = requests.get(api_url)

    if response.status_code != 200:
        print(f"Error fetching playlist transcripts: {response.status_code}")
        return

    # Parse the JSON response from the API
    playlist_data = response.json()
    playlist_title = playlist_data.get(
        'playlist_title')  # The name of the playlist
    video_summaries = playlist_data.get(
        'video_summaries', [])  # Updated to match new structure

    # Prepare video summaries from the API response
    formatted_summaries = []
    for video_summary in video_summaries:
        video_title = video_summary.get('video_title')
        # Summarized content from the AI
        ai_summary = video_summary.get('ai_summary')
        if ai_summary:
            formatted_summaries.append({
                'title': video_title,
                'summary': ai_summary
            })

    # Create the playlist page and subpages in Notion
    create_playlist_page_in_notion(playlist_title, formatted_summaries)

# REST API endpoint to trigger the Notion page creation process


@app.route('/api/notion_playlist', methods=['POST'])
def notion_playlist():
    try:
        # Get data from the request
        data = request.get_json()
        playlist_id = data.get('playlist_id')
        action_flag = data.get('action_flag')

        # Validate parameters
        if not playlist_id or not action_flag:
            return jsonify({"error": "Missing playlist_id or action_flag"}), 400

        # Process playlist and create Notion pages
        process_playlist_and_write_to_notion(playlist_id, action_flag)

        return jsonify({"message": "Notion pages created successfully"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
