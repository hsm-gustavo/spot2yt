import re
import time
from os import getenv, chdir, makedirs
import logging
import requests.exceptions
import urllib3.exceptions
from tqdm import tqdm
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp

load_dotenv()

logging.basicConfig(filename="download_log.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%Y %H:%M:%S")

def authenticate_spotify():
    client_id = getenv("CLIENT_ID")
    client_secret = getenv("CLIENT_SECRET")
    
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_playlist_uri():
    try:
        user_playlist = input("Enter the playlist URL: ")
        is_playlist = re.match(r"http(?:s?):\/\/(?:www\.)?open\.spotify\.com\/playlist\/[\w]*\?si\=[\w]*", user_playlist)
        if is_playlist is None:
            raise Exception("Invalid URL")
        print("Valid URL")
        uri_match = re.search(r'[\w]{22}(?=\?)', user_playlist).group(0)
        return f"spotify:playlist:{uri_match}"
    except Exception as e:
        print(e)
        exit()

def create_yt_downloader():
    return yt_dlp.YoutubeDL({"format": "m4a/bestaudio/best", "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
        }], "quiet": True,
        "no_warnings": True,
        "progress_hooks": [lambda d: logging.info(f" Downloaded '{d['filename'].replace('.m4a', '')}'") if d['status'] == 'finished' else None]})

def get_track_list(sp, playlist_uri):
    start_index = 0
    total_songs = sp.playlist(playlist_uri)["tracks"]["total"]
    
    track_list = list()
    
    while start_index < total_songs:
        for i in sp.playlist_tracks(playlist_uri, offset=start_index)["items"]:
            track = str()
            for j in i["track"]["artists"]:
                track+=j["name"]+" "
            track+="- "+i["track"]["name"]
            track_list.append(track)

        start_index+=100
    
    return track_list

def download_tracks(yt, track_list):
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

def main():
    sp = authenticate_spotify()
    playlist_uri = get_playlist_uri()
    makedirs("songs", exist_ok=True)
    chdir("songs")
    yt = create_yt_downloader()
    track_list = get_track_list(sp, playlist_uri)
    download_tracks(yt, track_list)
    print("A log file has been created in the current directory.")

if __name__ == "__main__":
    main()