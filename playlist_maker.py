from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import yt_dlp
import os

# SETUP SPOTIFY
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="43d310460ad64d7cb03e5260ddcdc822",
    client_secret="a3206155529440b5adb69f46e4f91f65"
))

# Playlist URL and extract ID
playlist_url = "https://open.spotify.com/playlist/4j86KfvtuDaQ7NeJbtYMqY?si=b555c5d0f7984124"
playlist_id = playlist_url.split("/")[-1].split("?")[0]

# Get all tracks (including pagination)
tracks = []
results = sp.playlist_tracks(playlist_id)
tracks.extend(results['items'])
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

# Create download folder
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# YT-DLP Options
ydl_opts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'noplaylist': True,
    'default_search': 'ytsearch1',  # search and download top result
    'quiet': False,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# Download songs
for item in tracks:
    track = item['track']
    song_name = track['name']
    artist_name = track['artists'][0]['name']
    search_query = f"{song_name} {artist_name}"
    print(f"\n🔍 Searching & Downloading: {search_query}")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
    except Exception as e:
        print(f"❌ Failed: {search_query} — {e}")
