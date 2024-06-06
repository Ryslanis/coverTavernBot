import random
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from services.database.artistsService import Artists
from settings import STANDARD_ARTISTS
from utils.utils import get_language
from spotipy.exceptions import SpotifyException

load_dotenv()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                                                           client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")))

def get_preview_url(query):
    try:
        results = sp.search(q=query, limit=1, type='track')
        return results['tracks']['items'][0]['preview_url']
    except SpotifyException:
        return '-'

def get_random_song():
    users_favorite_artists = Artists.get_artists()
    users_favorite_artists = list([artist.artist_name for artist in users_favorite_artists])
    artists = users_favorite_artists + STANDARD_ARTISTS
    if artists:
        random_artist = random.choice(artists)
        random_spotify_artist = get_artist_by_name(random_artist)
        artist_songs = sp.artist_top_tracks(random_spotify_artist['id'])['tracks'] # 50 songs
        random_song = random.choice(artist_songs)
        preview = get_preview_url(random_song['artists'][0]['name'] + ' ' + random_song['name'],)
        random_song['preview_url'] = preview
        return random_song

def get_top_artists(genre, lang, page):
    language = get_language(lang)
    result = sp.search(q=f'genre:"{language} {genre}"', type='artist', limit=8, offset=page*8)
    return result['artists']['items']


def get_artist_by_name(artist):
    results = sp.search(q=artist, type='artist', limit=1)
    artist = results['artists']['items'][0]
    return artist

def get_similar_artists(spotify_id):
    results = sp.artist_related_artists(spotify_id)
    similar_artists = results['artists']
    return similar_artists[0:8]


