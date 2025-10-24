import pandas as pd
import streamlit as st
from Main import sp
from pages import Mini_Wrapped

user = sp.current_user()

top_tracks_short = sp.current_user_top_tracks(limit=50, offset=0, time_range="short_term")
top_tracks_medium = sp.current_user_top_tracks(limit=50, offset=0, time_range="medium_term")
top_tracks_long = sp.current_user_top_tracks(limit=50, offset=0, time_range="long_term")

top_artists_short = sp.current_user_top_artists(limit=50, offset=0, time_range="short_term")
top_artists_medium = sp.current_user_top_artists(limit=50, offset=0, time_range="medium_term")
top_artists_long = sp.current_user_top_artists(limit=50, offset=0, time_range="long_term")

def get_track_features(ids):
    try:
        meta = sp.tracks(ids, market="from_token")["tracks"]
    except Exception as e:
        print("Error {e}")
        return []

    track_list = []
    for m in meta:
        if m is None:
            continue
        track_list.append([
            m.get('name'),
            m['album']['name'],
            m['album']['artists'][0]['name'],
            m.get('duration_ms'),
            m.get('popularity'),
            m.get("album", {}).get("release_date")[:4] or "Unknown date"
        ])
    return track_list

def get_artists_features(ids):
    artist_list = []
    if isinstance(ids, list):
        try:
            meta = sp.artists(ids)["artists"]
        except Exception as e:
            print("Error fetching artists:", e)
            return []
    else:
        try:
            meta = [sp.artist(ids)]
        except Exception as e:
            print("Error fetching artist:", e)
            return []

    for m in meta:
        if not m:
            continue
        artist_image = None
        if m.get("images"):
            artist_image = m["images"][0]["url"]
        artist_list.append([
            m.get("name"),
            m.get("genres", []),
            m.get("popularity"),
            m["external_urls"]["spotify"],
            artist_image
        ])

    return artist_list

def main():

    st.title("Deeper Dive 📊")
    st.divider(width= "stretch")


    if user.get("images"):
        st.sidebar.image(user['images'][0]['url'], width=250)
    st.sidebar.markdown(f"Username: {user['display_name']}")
    st.sidebar.write(f"Followers: {user['followers']['total']}")
    st.sidebar.markdown(f"[Open Profile]({user['external_urls']['spotify']})")

    st.subheader("Select a timeframe for your Spotify Wrapped")
    choice = st.radio("Timeframe", ["1 month", "6 months", "12 months"], index = 0)

    if choice.startswith("1 month"):
        top_artists = top_artists_short
        track_ids = Mini_Wrapped.get_track_ids(top_tracks_short)
        artists_ids = Mini_Wrapped.get_artists_ids(top_artists)

    elif choice.startswith("6 months"):
        top_artists = top_artists_medium
        track_ids = Mini_Wrapped.get_track_ids(top_tracks_medium)
        artists_ids = Mini_Wrapped.get_artists_ids(top_artists)

    else:
        top_artists = top_artists_long
        track_ids = Mini_Wrapped.get_track_ids(top_tracks_long)
        artists_ids = Mini_Wrapped.get_artists_ids(top_artists)

    tracks = []
    for i in range(0, len(track_ids), 50):
        chunk = track_ids[i:i+50]
        tracks.extend(get_track_features(chunk))  

    rows_df = pd.DataFrame(tracks,columns = ['name', 'album', 'artist', 'duration_ms','popularity', 'release'])

    artists_rows = []
    for i in range(0, len(artists_ids), 50):
        chunk2 = artists_ids[i:i+50]
        artists_rows.extend(get_artists_features(chunk2))

    rows_db = pd.DataFrame(artists_rows,columns = ['name', 'genres', 'popularity', 'spotify_url', 'artist_image'])

    col1, col2 = st.columns(2)

    if len(rows_df) > 0:
        avg_duration_ms = rows_df['duration_ms'].mean()
        avg_duration_min = avg_duration_ms / 60000
        avg_track_popularity = (rows_df["popularity"]).mean()
        with col1:
            st.metric("Average track duration(min)", round(avg_duration_min, 2))
        with col2:
            score = st.slider("🎧 Average Track Popularity", min_value=0, max_value=100, value = int(round(avg_track_popularity)), step = 1)
            if score < 40:
                category = "🎵 Extremely niche — deep underground finds!"
            elif score < 65:
                category = "🧠 Niche — indie and lesser-known tracks."
            elif score < 75:
                category = "🌱 Rising — your music is getting some attention."
            elif score < 90:
                category = "🔥 Charting — trending. Your probably get your music from Tiktok"
            else:
                category = "🐑 You're a sheep"
            st.write(category)
    else: 
        st.write("Not enough data")


    if len(rows_db) > 0:
        with col2:
            avg_artist_popularity = (rows_db["popularity"]).mean()
            score = st.slider("🎧 Average Artists Popularity", min_value=0, max_value=100, value = int(round(avg_artist_popularity)), step = 1)
            if score < 40:
                category = "🎵 Extremely underground finds!"
            elif score < 65:
                category = "🧠 Niche — indie and cult favourites."
            elif score < 80:
                category = "🌱 Rising — your artists is on the up and coming."
            elif score < 90:
                category = "🔥 Charting — trending. Your artists are trending on Tiktok"
            else:
                category = "🐑 You suck"
            st.write(category)
    else:
        st.write("Not enough data")
    
    year_counts = rows_df["release"].dropna().value_counts().sort_index()
    artists = top_artists.get("items", [])
    genres= {}

    st.subheader("Top Genres 🎸")
    genres = {}  
    for artist in artists:
        for g in artist.get("genres", []):
            k = g.strip().lower()
            genres[k] = genres.get(k, 0) + 1

    if genres:
        df = pd.DataFrame(sorted(genres.items(), key=lambda x: x[1], reverse=True),
                        columns=["Genre", "Count"])

        st.bar_chart(df.set_index("Genre")["Count"].head(10))
    else:
        st.write("No genres available for your top artists.")


    st.subheader("Tracks' Release Year Distribution 📅")
    st.bar_chart(year_counts)

if __name__ == "__main__":
    main()










    



