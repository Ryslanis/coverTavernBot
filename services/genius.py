from lyricsgenius import Genius

from dotenv import load_dotenv
import os

load_dotenv()

genius = Genius(os.getenv("GENIUS_ACCESS_TOKEN"), verbose=False if os.getenv("ENVIRONMENT") == 'production' else True)


def get_lyrics_for_cover(artist_query, song_query):
    song = genius.search_song(title=song_query, artist=artist_query)
    if song:
        return song.lyrics
    else:
        return "Not found"
