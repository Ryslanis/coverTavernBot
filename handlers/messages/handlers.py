import os
from datetime import datetime, timedelta
from requests.exceptions import HTTPError, Timeout
from sqlalchemy.exc import NoResultFound

from services.genius import get_lyrics_for_cover
from services.database import Cover, session
from services.database.coverService import Covers
from services.database.userService import Users
from services.database.voiceService import Voices
from ui.keyboards import get_participation_propose_keyboard
from ui.sentences import _
from ui.sentences import *
from settings import *
from utils import utils
from utils.exceptions import TheSameCover
from utils.utils import is_song_covered_by_user, level_to_word, check_cp, \
    word_to_level
from config import *


def send_inline_poll(bot, message):
    cover_id = int(message.text.split(". ")[0])
    try:
        cover = Covers.get_cover_by_id(cover_id)
    except NoResultFound:
        # if a cover was added by an admin (via inline mode)
        name, _, level, preview_url = message.text.split("\n", maxsplit=3)
        name = name.split(PARAMETER_SPLITTER, maxsplit=1)[1].strip()
        level = level.split(PARAMETER_SPLITTER, maxsplit=1)[1].strip()
        preview_url = preview_url.split(PARAMETER_SPLITTER, maxsplit=1)[1].strip()
        level = int(word_to_level(level))
        artist, song = name.strip().split(SPLITTER, maxsplit=1)
        cover = Covers.add_cover(artist, song, level, WANTING, config.ADMIN_ID, partcipantsCount=0,
                                 preview_url=preview_url, postID=message.id)

    inline_markup = get_participation_propose_keyboard(cover, message.from_user.language_code)

    full_cover_name = message.text.split(NEW_COVER_INDICATOR_CHANNEL)[-1]

    # bot.send_voice(config.DISCUSSION_GROUP_ID, voice=cover.previewUrl, reply_to_message_id=message.message_id)
    message_with_poll = bot.send_message(
        config.DISCUSSION_GROUP_ID,
        WHO_WANTS_INDICATOR,
        reply_markup=inline_markup, reply_to_message_id=message.message_id)

    cover.wantingPollID = message_with_poll.id
    session.commit()



def send_group_message__poll_cover(bot, message):
    cover_id = message.text.split('.')[0]
    cover = Covers.get_cover_by_id(cover_id)
    rating_voices = Voices.get_voices_by_cover_id(cover_id)
    for index, voice in enumerate(rating_voices, start=1):
        bot.send_voice(config.DISCUSSION_GROUP_ID, voice=voice.telegramVoiceID,
                       reply_to_message_id=message.id, caption=str(index))

    answers = [str(num) for num in list(range(1, 3 if cover.participationsCount == 1 else cover.participationsCount+1))]
    message = bot.send_poll(config.DISCUSSION_GROUP_ID, f"Кто исполнил песню лучше?",                            answers,
                            reply_to_message_id=message.id,
                            is_anonymous=False)

    cover.ratingPollID = message.poll.id
    cover.ratingPollMessageID = message.id
    session.commit()


def add_new_cover(bot, message):
    try:
        user = Users.get_user_by_id(message.from_user.id)
    except NoResultFound:
        user = Users.add_new_user(message.from_user.id, message.from_user.username, message.from_user.language_code)

    check_cp(bot, user)

    cover_params = []
    for row in message.text.split('\n'):
        value = row.split(PARAMETER_SPLITTER, maxsplit=1)[1]
        cover_params.append(value)

    # static_points = int(static_points.strip(f' {POINT}{FAKE_POINT}'))

    if user.points < MIN_POINTS + COST_ADD_COVER:
        bot.send_message(message.chat.id, _(ERROR_NO_POINTS, user.lang))
        return

    if user.fake_points < COST_ADD_COVER + MIN_POINTS:
        bot.send_message(message.chat.id, _(ERROR_NO_POINTS, message.from_user.language_code))
        return

    song_full_name, preview_url = cover_params

    artist = song_full_name.split(SPLITTER)[0]
    song = song_full_name.split(SPLITTER)[1]

    try:
        is_song_covered_by_user(user.telegramUserID, artist + SPLITTER + song)
    except TheSameCover:
        bot.send_message(message.chat.id, _(ERROR_SAME_COVER, user.lang))
        return

    user.points -= COST_ADD_COVER
    new_cover = Cover(artist=artist, song=song, level=user.level, status=WANTING,
                  targetDate=datetime.now() + timedelta(seconds=SEC_WANTING),
                  previewUrl=preview_url,
                  )

    session.add(new_cover)
    session.commit()

    post = bot.send_message(config.GROUP_ID,
                           _(COVER_ADDED_PUBLIC, 'en') % (
                                new_cover.id,
                                artist + SPLITTER + song,
                                POINT if user.level else FAKE_POINT,
                                level_to_word(new_cover.level),
                                new_cover.previewUrl
                            ))
    new_cover.postID = post.id
    user.experience += EXP_VOICE
    session.commit()


def handle_admin_users_actions_command(bot, message):
    try:
        command, option, parameter, username, user_id = message.text.split(' ', maxsplit=5)
    except ValueError:
        command, username, user_id = message.text.split(' ', maxsplit=2)
        try:
            user = Users.get_user_by_username(username)
            bot.send_message(config.ADMIN_ID, utils.get_user_info_text(user, foreign_user=False))
            return
        except NoResultFound:
            bot.send_message(config.ADMIN_ID, _(ERROR_USER_NOT_FOUND, message.from_user.language_code))
            return

    if option == ADD_POINTS:
        try:
            if 'all' in parameter:
                points = int(parameter.removeprefix('all'))
                Users.add_points(None, points, to_all=True)
            else:
                Users.add_points(user_id, int(parameter))

            bot.send_message(message.chat.id, _(SUCCESS_OK, message.from_user.language_code))

        except ValueError:
            bot.send_message(message.chat.id, _(ERROR_WRONG_PARAMETER, message.from_user.language_code) % parameter)


def send_fake_covers(bot, message):

    directory = 'services/faking/downloads'

    # Get the list of files and subdirectories in the directory
    contents = os.listdir(directory)
    if contents:
        # Iterate over the contents
        for item in contents:
            # Create the full path to the item
            item_path = os.path.join(directory, item)
            # Check if the item is a file
            if os.path.isfile(item_path):
                audio = open(item_path, 'rb')
                bot.send_audio(config.DISCUSSION_GROUP_ID, audio, reply_to_message_id=message.id)
                audio.close()
        bot.send_poll(config.DISCUSSION_GROUP_ID, f"Кто исполнил песню лучше?", [str(num) for num in range(1, len(contents) + 1)],
                                reply_to_message_id=message.id,
                                is_anonymous=False)
    else:
        bot.send_message(message.chat.id, "Can't stuff fake covers")

    # Clean up downloaded files

    # for audio_file in contents:
    #     try:
    #         os.remove(audio_file)
    #     except FileNotFoundError:
    #         pass