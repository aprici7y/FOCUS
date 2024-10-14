# YouTube Transcript Summarizer

This project provides a YouTube Transcript Summarizer, with a backend Flask API to process transcripts and an Electron-based frontend for managing API keys and submitting playlists or transcripts for summarization. The application supports different summarization actions (summarize, enrich, simplify) and integrates with Obsidian for note management.

## Features

- **Electron Frontend**: A user-friendly interface to manage API keys and submit requests to the backend.
- **Flask Backend API**: Processes YouTube playlists or transcripts and provides summaries.
- **Database & Key Management**: Stores API keys securely using SQLite and Keytar.
- **Supports Summarization Options**: Summarize, enrich, or simplify video transcripts.
- **Obsidian Integration**: Stores generated summaries in an Obsidian vault.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: Electron (JavaScript)
- **Database**: SQLite (for API keys)
- **API Key Management**: Keytar (secure storage of API keys)
- **YouTube Transcript API**: For fetching video transcripts
- **Mistral AI**: For summarizing and processing transcripts
- **Obsidian**: Optional integration for storing summaries locally

## Requirements

- **Backend**:

  - Python 3.x
  - Flask
  - Mistral AI Key
  - YouTube API Key
  - Obsidian Vault (if using Obsidian integration)

- **Frontend**:
  - Node.js
  - Electron
  - SQLite
  - Keytar

## Getting Started

### 1. Backend Setup

#### a) Clone the repository

```bash
git clone https://github.com/aprici7y/summarizer.git
cd your-repo/backend
```

#### b) Install backend dependencies

```bash
pip install -r requirements.txt
```

#### c) Run the Flask API

```bash
python main.py
```

The API will be available at `http://localhost:5000`.

### 2. Frontend Setup

#### a) Navigate to the frontend directory

```bash
cd ../frontend
```

#### b) Install frontend dependencies

```bash
npm install
```

#### c) Run the Electron app

```bash
npm start
```

This will launch the Electron application for managing API keys and submitting requests.

## Application Structure

### Backend (Flask)

- **Flask API**: Handles requests for summarizing YouTube playlists or transcripts.
- **Endpoints**:
  - `/api/playlist_transcripts`: Summarizes a YouTube playlist.
  - `/api/summarize`: Processes and stores summaries in Obsidian.
  - `/api/process_transcript`: Processes and summarizes individual transcripts.

### Frontend (Electron)

- **Electron App**: Provides a user interface to input playlists, manage API keys, and configure settings.
- **SQLite & Keytar**: For securely managing API keys locally.
- **Main Files**:
  - `main.js`: Main Electron script that creates windows, handles database initialization, and processes API key management.
  - `preload.js`: Securely exposes specific APIs to the renderer process.
  - `index.html`: Frontend UI for interacting with the app.

### API Key Management

- **Key Storage**: API keys are stored securely using Keytar and a SQLite database.
- **Database**: A SQLite database is used to keep track of key names and services.
- **IPC Handlers**:
  - `save-api-keys`: Saves the API keys securely.
  - `get-api-keys`: Retrieves stored API keys from Keytar.
  - `submit-playlist`: Submits a playlist for summarization.
  - `submit-transcript`: Submits a transcript for summarization.

## How to Use

### 1. Managing API Keys

- Open the Electron app.
- Go to **Settings**.
- Enter the API keys for YouTube, Mistral, and Obsidian (if applicable), and click **Save**. The keys are securely stored using Keytar.

### 2. Summarizing Playlists or Transcripts

- Enter the YouTube playlist ID and select the action (`summarize`, `enrich`, or `simplify`).
- Click **Submit** to send the request to the backend.
- Summaries will be saved either in your Obsidian vault or processed and returned via the API.

## Development

### Backend

- To run the backend API server, navigate to the backend directory and run `python app.py`.
- You can modify API endpoints or integrate additional services as needed.

### Frontend

- For frontend development, modify the Electron app and run `npm start` to test changes.
- You can add more features, such as advanced settings or integrations, by extending `main.js` or `index.html`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you encounter any bugs or have suggestions for new features.

---

This README covers both backend and frontend parts, setup, API usage, and development instructions.
