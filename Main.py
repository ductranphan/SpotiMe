# from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
import json

album_rating_file = "user_album_ratings.json"
track_rating_file = "user_track_ratings.json"

# load_dotenv(override = True)

# for k in ("SPOTIPY_CLIENT_ID","SPOTIPY_CLIENT_SECRET","SPOTIPY_REDIRECT_URI"):
#     os.environ.pop(k, None)

# CLIENT_ID = os.getenv("CLIENT_ID")
# CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# REDIRECT_URI = os.getenv("REDIRECT_URI") 

# SCOPE = "user-top-read user-read-private playlist-modify-private playlist-modify-public"

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=st.secrets["SPOTIPY_CLIENT_ID"],
        client_secret=st.secrets["SPOTIPY_CLIENT_SECRET"],
        redirect_uri=st.secrets["SPOTIPY_REDIRECT_URI"],
        scope=st.secrets["SPOTIFY_SCOPES"],
        cache_handler=CacheFileHandler(),
        show_dialog=False,    
    )
)

user = sp.current_user()

def load_track_rating():
    if os.path.exists(track_rating_file):
        try:
            with open(track_rating_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def load_album_rating():
    if os.path.exists(album_rating_file):
        try:
            with open(album_rating_file, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

all_album_ratings = load_album_rating()
all_track_ratings = load_track_rating()
user_id = user.get("id") or "anon"
my_album_rating = all_album_ratings.get(user_id, {})
my_track_rating = all_track_ratings.get(user_id, {})


album_ids = list(my_album_rating.keys())
track_ids = list(my_track_rating.keys())

def chunks(lst, n =20):
    for i in range (0, len(lst), n):
        yield lst[i:i+n]

def main():
    page_bg_img = """
    <style>
    [data-testid="stAppViewContainer"] {
    }
    </style>
    """

    st.markdown(page_bg_img, unsafe_allow_html=True)

    st.set_page_config(page_title = "SpotiMe", page_icon = "🎧", layout="wide")
    st.title("SpotiMe 🎧")
    st.write("Please use the sidebar to navigate through the app 🧭")
    st.write("- **Main** page allows provide information for the app and allows user to see rated tracks and albums 💪")
    st.write("- **Rate** page allows user to navigate through albums/tracks/artists and user are able to have their own rating of tracks and albums 😊")
    st.write("- **Mini_Wrapped** page serves as a Spoitfy Wrapped for users' (display top tracks/artists) and allows users their Wraps in 3 different time frame ℹ️")
    st.write("- **Statistics** page allows a deeper dive into users' Mini Wrapped information 🎯")
    st.divider(width= "stretch")
    col1, col2 = st.columns(2)

    if user.get("images"):
        st.sidebar.image(user['images'][0]['url'], width=250)
    st.sidebar.markdown(f"Username: {user['display_name']}")
    st.sidebar.write(f"Followers: {user['followers']['total']}")
    st.sidebar.markdown(f"[Open Profile]({user['external_urls']['spotify']})")
 
    albums_info = []
    albums_info = [a for a in albums_info if isinstance(a, dict)]

    tracks_info = []
    tracks_info = [a for a in tracks_info if isinstance(a,dict)]

    for chunk in chunks(album_ids, 20):
        res = sp.albums(chunk)
        albums_info.extend(res.get("albums", []))

    for chunk in chunks(track_ids, 20):
        res = sp.tracks(chunk)
        tracks_info.extend(res.get("tracks", []))

    with col1:
        st.subheader("Your Rated Albums 👑")
        
        if not my_album_rating:
            st.write("No album rated. Go to the Search section to rate ✅")

        sort_by = st.selectbox("Sort by", ["Rating (high→low)", "Rating (low→high)", "Album name (A→Z)"], key="album_sort")
        if sort_by == "Rating (high→low)":
            albums_info.sort(key=lambda a: my_album_rating.get(a["id"], 0), reverse=True)
        elif sort_by == "Rating (low→high)":
            albums_info.sort(key=lambda a: my_album_rating.get(a["id"], 0))
        else:
            albums_info.sort(key=lambda a: (a.get("name") or "").lower())

        for i in range (0, len(albums_info) , 2):
            row = st.columns(2)
            for c, a in zip(row, albums_info[i:i+2]):
                if not a:
                    continue  
                img = a["images"][0].get("url") or "Unavailable image"
                name = a.get("name", "Unknown album")
                artists = ", ".join([artist["name"] for artist in a.get("artists", [])]) or "Unknown Artist"
                release = a.get("release_date", "Unknown Date")
                url = a.get("external_urls",{}).get("spotify", "#")
                album_id = a.get("id") or "anon"
                rating = my_album_rating.get(album_id, 0)

                with c:
                    if img:
                        st.image(img, width = 200)
                    st.markdown(f"**{name}**  \nBy {artists}")
                    st.caption(f"Released: {release}")
                    st.markdown(f"**Rating: {rating}/10**")
                    st.markdown(f"[Open in Spotify]({url})")

    with col2:
        st.subheader("Your Rated Tracks ⭐")
        if not my_track_rating:
            st.write("No track rated. Go to the Search section to rate ✅")

        sort_by = st.selectbox("Sort by", ["Rating (high→low)", "Rating (low→high)", "Track name (A→Z)"], key="track_sort")
        if sort_by == "Rating (high→low)":
            tracks_info.sort(key=lambda a: my_track_rating.get(a["id"], 0), reverse=True)
        elif sort_by == "Rating (low→high)":
            tracks_info.sort(key=lambda a: my_track_rating.get(a["id"], 0))
        else:
            tracks_info.sort(key=lambda a: (a.get("name") or "").lower())

        for i in range (0, len(tracks_info),2):
            row = st.columns(2)
            for c, a in zip(row, tracks_info[i:i+2]):
                if not a:
                    continue
                album_img = a.get("album", {}).get("images", []) or "Unavailable image"
                img = album_img[0]["url"] if album_img else None
                name = a.get("name", "Unknown name")
                artists = ", ".join([artist["name"] for artist in a.get("artists", [])]) or "Unknown Artist"
                release = a.get("album", {}).get("release_date") or "Unknown date"
                url = a.get("external_urls",{}).get("spotify", "#")
                track_id = a.get("id") or "Unknown id"
                rating = my_track_rating.get(track_id, 0)
                with c:
                    if img:
                        st.image(img, width = 200)
                    st.markdown(f"**{name}**  \nBy {artists}")
                    st.caption(f"Released: {release}")
                    st.markdown(f"**Rating: {rating}/10**")
                    st.markdown(f"[Open in Spotify]({url})")

if __name__ == "__main__":
    main()

