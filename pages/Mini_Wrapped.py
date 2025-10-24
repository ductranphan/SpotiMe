import streamlit as st
from Main import sp


user = sp.current_user()

top_tracks_short = sp.current_user_top_tracks(limit=20, offset=0, time_range="short_term")
top_tracks_medium = sp.current_user_top_tracks(limit=20, offset=0, time_range="medium_term")
top_tracks_long = sp.current_user_top_tracks(limit=20, offset=0, time_range="long_term")

top_artists_short = sp.current_user_top_artists(limit=20, offset=0, time_range="short_term")
top_artists_medium = sp.current_user_top_artists(limit=20, offset=0, time_range="medium_term")
top_artists_long = sp.current_user_top_artists(limit=20, offset=0, time_range="long_term")


def get_track_ids(time_frame):
    track_ids = []
    for song in time_frame.get('items'):
        track_ids.append(song['id'])
    return track_ids

def get_artists_ids(time_frame):
    artists_id = []
    for song in time_frame.get("items", []):  
        artists_id.append(song["id"])
    return artists_id

def get_user_id():
    return sp.current_user()["id"]

def create_playlist(user_id, name, public = True, description = "Created by Mini Wrap"):
    pl = sp.user_playlist_create(user = user_id, name = name, public = public, description = description)
    return pl["id"]

def add_tracks_to_playlist(playlist_id, track_ids):
    for i in range (0, len(track_ids), 50):
        sp.playlist_add_items(playlist_id, track_ids[i:i+50])

def ms_to_mmss(ms):
    if ms is None:
        return None
    s = ms // 1000
    m, s = divmod(s, 60)
    return f"{m}:{s:02d}"

def chunks(lst, n =20):
    for i in range (0, len(lst), n):
        yield lst[i:i+n]

def main():
    st.set_page_config(layout="wide")
    st.title ("Top Tracks/Artists 🔥")
    st.divider(width= "stretch")

    if user.get("images"):
        st.sidebar.image(user['images'][0]['url'], width=250)
    st.sidebar.markdown(f"Username: {user['display_name']}")
    st.sidebar.write(f"Followers: {user['followers']['total']}")
    st.sidebar.markdown(f"[Open Profile]({user['external_urls']['spotify']})")

    st.subheader("Select a timeframe for your Mini Wrapped")
    choice = st.radio("Timeframe", ["1 month", "6 months", "12 months"], index = 0)

    if choice.startswith("1 month"):
        track_ids = get_track_ids(top_tracks_short)
        artists_ids = get_artists_ids(top_artists_short)

    elif choice.startswith("6 months"):
        track_ids = get_track_ids(top_tracks_medium)
        artists_ids = get_artists_ids(top_artists_medium)

    elif choice.startswith("12 months"):
        track_ids = get_track_ids(top_tracks_long)
        artists_ids = get_artists_ids(top_artists_long)

    artists = []
    tracks = []
    
    for chunk in chunks(artists_ids, 20):
        res = sp.artists(chunk)
        artists.extend(res.get("artists", []))

    for chunk in chunks(track_ids, 20):
        res = sp.tracks(chunk)
        tracks.extend(res.get("tracks", []))

    top_track, top_artist = st.columns(2)

    with top_track: 
        left, right = st.columns([1,1] ,vertical_alignment="bottom")  
        with left:
            st.subheader("\nTop Tracks 🎵")

        with right:
            if st.button("Create Playlist 🟢ᯤ"):
                try:
                    if not track_ids:
                        st.warning("No tracks to add")
                    else:
                        user_id = get_user_id()
                        pl_name = f"Top Tracks - {choice} by SpotiMe"
                        pl_id = create_playlist(user_id, pl_name, public = True, description = "Top tracks from {choice} timeframe, created by SpotiMe")
                        add_tracks_to_playlist(pl_id, track_ids)
                        st.success(f"Playlist created: {pl_name}")
                        st.markdown(f"[Open playlist in Spotify](https://open.spotify.com/playlist/{pl_id})")
                except Exception as e:
                    st.error(f"Failed to create playlist: {e}")

        for track in tracks: 
            if not track:
                continue  
            img = (track.get("album", {}).get("images") or [{}])[0].get("url")
            name = track.get("name", "Unknown album")
            artist_names = ", ".join([artist["name"] for artist in track.get("artists", [])]) or "Unknown Artist"
            release = track.get("album", {}).get("release_date") or "Unknown date"
            duration_ms = track.get("duration_ms", "Unknown duration")
            url = track.get("external_urls",{}).get("spotify", "#")
            cols = st.columns([1,3])
            with cols[0]:
                if img and isinstance(img, str) and img.startswith("http"):
                    st.image(img, width=200)
                else:
                    st.write("No image available")
            duration = ms_to_mmss(duration_ms)
            with cols[1]:
                st.markdown(f"**{name}**  \nBy **{artist_names}** \nDuration: {duration}")
                st.caption(f"Released: {release}")
                st.markdown(f"[Open in Spotify]({url})")


    with top_artist: 
        st.subheader("\n Top Artists 🧑‍🎤")

        for artist in artists: 
            if not artist:
                continue  
            img = (artist.get("images") or [{}])[0].get("url")
            name = artist.get("name", "Unknown artist")
            genres = artist.get("genres", "Unknown genre")
            popularity = artist.get("popularity" , "Unknown popularity")
            url = artist.get("external_urls",{}).get("spotify", "#")
            cols = st.columns([1,3])
            with cols[0]:
                if img and isinstance(img, str) and img.startswith("http"):
                    st.image(img, width=200)
                else:
                    st.write("No image available")
            with cols[1]:
                st.markdown(f"**{name}** \nGenres: {genres}")
                st.caption(f"Popularity: {popularity}")
                st.markdown(f"[Open in Spotify]({url})")
    

if __name__ == "__main__":
    main()



