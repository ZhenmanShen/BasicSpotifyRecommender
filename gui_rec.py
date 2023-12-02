import pandas as pd
import random as rand

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from sklearn.metrics.pairwise import cosine_similarity

# Tkinter imports
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

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

def create_playlist_and_add_tracks(track_ids):
    playlist_name = playlist_name_var.get()
    # Create a new private playlist
    playlist = sp.user_playlist_create(sp.me()['id'], playlist_name, public=False)

    # Add the tracks to the playlistPop
    sp.playlist_add_items(playlist['id'], track_ids)

def play_track(track_id):
    devices = sp.devices()
    if not devices['devices']:
        print("No active devices found.")
        return

    sp.start_playback(uris=['spotify:track:' + track_id])
    
def recommend_similar_songs(user_preferences, tracks_dataset):
    # Global vars
    global val
    
    # Extract features from the tracks dataset
    track_features = tracks_dataset.iloc[:, 3:10]

    # Compute cosine similarity between user preferences and track features
    similarities = cosine_similarity([user_preferences], track_features)

    tracks_dataset['similarity_score'] = similarities.flatten()
    
    tracks_dataset.sort_values(by='similarity_score', ascending=False, inplace = True)
    
    top = tracks_dataset.head(int(len(tracks_dataset) * (10/val)))
    similar_tracks = top.copy()

    val += 1
    return similar_tracks

def like_song(idv_song):
    # Global vars
    global yes
    global tracks
    
    # Extract single song values
    song_data = [idv_song["key"], idv_song["loudness"], idv_song["speechiness"], idv_song["acousticness"], 
                 idv_song["instrumentalness"], idv_song["tempo"], idv_song["danceability"]]
    
    sim_tracks = recommend_similar_songs(song_data, tracks)
    sim_tracks.reset_index(drop=True, inplace=True)
    tracks = sim_tracks.copy()

    button_clicked.set(True)
    yes = True
    
def dislike_song():
    global no
    
    button_clicked.set(True)
    no = True
    

def run_rec():
    if not playlist_name_var.get():
        messagebox.showerror("Error", "Please enter a playlist name.")
        return

    
    playlist_name_label.destroy()
    playlist_name_entry.destroy()
    start_button.destroy()
    
    global yes
    global no
    global count
    global idv_song
    global playlist_tracks
    
    no = False
    yes = False

    if count < 15:
        button_clicked.set(False)
        
        rand_idx = rand.randint(0, len(tracks) - 1)
        idv_song = tracks.iloc[rand_idx]

        play_track(idv_song["id"])

        text_label_amt.config(text=f"There are {len(tracks)} songs you may like")
        text_label_q.config(text=f"Do you like {idv_song['name']} by {idv_song['main_artist']}?")

        yes_button = ttk.Button(root, text="Yes", command=lambda idv_song=idv_song: like_song(idv_song))
        yes_button.pack(side = "left",pady=10, padx = 50)

        no_button = ttk.Button(root, text="No", command= lambda: dislike_song())
        no_button.pack(side = "right",pady=10, padx = 50)
        
        # Wait for a button click before continuing
        root.wait_variable(button_clicked)
        
        # Hide the yes and no buttons
        no_button.pack_forget()
        yes_button.pack_forget()
        
        # Rerun the loop
        if no == True:
            run_rec()
        if yes == True:
            count += 1
            run_rec()
            

    else:
        tracks.sort_values(by='similarity_score', ascending=False, inplace=True)

        for i in range(0, 20):
            selected_row = tracks.iloc[i]
            playlist_tracks.append(selected_row["id"])

        create_playlist_and_add_tracks(playlist_tracks)
        sp.pause_playback()
        
        text_label_q.config(text="Here is a playlist of your top 20")
        
        exit_button = ttk.Button(root, text="Exit", command=root.destroy)
        exit_button.pack(pady=10)

# Variables
count = 0
playlist_tracks = []
yes = False
no = False
yes_button = None
no_button = None
val = 11

# GUI
root = tk.Tk()
root.title("Music Recommendation Playlist Creator")
root.geometry("500x300")

playlist_name_var = tk.StringVar()
button_clicked = tk.BooleanVar()
playlist_name_label = ttk.Label(root, text="Enter Playlist Name:")
playlist_name_label.pack(pady=10)

playlist_name_entry = ttk.Entry(root, width=30, textvariable=playlist_name_var)
playlist_name_entry.pack(pady=10)

text_label_amt = tk.Label(root, text="")
text_label_amt.pack(pady=10)

text_label_q = tk.Label(root, text="")
text_label_q.pack(pady=10)

start_button = ttk.Button(root, text="Start Recommendation", command=run_rec)
start_button.pack(pady=10)

root.mainloop()