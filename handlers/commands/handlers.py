from datetime import datetime, timedelta
import random
import time

from sqlalchemy.exc import NoResultFound

from config import ADMIN_ID
from services.database import Cover, session, Settings
from services.database.coverService import Covers
from services.database.userService import Users
from services.database.voiceService import Voices
from services.faking.faking import get_random_covers_from_youtube, check_if_youtube_covers
from services.spotify import get_random_song
from ui.keyboards import get_wantings_keyboard, get_general_info_keyboard, get_genres
from ui.sentences import *
from ui.sentences import _
from utils.utils import level_to_word


def send_inline_info_panel(bot, message):
    reply_markup = get_general_info_keyboard(message.from_user.language_code)
    try:
        Users.get_user_by_id(message.from_user.id)
    except NoResultFound:
        Users.add_new_user(message.from_user.id, message.from_user.username, message.from_user.language_code)
        bot.send_message(message.chat.id, _(SUBSCRIBE, message.from_user.language_code))
    finally:
        bot.send_message(chat_id=message.chat.id, text=_(CHOOSE_OPTION, message.from_user.language_code), reply_markup=reply_markup)


def send_statistics(bot, message):
    covers_count = Covers.get_covers_count()
    users_count = Users.get_users_count()
    voices_count = Voices.get_voices_count()

    bot.send_message(message.chat.id, f"Total users: {users_count}\n"
                                      f"Total covers: {covers_count}\n"
                                      f"Total voices: {voices_count}")


def add_cover(bot, artist, song, preview_url):
    level = random.choice([0, 4])
    new_cover = Cover(artist=artist, song=song, level=level, status=WANTING,
                      targetDate=datetime.now() + timedelta(seconds=SEC_WANTING),
                      previewUrl=preview_url,
                      )

    session.add(new_cover)
    session.commit()

    post = bot.send_message(config.GROUP_ID,
                            _(COVER_ADDED_PUBLIC, 'en') % (
                                new_cover.id,
                                artist + SPLITTER + song,
                                POINT if level else FAKE_POINT,
                                level_to_word(level),
                                new_cover.previewUrl
                            ))
    new_cover.postID = post.id
    session.commit()
    return new_cover


def set_random_fake_cover(bot):
    randomization = session.query(Settings).filter_by(id=1).one()
    randomization.value = 1
    session.commit()
    while randomization.value:
        randomization.value = session.query(Settings).filter_by(id=1).one()
        if randomization.value == 0:
            break
        time_sleep = random.choice([10])
        spotify_song = get_random_song()
        time.sleep(time_sleep)
        if spotify_song:
            artist = spotify_song['artists'][0]['name']
            song = spotify_song['name']
            result = check_if_youtube_covers(bot, artist + SPLITTER + song)
            if result:
                new_random_cover = add_cover(bot, artist, song, spotify_song['preview_url'])
                time.sleep(time_sleep)
                previous_cover = Covers.get_cover_by_id(new_random_cover.id)
                voices = Voices.get_voices_by_cover_id(previous_cover.id)
                if previous_cover and not voices:
                    get_random_covers_from_youtube(bot, artist + SPLITTER + song, fake_cover=previous_cover)
        else:
            bot.send_message(ADMIN_ID, 'Ни у кого нет песен!')
            break

def handle_start(bot, message):
    bot.send_message(message.chat.id, _(START, message.from_user.language_code))
    try:
        Users.get_user_by_id(message.from_user.id)
    except NoResultFound:
        Users.add_new_user(message.from_user.id, message.from_user.username, message.from_user.language_code)
        bot.send_message(message.chat.id, _(SUBSCRIBE, message.from_user.language_code))
        reply_markup = get_genres()
        bot.send_message(message.chat.id, 'Выбери жанр музыки, который тебе нравится:', reply_markup=reply_markup)


def get_wantings(bot, message, page=0):
    user = Users.get_user_by_id(message.from_user.id)
    covers_voices = Covers.get_wantings(user.telegramUserID, user.level, page)
    wantings_markup = get_wantings_keyboard(covers_voices, page)
    bot.send_message(message.from_user.id, 'Песни, которые сейчас доступны для тебя: ', reply_markup=wantings_markup)
