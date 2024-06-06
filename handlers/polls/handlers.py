from datetime import datetime

import config
from settings import *
import utils.utils
from services.database.coverService import Covers
from services.database import session
from services.database.userService import Users
from services.database.voiceService import Voices
from ui.sentences import *
from ui.sentences import _
from sqlalchemy.exc import NoResultFound


def boost_rating(bot, stopped_poll, cover):
    sorted_winners = sorted(stopped_poll.options, key=lambda x: x.voter_count, reverse=True)
    voices = Voices.get_voices_by_cover_id(cover.id)
    for index, part in enumerate(sorted_winners):
        voice_number = int(part.text) - 1
        voice = voices[voice_number]
        score = part.voter_count / stopped_poll.total_voter_count * 100
        voice.score = score

        user = Users.get_user_by_id(voice.telegramUserID)

        user.experience += EXPERIENCE[index]

        # send messages depends on place
        if index == 0:
            cover.winner = voice.id
            if cover.level == 0:
                user.fake_points += cover.points * WINNER_PERCENTAGE
            else:
                user.points += cover.points * WINNER_PERCENTAGE
        else:
            if cover.level == 0:
                user.fake_points -= voice.points
            else:
                user.points -= voice.points

        bot.send_message(voices[voice_number].telegramUserID, _(PRIVATE_WINNER, user.lang) % (
                                                     utils.utils.get_place_emoji(index + 1),
                                                     cover.full_name,
                                                     f'-{cover.points}' if index != 0 else f'+{cover.points}',
                                                     EXPERIENCE[index]
        ))

        voice.place = index + 1

        cover.status = FINISHED

        if user.level <= 0:
            message = bot.send_voice(config.ADMIN_ID, voice=voice.telegramVoiceID)
            poll_message = bot.send_poll(config.ADMIN_ID,
                                         _(POLL_RATE),
                                         LEVELS,
                                         is_anonymous=False,
                                         reply_to_message_id=message.id)
            user.ratingPollID = poll_message.poll.id
            user.ratingPollMessageID = poll_message.id

def handle_newbie_rating_polls(bot, poll_answer):
    """There are two non-anonymous polls: RATING COVER and RATING NEWBIES"""
    try:
        cover = Covers.get_cover_by_rating__poll_id(poll_answer.poll_id)
        cover.votedCount += 1
        session.commit()
        if cover.targetDate < datetime.now() or cover.votedCount >= MIN_VOTED:
            stopped_poll = bot.stop_poll(config.DISCUSSION_GROUP_ID, cover.ratingPollMessageID)
            if cover.status == RATING:
                boost_rating(bot, stopped_poll, cover)
        session.commit()
    except NoResultFound:
        try:
            user = Users.get_user_by_poll_id(poll_answer.poll_id)
            if user.level <= 0:
                stopped_poll = bot.stop_poll(config.ADMIN_ID, user.ratingPollMessageID)
                answer = max(stopped_poll.options, key=lambda x: x.voter_count).text
                if answer in [BOTTOM, LOW, MIDDLE, HIGH, PRO]:
                    level = utils.utils.word_to_level(answer)
                    user.level = level

                    bot.send_message(user.telegramUserID, f'Твой уровень {answer}')

                    if user.experience > LVL_UPGRADE_SCHEME[user.cp]:
                        user.cp += 1

                    session.commit()
                elif answer == BAD:
                    bot.send_message(user.telegramUserID, f'Извини, но твой уровень не подходит. Практикуйтесь')
        except NoResultFound:
            pass
            # if cover.status != FAKE:
            #     bot.send_message(config.ADMIN_ID, 'Нету такого пользователя!')



