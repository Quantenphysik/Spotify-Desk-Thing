import requests
import os
import json
import threading
import webbrowser
from flask import Flask, request

from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"
TOKEN_FILE = "token_data.json"

BASE_URL = "https://api.spotify.com/v1/"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

TOKEN_DATA = {}
SCOPE = "user-modify-playback-state user-read-playback-state user-library-read user-library-modify"
app = Flask(__name__)  # Flask app for callback handling

# Helper function to save token data to file
def save_token_data():
    with open(TOKEN_FILE, "w") as file:
        json.dump(TOKEN_DATA, file)

# Helper function to load token data from file
def load_token_data():
    global TOKEN_DATA
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as file:
            TOKEN_DATA = json.load(file)

# Helper function to check if the user is authenticated
def is_authenticated():
    print("Checking if authenticated")
    load_token_data()
    global TOKEN_DATA
    return bool(TOKEN_DATA.get("access_token")) and set(TOKEN_DATA.get("scope").split()) == set(SCOPE.split())

# Function to generate Spotify authentication URL
def generate_auth_url():
    scope = SCOPE
    state = "some_random_state"
    auth_url = (
        f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope={scope}&state={state}"
    )
    return auth_url

# Flask route to handle the callback
@app.route('/callback')
def callback():
    global TOKEN_DATA
    code = request.args.get("code")
    state = request.args.get("state")

    if state != "some_random_state":
        return "State mismatch error."

    # Exchange authorization code for tokens
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code == 200:
        TOKEN_DATA = response.json()
        save_token_data()
        return "Authorization successful! You can close this window."
    else:
        return f"Error: {response.json().get('error_description', 'Unknown error')}"

# Function to start Flask server in a separate thread
def start_auth_server():
    threading.Thread(target=lambda: app.run(port=8888), daemon=True).start()


# Spotify API request helper
def spotify_request(method, endpoint, data=None):
    global TOKEN_DATA
    headers = {"Authorization": f"Bearer {TOKEN_DATA.get('access_token', '')}"}

    response = getattr(requests, method)(
        BASE_URL + endpoint, headers=headers, json=data
    )

    # Refresh token if expired
    if response.status_code == 401:
        refresh_token()
        headers["Authorization"] = f"Bearer {TOKEN_DATA['access_token']}"
        response = getattr(requests, method)(
            BASE_URL + endpoint, headers=headers, json=data
        )

    return response

USER_URI = None

# Get the current user's Spotify data
def get_curr_user_data():
    global USER_URI
    response = spotify_request("get", "me")
    if response.status_code == 200:
        USER_URI = response.json()["uri"]
        print(USER_URI)

# Refresh Spotify access token
def refresh_token():
    global TOKEN_DATA
    print(TOKEN_DATA)
    if "refresh_token" not in TOKEN_DATA:
        raise Exception("No refresh token available. Please reauthenticate.")

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "refresh_token",
            "refresh_token": TOKEN_DATA["refresh_token"],
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )

    if response.status_code == 200:
        TOKEN_DATA.update(response.json())
        save_token_data()
    else:
        raise Exception("Failed to refresh token.")


# Playback control functions
def skip_song():
    response = spotify_request("post", "me/player/next")
    try:
        json_data = response.json()
        print("Error Skipping song:", json_data)
    except ValueError:
        print("Skip successful")


def skip_back():
    response = spotify_request("post", "me/player/previous")
    try:
        json_data = response.json()
        print("Error Skipping Back song:", json_data)
    except ValueError:
        print("Skip Back successful")


def play_song():
    response = spotify_request("put", "me/player/play")
    try:
        json_data = response.json()
        print("Error Playing song:", json_data)
    except ValueError:
        print("Play successful")


def pause_song():
    response = spotify_request("put", "me/player/pause")
    try:
        json_data = response.json()
        print("Error pausing song:", json_data)
    except ValueError:
        print("Pause successful")


def toggle_shuffle(state):
    response = spotify_request("put", f"me/player/shuffle?state={state}")
    try:
        json_data = response.json()
        print(f"Error toggling shuffle to {state}:", json_data)
    except ValueError:
        print(f"Toggling shuffle to {state} successful")


# Get the currently playing track
def get_current_track():
    response = spotify_request("get", "me/player/currently-playing")
    if response.status_code == 200:
        return response.json()
    return None

# Check if Spotify is currently playing
def is_playing():
    current_track = get_current_track()
    if current_track:
        return current_track["is_playing"]
    return False

# Check if Spotify is currently shuffled
def is_shuffled():
    if spotify_request("get", "me/player", data=None).status_code == 204:
        return False
    if spotify_request("get", "me/player", data=None).json()["shuffle_state"]:
        return True
    return False

# Check if the current track is liked
def is_liked():
    return spotify_request("get", f"me/tracks/contains?ids={get_current_track()["item"]["id"]}").json()[0]


# Add the current track to liked songs
def add_to_liked_songs():
    current_track = get_current_track()
    if current_track:
        track_id = current_track["item"]["id"]
        response = spotify_request("put", f"me/tracks?ids={track_id}")
        if response.status_code == 200:
            print("Added song to liked songs.")
        else:
            print("Error adding song to liked songs:", response.json())

# Remove the current track from liked songs
def remove_from_liked_songs():
    current_track = get_current_track()
    if current_track:
        track_id = current_track["item"]["id"]
        response = spotify_request("delete", f"me/tracks?ids={track_id}")
        if response.status_code == 200:
            print("Removed song from liked songs.")
        else:
            print("Error removing song from liked songs:", response.json())


# Download the album cover image
def download_album_cover(url, save_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"assets/{save_path}", "wb") as file:
            file.write(response.content)
    else:
        print("Error downloading album cover.")



# Function to initiate the Spotify authorization process
def authenticate_with_spotify():
    load_token_data()
    if TOKEN_DATA.get("access_token") and set(TOKEN_DATA.get("scope").split()) == set(SCOPE.split()):
       print("Already authenticated.")
    else:
        start_auth_server()  # Start Flask server to handle callback
        webbrowser.open(generate_auth_url())  # Open the auth URL in browser

