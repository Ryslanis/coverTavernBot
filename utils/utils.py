import json
from datetime import datetime, timedelta

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from handlers.polls.handlers import boost_rating
from services.database import session, User
from services.database.userService import Users
from services.database.voiceService import Voices
from settings import *
from ui.sentences import *
from ui.sentences import _
from utils.exceptions import MinParticipationsError, TheSameCover



def get_user_info_text(user, lang, place, foreign_user=True):
    count_recorded_voices = len(Voices.get_recorded_voices(user.telegramUserID))

    if not foreign_user:
        return _(USER_INFO, lang) % (
            user.username if user.username else "...",
            get_place_emoji(place),
            level_to_word(user.level),
            f"{user.experience}/{LVL_UPGRADE_SCHEME[user.level]}",
            user.points,
            user.fake_points,
            count_recorded_voices
        )
    else:
        return _(USER_INFO_PRIVATE) % (
            user.username if user.username else "...",
            get_place_emoji(place),
            level_to_word(user.level),
            f"{user.experience}/{LVL_UPGRADE_SCHEME[user.level]}",
            user.fake_points,
            count_recorded_voices
        )


def send_admin_notification__new_user(bot, user_count):
    bot.send_message(config.ADMIN_ID, f"You have already {user_count} users!")


def add_user_with_notification(bot, user_id, username, chat_id):
    user = Users.add_new_user(user_id, username)
    # send notification
    user_count = session.query(User).count()
    if user_count % 1 == 0:
        send_admin_notification__new_user(bot, user_count)

    return user


def boost_a_cover(bot, cover, points=0, part_count=0):
    if cover.status == WANTING:

        cover.status = COVERING
        cover.targetDate += timedelta(seconds=SEC_COVERING)
        user_voices = Voices.get_voices_by_cover_id(cover.id)
        cover.participationsCount = len(user_voices)
        # broadcast
        cover.points = points * part_count

        for v in user_voices:
            user = Users.get_user_by_id(v.telegramUserID)

            if cover.level:
                user.points -= points
            else:
                user.fake_points -= v.points

            bot.send_message(v.telegramUserID, _(PRIVATE_TIME_TO_RECORD, user.lang) % (
                cover.full_name,
                v.points,
                cover.participationsCount,
                cover.points - int(cover.points * MY_PERCENTAGE)
            ))



    elif cover.status == COVERING:
        voices = Voices.get_voices_by_cover_id(cover.id)
        recorded_voices = list(filter(lambda v: v.telegramVoiceID, voices))
        # todo
        if len(recorded_voices) >= MIN_COVER_PARTICIPANTS:
            cover.status = RATING
            cover.targetDate += timedelta(seconds=SEC_RATING)
            user_voices = Voices.get_voices_by_cover_id(cover.id)
            # broadcast
            for v in user_voices:
                user = Users.get_user_by_id(v.telegramUserID)
                bot.send_message(v.telegramUserID, _(PRIVATE_RATING, user.lang) % cover.full_name)
        else:
            raise MinParticipationsError(cover)

    elif cover.status == RATING:
        if cover.targetDate < datetime.now() or cover.votedCount >= MIN_VOTED:
            stopped_poll = bot.stop_poll(config.DISCUSSION_GROUP_ID, cover.ratingPollMessageID)
            boost_rating(bot, stopped_poll, cover)

    if cover.status == COVERING:
        reply_markup = None
        bot.edit_message_reply_markup(chat_id=config.DISCUSSION_GROUP_ID, message_id=cover.wantingPollID,
                                      reply_markup=reply_markup)

    session.commit()


def user_friendly_datetime_format(date, short=False):
    if not short:
        return date.strftime("%Y-%m-%d %H:%M")
    else:
        return date.strftime("%m-%d %H:%M")


def get_place_emoji(place):
    if place == 1:
        return FIRST
    elif place == 2:
        return SECOND
    elif place == 3:
        return THIRD
    else:
        return str(place)


def is_song_covered_by_user(user_id, full_song):
    cover_voice = Voices.get_voices_join_cover(user_id, 0, None)
    for covers, voices in cover_voice:
        if covers.full_name in full_song:
            user = Users.get_user_by_id(user_id)
            if covers.level == user.level:
                raise TheSameCover


def level_to_word(lvl):
    if lvl == 0:
        return NEWBIE
    elif lvl == 1:
        return BOTTOM
    elif lvl == 2:
        return LOW
    elif lvl == 3:
        return MIDDLE
    elif lvl == 4:
        return HIGH
    elif lvl == 5:
        return PRO


def word_to_level(word):
    if word == NEWBIE:
        return 0
    if word == BOTTOM:
        return 1
    elif word == LOW:
        return 2
    elif word == MIDDLE:
        return 3
    elif word == HIGH:
        return 4
    elif word == PRO:
        return 5


def check_cp(bot, user):
    # For level upgradings
    if user.level < 0:
        return
    if user.experience > LVL_UPGRADE_SCHEME[user.cp]:
        voice = Voices.get_last_random_voice(user.telegramUserID)
        if voice:
            message = bot.send_voice(config.ADMIN_ID, voice=voice.telegramVoiceID)
            poll_message = bot.send_poll(config.ADMIN_ID,
                                         _(POLL_RATE, message.from_user.language_code),
                                         LEVELS,
                                         is_anonymous=False,
                                         reply_to_message_id=message.id)

            user.ratingPollID = poll_message.poll.id
            user.ratingPollMessageID = poll_message.id
            user.level = -user.level
            session.commit()
            return


def get_language(lang, translate=False):
    language = 'russian'
    if lang == 'en':
        if not translate:
            language = ''
        else:
            language = 'Зарубежный'
    elif lang == 'ru':
        if not translate:
            language = 'russian'
        else:
            language = 'Русский'
    elif lang == 'uk':
        if not translate:
            language = 'ukrainian'
        else:
            language = 'Українский'

    return language