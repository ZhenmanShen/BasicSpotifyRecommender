import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Enter your Spotify API credentials
client_id = 'YOUR_CLIENT_ID'
client_secret = 'YOUR_CLIENT_SECRET'

# Set up the Spotify API client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Function to get track features based on track ID
def get_track_features(track_id):
    track = sp.track(track_id)
    features = sp.audio_features([track_id])
    return {
        'name': track['name'],
        'artists': ', '.join([artist['name'] for artist in track['artists']]),
        'id': track_id,
        'features': features[0]
    }

# Example: Fetch track features using a track ID
track_id = 'YOUR_TRACK_ID'
track_data = get_track_features(track_id)
print(f"Track Name: {track_data['name']}")
print(f"Artists: {track_data['artists']}")
print(f"Track Features: {track_data['features']}")

# Function to recommend similar tracks based on features
def recommend_similar_tracks(track_id, limit=10):
    seed_track = get_track_features(track_id)
    seed_features = seed_track['features']
    track_results = sp.recommendations(seed_tracks=[track_id], limit=limit)
    similar_tracks = []
    for track in track_results['tracks']:
        similar_tracks.append({
            'name': track['name'],
            'artists': ', '.join([artist['name'] for artist in track['artists']]),
            'id': track['id']
        })
    return similar_tracks

# Example: Recommend similar tracks based on a given track ID
recommended_tracks = recommend_similar_tracks(track_id)
print("Recommended Tracks:")
for track in recommended_tracks:
    print(f"{track['name']} by {track['artists']}")
