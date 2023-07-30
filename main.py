import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests.exceptions
import urllib3.exceptions
import time
from dotenv import load_dotenv
from os import getenv
import yt_dlp
import os
import re

load_dotenv()

client_id = getenv("CLIENT_ID")
client_secret = getenv("CLIENT_SECRET")

try:
    user_playlist = input("Enter the playlist URL: ")
    is_playlist = re.match(r"http(?:s?):\/\/(?:www\.)?open\.spotify\.com\/playlist\/[\w]*\?si\=[\w]*", user_playlist)
    if is_playlist is None:
        raise Exception("Invalid URL")
    print("Valid URL")
    uri_match = re.search(r'[\w]{22}(?=\?)', user_playlist).group(0)
    playlist_uri = f"spotify:playlist:{uri_match}"
except Exception as e:
    print(e)
    exit()

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

start_index = 0
total_songs = sp.playlist(playlist_uri)["tracks"]["total"]

os.makedirs("songs", exist_ok=True)
os.chdir("songs")

yt = yt_dlp.YoutubeDL({"format": "m4a/bestaudio/best", "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
        }], "quiet": True})

while start_index < total_songs:

    track_list = list()

    for i in sp.playlist_tracks(playlist_uri, offset=start_index)["items"]:
        track = str()
        for j in i["track"]["artists"]:
            track+=j["name"]+" "
        track+="- "+i["track"]["name"]
        track_list.append(track)

    for i in track_list:
        try:
            yt.extract_info(f"ytsearch:{i} official audio", download=True)
        except yt_dlp.utils.DownloadError:
            print(f"Could not download '{i}'")
        except (requests.exceptions.ConnectionError, urllib3.exceptions.ProtocolError):
            print("Connection Error, retrying in 5 seconds...")
            time.sleep(5)
            yt.extract_info(f"ytsearch:{i} official audio", download=True)
        except Exception as e:
            print(f"Unknown Error: {e}")

    start_index+=100