# Spotify Playlist Downloader

## Description

This is a simple python script that downloads all the songs in a Spotify playlist and saves them to a folder. It uses the [Spotipy](https://spotipy.readthedocs.io/en/2.22.1/) library to interact with the Spotify API.

## Usage

1. Install the required libraries using `pip install -r requirements.txt`
2. Create a Spotify app and get the client ID and client secret. You can follow the instructions [here](https://developer.spotify.com/documentation/general/guides/app-settings/#register-your-app).
3. Set the environment variables `CLIENT_ID` and `CLIENT_SECRET` to the client ID and client secret respectively.
4. Run the script using `python main.py`. It will ask you to enter the URL of the playlist you want to download. You can get the URL by right clicking on the playlist and selecting `Share > Copy link to playlist`.
5. The songs will be downloaded to a folder named `songs` in the same directory as the script.