from tkinter import *
import threading
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import yt_dlp
import os


def download_from_spotify(playlist_url):
    try:
        status_label.config(text="Connecting to Spotify...")

        # Set up Spotipy
        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
            client_id="43d310460ad64d7cb03e5260ddcdc822",
            client_secret="a3206155529440b5adb69f46e4f91f65"
        ))

        # Extract playlist ID
        playlist_id = playlist_url.split("/")[-1].split("?")[0]

        # Fetch all tracks
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        tracks.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])

        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            'default_search': 'ytsearch1',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        for item in tracks:
            track = item['track']
            song_name = track['name']
            artist_name = track['artists'][0]['name']
            search_query = f"{song_name} {artist_name}"

            status_label.config(text=f"Downloading: {song_name} - {artist_name}")
            print(f"🎵 {search_query}")

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([search_query])
            except Exception as e:
                print(f"❌ Error: {search_query} — {e}")

        status_label.config(text="✅ All downloads complete!")

    except Exception as e:
        status_label.config(text=f"❌ Failed: {e}")


def start_download():
    url = url_entry.get().strip()
    if not url:
        status_label.config(text="⚠️ Please enter a playlist URL")
        return

    status_label.config(text="Starting download...")
    threading.Thread(target=download_from_spotify, args=(url,)).start()


# GUI Setup
root = Tk()
root.title("Spotify Playlist Downloader")

Label(root, text="Paste Spotify Playlist URL:").pack(pady=5)
url_entry = Entry(root, width=60)
url_entry.pack(pady=5)

Button(root, text="Download", command=start_download).pack(pady=10)
status_label = Label(root, text="", fg="blue")
status_label.pack()

root.mainloop()
