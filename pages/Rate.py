import streamlit as st
from pages import Mini_Wrapped
import spotipy
from Main import sp
import json, os
import Main

album_rating_file = Main.album_rating_file
track_rating_file = Main.track_rating_file

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

def save_track_rating(data:dict):
    try:
        with open(track_rating_file, "w") as f:
            json.dump(data, f , indent = 2)
    except Exception as e:
        st.error(f"Failed to save ratings: {e}")

def save_album_rating(data: dict):
    try:
        with open(album_rating_file, "w") as f:
            json.dump(data, f, indent = 2)
    except Exception as e:
        st.error(f"Failed to save ratings: {e}")

def get_user_track_rating(ratings: dict, user_id: str, track_id: str):
    return (ratings.get(user_id) or {}).get(track_id)

def get_user_album_rating(ratings: dict, user_id: str, album_id: str):
    return (ratings.get(user_id) or {}).get(album_id)

def set_user_track_rating(ratings: dict, user_id:str, track_id: str, rating: int):
    user_block = ratings.get(user_id, {})
    if rating == 0:
        user_block.pop(track_id, None)
    else:
        user_block[track_id] = int(rating)

    if user_block:
        ratings[user_id] = user_block
    else:
        ratings.pop(user_id, None)

    save_track_rating(ratings)

def set_user_album_rating(ratings: dict, user_id: str, album_id: str, rating: int):
    user_block = ratings.get(user_id, {})
    if rating == 0:
        user_block.pop(album_id, None)
    else:
        user_block[album_id] = int(rating)

    if user_block:
        ratings[user_id] = user_block
    else:
        ratings.pop(user_id, None)

    save_album_rating(ratings)

def handle_album_rating_change(album_id: str, user_id: str, ratings: dict, max_rating: int, slider_key: str):
    new_val = int(st.session_state[slider_key])
    user_block = ratings.get(user_id, {})
    if new_val == 0:
        user_block.pop(album_id, None)
        st.toast("Rating deleted ❌")
    else:
        user_block[album_id] = new_val
        st.toast(f"Saved: {new_val}/{max_rating}")
    if user_block:
        ratings[user_id] = user_block
    else:
        ratings.pop(user_id, None)
    save_album_rating(ratings)

def handle_track_rating_change(track_id: str, user_id: str, ratings: dict, max_rating: int, slider_key: str):
    new_val = int(st.session_state[slider_key])
    user_block = ratings.get(user_id, {})
    if new_val == 0:
        user_block.pop(track_id, None)
        st.toast("Rating deleted ❌")
    else:
        user_block[track_id] = new_val
        st.toast(f"Saved: {new_val}/{max_rating}")
    if user_block:
        ratings[user_id] = user_block
    else:
        ratings.pop(user_id, None)
    save_track_rating(ratings)

user = sp.current_user()

