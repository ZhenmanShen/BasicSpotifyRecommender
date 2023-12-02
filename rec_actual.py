import pandas as pd
import random as rand

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from sklearn.metrics.pairwise import cosine_similarity

tracks = pd.read_csv("tracks_features.csv")
tracks['main_artist'] = tracks['artists'].str.split(',').str[0].str.strip("['']")
tracks = tracks[["id", "name", "main_artist", "key", "loudness", "speechiness", "acousticness", "instrumentalness", "tempo", "danceability"]]

SPOTIPY_CLIENT_ID = '9e6da8e7a7434b409e7c30ad4091e88d'      # Change to your ID
SPOTIPY_CLIENT_SECRET = 'ef0ba456de6f49ecbb364a0fa8e0f18e'  # Change to your Secret ID
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Create a Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope='user-read-playback-state,user-modify-playback-state,playlist-modify-private'))

def create_playlist_and_add_tracks(playlist_name, track_ids):
    # Create a new private playlist
    playlist = sp.user_playlist_create(sp.me()['id'], playlist_name, public=False)

    # Add the tracks to the playlistPop
    sp.playlist_add_items(playlist['id'], track_ids)

def play_track(track_id):
    devices = sp.devices()
    if not devices['devices']:
        print("No active devices found.")
        return

    print("Now playing:", idv_song["name"], "-", idv_song["main_artist"])
    sp.start_playback(uris=['spotify:track:' + track_id])

val = 11
def recommend_similar_songs(user_preferences, tracks_dataset, sim):
    global val
    # Extract features from the tracks dataset
    track_features = tracks_dataset.iloc[:, 3:10]

    # Compute cosine similarity between user preferences and track features
    similarities = cosine_similarity([user_preferences], track_features)

    tracks_dataset['similarity_score'] = similarities.flatten()

    tracks_dataset.sort_values(by='similarity_score', ascending=False, inplace = True)

    top = tracks_dataset.head(int(len(tracks_dataset) * (10/val)))
    similar_tracks = top.copy()
    print(len(similar_tracks))

    # Print the number of similar tracks found
    print(f"Number of similar tracks above the threshold: {len(similar_tracks)}")

    val += 1
    return similar_tracks


playlist_name = "My Recommended Playlist"
playlist_tracks = []

# Count Variables
count = 0

while True:

    #Variables
    sim = True

    print("ITERATION", count)
    print("There are", len(tracks), "songs")

    rand_idx = rand.randint(0, len(tracks) - 1)
    idv_song = tracks.iloc[rand_idx]
    # idv_song["energy"],idv_song["valence"]
    song_data = [idv_song["key"], idv_song["loudness"], idv_song["speechiness"],idv_song["acousticness"],
                 idv_song["instrumentalness"], idv_song["tempo"], idv_song["danceability"]]

    play_track(idv_song["id"])

    like = input("Do you like this song? (y/n): ").lower()

    if like == "y":
        sim = True
        sim_tracks = recommend_similar_songs(song_data, tracks, sim)

        sim_tracks.reset_index(drop = True, inplace = True)

        tracks = sim_tracks.copy()
        count += 1

    if count == 16:
        tracks.sort_values(by='similarity_score', ascending=False, inplace = True)

        for i in range(0, 10):
            selected_row = tracks.iloc[i]
            playlist_tracks.append(selected_row["id"])

        create_playlist_and_add_tracks(playlist_name, playlist_tracks)
        print(f"Playlist '{playlist_name}' created with {len(playlist_tracks)} songs.")
        sp.pause_playback()
        print("Exiting.")
        break