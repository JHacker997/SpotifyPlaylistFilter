'''
Author:
    John Hacker
File:
    SpotfiyPlaylistFilter.py
Description:
    Looks at all the songs in a playlist, compares an audio feature to 
    a threshold, and adds passing songs to a different playlist.
Instructions:
    Update SpotifyClientCredentials with your username and client ID 
    and secret before running this file.
'''

# Imports
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify variables
audio_feature = 'tempo'
destination_playlist_ids = ['0z5UmdAJjMFHB6ICmJP4K5'] # Medium Run
# destination_playlist_ids = ['32HDsVlkrXHJM0B5ttipc7'] # Fast Run
source_playlist_ids = ['3DGzYDs2dl4EBz0Q50CUX9', # run
                       '37i9dQZF1DX3rxVfibe1L0', # Mood Boster
                       '0s2ZRmfiCNp3jjXRa77uTv', # Top 100 Running Songs
                       '2O4svdQzGD6NFSgr4sBy6i'] # Brookelyn Creek

# Authentication variables
clientID = open("SpotifyClientCredentials.txt").read().split()[1]
secretID = open("SpotifyClientCredentials.txt").read().split()[3]
username = open("SpotifyClientCredentials.txt").read().split()[5]
scope = 'playlist-modify-public'
redirect_uri = "http://127.0.0.1:8080/"

# Create Spotify connection
token = SpotifyOAuth(client_id=clientID,client_secret=secretID,scope=scope,
                    username=username,redirect_uri=redirect_uri)
sp = spotipy.Spotify(auth_manager=token)

for destination_playlist_id in destination_playlist_ids:
    print ("Going to: " + str(sp.user_playlist(username, destination_playlist_id)['name']))
    for source_playlist_id in source_playlist_ids:
        print ("Coming from: " + str(sp.user_playlist(username, source_playlist_id)['name']))
        # Retrieve first 100 tracks and their audio features from source playlist
        results = sp.user_playlist_tracks(username, source_playlist_id)
        tracks = results['items']
        track_uris = [x['track']['uri'] for x in tracks]
        audio_features = sp.audio_features(track_uris)

        # Retrieve remaining tracks and features in batches of at most 100
        while results['next']:
            results = sp.next(results)
            temp_tracks = results['items']
            temp_uris = [x['track']['uri'] for x in temp_tracks]
            tracks.extend(temp_tracks)
            track_uris.extend(temp_uris)
            audio_features.extend(sp.audio_features(temp_uris))
            print(len(track_uris))

        # Iterate through all found tracks
        tracks_to_add = []
        for i in range(len(track_uris)):
            # Tracks set to be added based on a feature threshold
            if audio_features[i] is not None and (audio_features[i][audio_feature] >= 140 and 
                                                  audio_features[i][audio_feature] <= 160 and 
                                                  (audio_features[i]['energy'] >= 0.75 or
                                                  sp.user_playlist(username, source_playlist_id)['name'] == "run")):
                tracks_to_add.append(track_uris[i])
                print(str(len(tracks_to_add)) + " : " + tracks[i]['track']['name'] + 
                    " : " + str(audio_features[i][audio_feature]))
            
            # Can only add songs in batches of at most 100 (choosing to cap at 99)
            if len(tracks_to_add)%100 == 99:
                sp.user_playlist_add_tracks(user=username, playlist_id=destination_playlist_id, 
                                            tracks=tracks_to_add)
                tracks_to_add = []

        # Add remaining tracks to destination playlist
        if len(tracks_to_add) > 0:
            sp.user_playlist_add_tracks(user=username, playlist_id=destination_playlist_id, 
                                        tracks=tracks_to_add)
