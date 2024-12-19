import subprocess
from flask import Flask, request, jsonify
import requests
from ytmusicapi import YTMusic
import os
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Start the CORS server to avoid CORS and rate limit issues
def start_cors_server():
    # Navigate to the CORS server directory and run 'npm install && npm start'
    subprocess.Popen(["npm", "install"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.Popen(["npm", "start"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Start the SpotDL web server
def start_spotdl_web_server():
    subprocess.Popen(["spotdl", "web"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Initialize the CORS server and SpotDL web server
start_cors_server()
start_spotdl_web_server()

# Initialize YTMusic API
ytmusic = YTMusic()

@app.route('/search', methods=['GET'])
def search_song():
    # Step 1: Get the YouTube video ID
    video_id = request.args.get('video_id', '')
    if not video_id:
        return jsonify({"error": "video_id parameter is required!"}), 400

    try:
        # Step 2: Get title and artist using YTMusic API
        video_details = ytmusic.get_song(video_id)
        if not video_details or 'videoDetails' not in video_details:
            return jsonify({"error": "Failed to fetch video details!"}), 404

        title = video_details['videoDetails']['title']
        artist = video_details['videoDetails']['author']

        # Step 3: Create a search query and get song_id from SpotDL
        search_query = f"{title} {artist}"
        spotdl_url = f"http://localhost:8800/api/songs/search?query={search_query}"
        spotdl_response = requests.get(spotdl_url)
        spotdl_response.raise_for_status()

        songs = spotdl_response.json()
        if songs and isinstance(songs, list) and 'song_id' in songs[0]:
            song_id = songs[0]['song_id']
        else:
            return jsonify({"error": "No song_id found in SpotDL response!"}), 404

        # Step 4: Request gid from FabDL API using song_id
        fabdl_get_url = f"https://api.fabdl.com/spotify/get?url=https%3A%2F%2Fopen.spotify.com%2Ftrack%2F{song_id}"
        fabdl_get_response = requests.get(fabdl_get_url)
        fabdl_get_response.raise_for_status()

        fabdl_get_data = fabdl_get_response.json()
        if 'result' not in fabdl_get_data or 'gid' not in fabdl_get_data['result']:
            return jsonify({"error": "Failed to get gid from FabDL!"}), 404

        gid = fabdl_get_data['result']['gid']

        # Step 5: Request tid from FabDL API using gid and song_id
        fabdl_convert_url = f"https://api.fabdl.com/spotify/mp3-convert-task/{gid}/{song_id}"
        fabdl_convert_response = requests.get(fabdl_convert_url)
        fabdl_convert_response.raise_for_status()

        fabdl_convert_data = fabdl_convert_response.json()
        if 'result' not in fabdl_convert_data or 'tid' not in fabdl_convert_data['result']:
            return jsonify({"error": "Failed to get tid from FabDL!"}), 404

        tid = fabdl_convert_data['result']['tid']

        # Step 6: Get the audio URL using tid
        audio_url = f"https://api.fabdl.com/spotify/download-mp3/{tid}"

        # Return the audio URL
        return jsonify({"streamUrl": audio_url})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to connect to one of the external APIs", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
