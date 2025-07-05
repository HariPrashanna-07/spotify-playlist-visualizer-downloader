import streamlit as st
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import yt_dlp
import os
import zipfile

# App configs
st.set_page_config(page_title="Spotify MP3 Downloader", page_icon="🎧", layout="centered")

SPOTIFY_CLIENT_ID = "43d310460ad64d7cb03e5260ddcdc822"
SPOTIFY_CLIENT_SECRET = "a3206155529440b5adb69f46e4f91f65"

def fetch_playlist_info(playlist_url):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))

    playlist_id = playlist_url.split("/")[-1].split("?")[0]
    playlist = sp.playlist(playlist_id)
    name = playlist['name']
    owner = playlist['owner']['display_name']
    total = playlist['tracks']['total']
    return name, owner, total, sp, playlist_id


def download_songs(sp, playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'default_search': 'ytsearch1',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    download_log = []
    for item in tracks:
        track = item['track']
        name = track['name']
        artist = track['artists'][0]['name']
        query = f"{name} {artist}"
        status = f"🔄 {query}"
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([query])
            download_log.append(f"✅ {query}")
        except Exception as e:
            download_log.append(f"❌ {query} — {e}")

    # Zip downloaded MP3s
    zip_path = "playlist.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in os.listdir("downloads"):
            zipf.write(os.path.join("downloads", file), arcname=file)

    return zip_path, download_log


# 🌟 UI Starts Here
st.markdown("<h1 style='text-align: center; color: #1DB954;'>Spotify Playlist to MP3 Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Paste any public playlist URL, and we’ll download it for you!</p>", unsafe_allow_html=True)

url = st.text_input("🎵 Enter your Spotify Playlist URL")

if st.button("🚀 Start Download", use_container_width=True):
    if not url.strip():
        st.error("Please paste a valid playlist URL.")
    else:
        with st.spinner("Fetching playlist info..."):
            try:
                name, owner, total, sp, playlist_id = fetch_playlist_info(url)
                st.success(f"📂 Playlist: {name} by {owner} ({total} tracks)")
            except:
                st.error("Failed to fetch playlist. Is the URL correct?")
                st.stop()

        with st.spinner("Downloading songs..."):
            zip_file, logs = download_songs(sp, playlist_id)

        with st.expander("📋 Download Log"):
            for line in logs:
                st.markdown(f"- {line}")

        st.success("✅ All done! Download your zip file below:")
        with open(zip_file, "rb") as z:
            st.download_button(
                label="⬇️ Download Playlist (ZIP)",
                data=z,
                file_name="playlist.zip",
                mime="application/zip",
                use_container_width=True
            )

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 12px;'>Built with ❤️ using Streamlit, Spotipy & yt-dlp</p>", unsafe_allow_html=True)
