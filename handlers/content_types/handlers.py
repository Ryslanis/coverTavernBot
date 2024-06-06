from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from settings import *
import utils.utils
from ui.sentences import *
from ui.sentences import _
from utils import exceptions
from services.database.coverService import Covers
from services.database import session
from services.database.voiceService import Voices
from services.database.userService import Users


def handle_voice(bot, message):
    try:
        user = Users.get_user_by_id(message.from_user.id)
    except NoResultFound:
        user = Users.add_new_user(message.from_user.id, message.from_user.username, message.from_user.language_code)
        bot.send_message(message.chat.id, config.GROUP_INVITE_LINK)

    try:
        voice = Voices.get_active_voice(user.telegramUserID)
        cover = Covers.get_cover_by_id(voice.coverID)
        try:
            if message.voice.duration < MIN_DURATION:
                raise exceptions.WrongVoiceDuration(duration=message.voice.duration)

            if cover.participationsCount < MIN_COVER_PARTICIPANTS:
                raise exceptions.MinParticipationsError(cover)

            # a user fucked up a voice
            if cover.status != COVERING:
                raise exceptions.CoverExpiredError(cover)

            # okay
            voices = Voices.get_voices_by_cover_id(cover.id)
            if cover.status == COVERING:
                if not voice.telegramVoiceID:
                    voice.recorded = True
                    voice.telegramVoiceID = message.voice.file_id
                    voice.telegramMessageID = message.id
                    voice.current = False
                    session.commit()
                else:
                    bot.send_message(message.chat.id,
                                     _(ERROR_ALREADY_RECORDED, user.lang) % (cover.artist + SPLITTER + cover.song))
                    return

            if cover.status == COVERING:
                rest_covers_count = len([v for v in voices if not v.telegramVoiceID])
                bot.send_message(message.chat.id,
                                 _(SUCCESS_VOICE_ACCEPTED, user.lang) % (cover.artist + SPLITTER + cover.song) +
                                 (_(EARLY_BOOST, user.lang) % (len([v for v in voices if not v.telegramVoiceID]),
                                                     (utils.utils.user_friendly_datetime_format(
                                                         cover.targetDate))) if rest_covers_count else ''))

                all_voices_recorded = all(v.telegramVoiceID for v in voices)
                if all_voices_recorded:
                    utils.utils.boost_a_cover(bot, cover, voice.points)
                    post = bot.send_message(
                        config.GROUP_ID,
                        _(CHANNEL_RATING, 'en') % (cover.id, RATING_INDICATOR, cover.full_name, utils.utils.level_to_word(cover.level),
                                                   ))
                    cover.resultPostID = post.id


        except exceptions.CoverExpiredError as e:
            bot.send_message(message.chat.id, _(ERROR_EXPIRED, user.lang))
        except exceptions.MinParticipationsError as e:
            bot.send_message(message.chat.id, _(ERROR_MIN_PARTICIPANTS, user.lang))
        except exceptions.WrongVoiceDuration as e:
            bot.send_message(message.chat.id, _(ERROR_DURATION, user.lang))

        session.commit()

    except (MultipleResultsFound, NoResultFound):
        bot.send_message(message.chat.id, _(ERR0R_NOT_CHOSEN, user.lang))
