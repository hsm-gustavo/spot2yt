import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests.exceptions
import urllib3.exceptions
import time
from tqdm import tqdm
from dotenv import load_dotenv
from os import getenv
import yt_dlp
import os
import re
import logging

load_dotenv()

logging.basicConfig(filename="download_log.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%Y %H:%M:%S")

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
        }], "quiet": True,
        "no_warnings": True,
        "progress_hooks": [lambda d: logging.info(f" Downloaded '{d['filename'].replace('.m4a', '')}'") if d['status'] == 'finished' else None]})

while start_index < total_songs:

    track_list = list()

    for i in sp.playlist_tracks(playlist_uri, offset=start_index)["items"]:
        track = str()
        for j in i["track"]["artists"]:
            track+=j["name"]+" "
        track+="- "+i["track"]["name"]
        track_list.append(track)

    for i in tqdm(track_list, desc="Downloading", unit="song"):
        try:
            yt.extract_info(f"ytsearch:{i} official audio", download=True)
        except yt_dlp.utils.DownloadError:
            logging.warning(f"Could not download '{i}'")
        except (requests.exceptions.ConnectionError, urllib3.exceptions.ProtocolError):
            logging.warning("Connection Error, retrying in 5 seconds...")
            time.sleep(5)
            yt.extract_info(f"ytsearch:{i} official audio", download=True)
        except Exception as e:
            logging.error(f"Unknown Error: {e}")

    start_index+=100

print("A log file has been created in the current directory.")