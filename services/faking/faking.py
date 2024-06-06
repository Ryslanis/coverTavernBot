import random
import os
from pytube import YouTube, Search
from moviepy.editor import AudioFileClip

import settings
from config import *
from services.database import session
from services.database.coverService import Covers
from settings import RATING_INDICATOR, SPLITTER, STOP_WORDS, MUST_WORDS
from ui.sentences import CHANNEL_RATING, _
from utils import utils


def check_if_youtube_covers(bot, song_name):
    result = get_random_covers_from_youtube(bot, song_name, check=True)
    return result

def get_random_covers_from_youtube(bot, song_name, check=False, fake_cover=None):
    artist = song_name.split(SPLITTER)[0]
    song = song_name.split(SPLITTER)[1]

    try:
        folder = 'services/faking/downloads'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Extract the song name from the message
        query = song_name + ' кавер акустика cover acoustic'

        # Search for covers on YouTube
        youtube_search = Search(query)
        videos = youtube_search.results
        # Download four covers
        youtubes = []

        i = 1
        cover_count = random.randint(settings.MIN_COVER_PARTICIPANTS, settings.MAX_COVER_PARTICIPANTS)

        for video in videos:
            if song.lower() not in video.title.lower():
                continue
            if not any(word in video.title.lower() for word in MUST_WORDS):
                continue
            if any(stop_word in video.title.lower() for stop_word in STOP_WORDS):
                continue

            min_seconds = 140
            max_seconds = 220

            if video.length > max_seconds or video.length < min_seconds:
                continue

            video_url = f'https://www.youtube.com/watch?v={video.video_id}'
            youtube_video = YouTube(video_url)
            youtubes.append(youtube_video)

        min_covers_on_song = 6
        if check and len(youtubes) >= min_covers_on_song:
            return True
        elif check:
            return False

        if len(youtubes) >= cover_count:
            covers = []
            for number in range(1, cover_count+1):
                random_index = random.randint(0, len(youtubes) - 1)
                random_cover = youtubes.pop(random_index)
                try:
                    random_cover.streams.first().download(output_path=folder, filename=f'{i}.mp4')
                    covers.append(f'{folder}/{i}.mp4')
                    i += 1
                except Exception as e:
                    print(f"An error has occurred: {str(e)}")

            # Convert covers to MP3 and randomly cut them
            for cover in covers:
                audio = AudioFileClip(cover)
                start_time = random.randint(8, 15)
                end_time = start_time + random.randint(settings.MIN_DURATION, settings.MAX_DURATION)
                audio = audio.subclip(start_time, end_time)
                output_file = cover.replace('.mp4', '.mp3')
                audio.write_audiofile(output_file)

            for cover in covers:
                os.remove(cover)
            if len(os.listdir(folder)) == cover_count:
                fake_cover.status = settings.FAKE

                bot.send_message(GROUP_ID, _(CHANNEL_RATING, 'en') % (fake_cover.id, RATING_INDICATOR, song_name, utils.level_to_word(4)))
            else:
                fake_cover.status = 'error'
            session.commit()
            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")