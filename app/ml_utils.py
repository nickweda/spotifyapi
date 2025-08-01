import os
import joblib
import pandas as pd

# Base directory of the current file (app/ml_utils.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Model directory (app/model/)
model_dir = os.path.join(current_dir, "model")

# Load model
model_path = os.path.join(model_dir, "lightgbm_model.pkl")
model = joblib.load(model_path)

# Load CSVs
ranking_path = os.path.join(model_dir, "nick_artist_ranking.csv")
freq_path = os.path.join(model_dir, "nick_artist_freq.csv")
genres_path = os.path.join(model_dir, "nick_artist_genres.txt")

ranking = pd.read_csv(ranking_path, index_col=0).squeeze()
freq = pd.read_csv(freq_path, index_col=0).squeeze()

# Load genres
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
    # release_date_str = track_info['album']['release_date']
    # release_date_obj = datetime.strptime(release_date_str, "%Y-%m-%d")
    # track_release_date = int(release_date_obj.strftime("%Y%m"))

    # Format release date with flexible parsing
    release_date_str = track_info['album']['release_date']

    # Try multiple date formats to parse release_date_str
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            release_date_obj = datetime.strptime(release_date_str, fmt)
            break
        except ValueError:
            continue
    else:
        raise ValueError(f"Unrecognized date format: {release_date_str}")

    # Format to YYYYMM integer
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

    # Pass back some of the features to be rendered on HTML
    album_image_url = track_info['album']['images'][0]['url'] if track_info['album']['images'] else None
    album_name = track_info['album']['name']

    features_display = {
        "Track Name": track_name,
        "Artist Name": artist_name,
        "Album Name": album_name,
        "Artist Genres": ", ".join(genre_list) if genre_list else "None",
        "album_image_url": album_image_url
    }


    # Predict
    X = pd.DataFrame([features])
    prediction = int(model.predict(X)[0] >= 0.5)
    return prediction, features_display # probability