def main():
    st.set_page_config(layout="wide")
    st.title ("Rate/Search 🔍")
    st.write ("- Search and have your own rating of tracks and albums (artists not available yet... 😔)")
    st.write ("- Use the slide bar to rate and **set the bar to 0 if you want to delete** (No track/album is a 0 👍)")
    st.divider(width= "stretch")

    if user["images"]:
        st.sidebar.image(user['images'][0]['url'], width=250)
        st.sidebar.markdown(f"Username: {user['display_name']}")
        st.sidebar.write(f"Followers: {user['followers']['total']}")
        st.sidebar.markdown(f"[Open Profile]({user['external_urls']['spotify']})")

    with st.sidebar.expander("Rating settings", expanded=False):
        min_rating = st.number_input("Min rating", min_value=0, max_value=0, value=0, step=1)
        max_rating = st.number_input("Max rating", min_value=10, max_value=10, value=10, step=1)
        if min_rating >= max_rating:
            st.warning("Min rating must be less than Max rating. Using defaults 0–10.")
            min_rating, max_rating = 0, 10

    tab1, tab2, tab3= st.tabs(["Tracks" ,"Artists", "Albums"], width = "stretch")

    with tab1:
        q = st.text_input("Search tracks")
        if q:
            try:
                result = sp.search(q, type = "track", limit = 10)

                if not result or not result.get("tracks") or not result["tracks"].get("items"):
                    st.warning(f"No result found for {q}")

                else:
                    ratings = load_track_rating()
                    user_id = user.get("id") or "None"
                    items = result["tracks"]["items"]
                    for a in items:
                        img = (a.get("album", {}).get("images") or [{}])[0].get("url")
                        name = a.get("name", "Unknown name")
                        artists = ", ".join([artist["name"] for artist in a.get("artists", [])]) or "Unknown Artist"
                        release = a.get("album", {}).get("release_date") or "Unknown date"
                        duration_ms = a.get("duration_ms", "Unknown duration")
                        url = a.get("external_urls",{}).get("spotify", "#")
                        track_id = a.get("id") or "Unknown id"
                        cols = st.columns([1,3])
                        with cols[0]:
                            if img and isinstance(img, str) and img.startswith("http"):
                                st.image(img, width=200)
                            else:
                                st.write("No image available")
                        duration = Mini_Wrapped.ms_to_mmss(duration_ms)
                        with cols[1]:
                            st.markdown(f"**{name}** \n"
                                        f"Artist: {artists} \n"
                                        f"Release date: {release} \n"
                                        f"Duration: {duration} \n"
                                        f"[Open in Spotify]({url})"
                                        )
                            current_rating = get_user_track_rating(ratings, user_id, track_id)
                            slider_key = f"rating_{track_id}"
                            st.slider(
                                f"Your rating for **{name}**",
                                min_value=int(min_rating),
                                max_value=int(max_rating),
                                value=int(current_rating) if isinstance(current_rating, int) else int(min_rating),
                                step=1,
                                key=slider_key,
                                on_change=handle_track_rating_change,
                                kwargs=dict(
                                    track_id=track_id,
                                    user_id=user_id,
                                    ratings=ratings,
                                    max_rating=max_rating,
                                    slider_key=slider_key
                                )
                            )
            except spotipy.SpotifyException as e:
                st.error(f"Spotify API error: {e}")
            except Exception as e:
                st.error(f"unexpected error: {e}")


    with tab2:
        q = st.text_input("Search artists")
        if q:
            try:
                result = sp.search(q, type = "artist", limit = 10)

                if not result or not result.get("artists") or not result["artists"].get("items"):
                    st.warning(f"No result found for {q}")
                else:
                    items = result["artists"]["items"]
                    for i in items:
                        img = (i.get("images") or [{}])[0].get("url")
                        name = i.get("name", "Unknown artist")
                        genres = i.get("genres", "Unknown genre")
                        popularity = i.get("popularity" , "Unknown popularity")
                        url = i.get("external_urls",{}).get("spotify", "#")
                        cols = st.columns([1,3])
                        with cols[0]:
                            if img and isinstance(img, str) and img.startswith("http"):
                                st.image(img, width=200)
                            else:
                                st.write("No image available")
                        with cols[1]:
                            st.markdown(f"**{name}** \nGenres: {genres}")
                            st.markdown(f"Popularity score: {popularity}")
                            st.markdown(f"[Open in Spotify]({url})")
                                        
            except spotipy.SpotifyException as e:
                st.error(f"Spotify API error: {e}")
            except Exception as e:
                st.error(f"unexpected error: {e}")

    with tab3:
        q = st.text_input("Search albums")
        if q:
            try:
                result = sp.search(q, type = "album", limit = 10)

                if not result or not result.get("albums") or not result["albums"].get("items"):
                    st.warning(f"No result found for {q}")
                else:
                    ratings = load_album_rating()
                    user_id = user.get("id") or "None"
                    items = result["albums"]["items"]
                    for i in items:
                        img = (i.get("images") or [{}])[0].get("url")
                        name = i.get("name", "Unknown album")
                        artists = ", ".join([a["name"] for a in i.get("artists", [])]) or "Unknown Artist"
                        release = i.get("release_date", "Unknown Date")
                        url = i.get("external_urls",{}).get("spotify", "#")
                        album_id = i.get("id") or f"Unknown id"
                        cols = st.columns([1,3])
                        with cols[0]:
                            if img and isinstance(img, str) and img.startswith("http"):
                                st.image(img, width=200)
                            else:
                                st.write("No image available")
                        with cols[1]:
                            st.markdown(f"**{name}** \n"
                                        f"By {artists} \n"
                                        f"Release date: {release} \n"
                                        f"[Open in Spotify]({url})"
                                        )
                            current_rating = get_user_album_rating(ratings, user_id, album_id)
                            slider_key = f"rating_{album_id}"
                            st.slider(
                                f"Your rating for **{name}**",
                                min_value=int(min_rating),
                                max_value=int(max_rating),
                                value=int(current_rating) if isinstance(current_rating, int) else int(min_rating),
                                step=1,
                                key=slider_key,
                                on_change=handle_album_rating_change,
                                kwargs=dict(
                                    album_id=album_id,
                                    user_id=user_id,
                                    ratings=ratings,
                                    max_rating=max_rating,
                                    slider_key=slider_key
                                )
                            )
            except spotipy.SpotifyException as e:
                st.error(f"Spotify API error: {e}")
            except Exception as e:
                st.error(f"unexpected error: {e}")


if __name__ == "__main__":
    main()







