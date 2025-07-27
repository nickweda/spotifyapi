import pandas as pd
import os
import joblib

# Load Model
model_path = os.path.join(os.path.dirname(__file__), '..', 'lightgbm_model.pkl')
model = joblib.load(model_path)


# Directories
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
model_dir = os.path.join(current_dir, "model")

# Load Paths
ranking_path = os.path.join(model_dir, "nick_artist_ranking.csv")
freq_path = os.path.join(model_dir, "nick_artist_freq.csv")
genres_path = os.path.join(model_dir, "nick_artist_genres.txt")

# Load the CSVs
ranking = pd.read_csv(ranking_path, index_col=0).squeeze()
freq = pd.read_csv(freq_path, index_col=0).squeeze()

# Load the genre list
with open(genres_path, "r") as f:
    genres = [line.strip() for line in f.readlines()]


# Use - https://open.spotify.com/track/3hUxzQpSfdDqwM3ZTFQY0K?si=f293d678602c4803
def get_prediction(track_url):
    import pandas as pd
    from datetime import datetime
    from spotipy import Spotify
    from spotipy.oauth2 import SpotifyClientCredentials

    # Set up Spotify API (.env file)
    sp = Spotify(auth_manager=SpotifyClientCredentials())

    # Extract Spotify track ID
    track_id = track_url.split("/")[-1].split("?")[0]

    # Retrieve Spotify data
    track_info = sp.track(track_id)
    artist_id = track_info['artists'][0]['id']
    artist = sp.artist(artist_id)

    # Extract features
    track_name = track_info['name']
    artist_name = artist['name']
    track_duration = int(track_info['duration_ms'] / 1000)
    track_popularity = track_info['popularity']
    track_explicit = int(track_info['explicit'])
    artist_popularity = artist['popularity']
    artist_follower_count = artist['followers']['total']
    genre_list = artist['genres']
    
    # Format release date
    release_date_str = track_info['album']['release_date']
    release_date_obj = datetime.strptime(release_date_str, "%Y-%m-%d")
    track_release_date = int(release_date_obj.strftime("%Y%m"))

    # Build feature dictionary
    features = {
        "track_duration": track_duration,
        "track_popularity": track_popularity,
        "track_release_date": track_release_date,
        "track_explicit": track_explicit,
        "artist_popularity": artist_popularity,
        "artist_follower_count": artist_follower_count,
        "artist_ranking": ranking.get(artist_name, 0),
        "artist_freq": freq.get(artist_name, 0),
    }

    # Add genre flags
    for g in genres:
        features[f"genre_{g.replace(' ', '_')}"] = int(g in genre_list)

    # Predict
    X = pd.DataFrame([features])
    return int(model.predict(X)[0] >= 0.5) # probability
