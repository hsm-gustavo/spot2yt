import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from os import getenv
from youtubesearchpython import VideosSearch
import yt_dlp
import re
import time

start = time.time()

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

while start_index < total_songs:

    track_list = list()

    for i in sp.playlist_tracks(playlist_uri, offset=start_index)["items"]:
        track = str()
        for j in i["track"]["artists"]:
            track+=j["name"]+" "
        track+="- "+i["track"]["name"]
        track_list.append(track)

    for i in track_list:
        """ results = VideosSearch(i, limit=1)
        url = results.result()["result"][0]["link"] """
        
        yt = yt_dlp.YoutubeDL({"format": "m4a/bestaudio/best", "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
        }], "quiet": True})
        yt.extract_info(f"ytsearch:{i}", download=True)

    start_index+=100

print(f"Time taken: {time.time()-start} seconds")


