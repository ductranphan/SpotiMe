# SpotiMe
A personalized Spotify analytics dashboard built with Python, Streamlit, and Spotipy that visualizes your listening habits, top tracks, and favorite artists.
The app connects directly to the Spotify Web API and stores user ratings locally using JSON, allowing users to rate albums or songs and revisit their past favorites.

✨ Features
- Top Tracks & Artists — View your most-played songs and artists over 1 month, 6 months, or 1 year
- Audio Stats Dashboard — See average song duration, popularity, and more
- User Ratings (JSON): Rate albums or tracks and save ratings persistently
- Playlist Generator — Instantly create a Spotify playlist of your top tracks
- Streamlit Frontend — Easy-to-deploy interactive web app with modern UI
- Ratings persist locally for the logged in user. Cloud demo is stateless

🛠️ Technologies Used
- Python 3
- Streamlit (frontend web framework)
- Spotipy (Spotify Web API wrapper)
- Pandas for data manipulation
- JSON storage for user ratings and local state management

🚀 Future Improvements
- Integrate ReccoBeats API for richer audio features
- Ratings can save online using FastAPI + database running on Render / Railway
