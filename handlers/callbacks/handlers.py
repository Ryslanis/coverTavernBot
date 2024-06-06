import json
from datetime import datetime

from requests.exceptions import HTTPError, Timeout
from sqlalchemy.exc import NoResultFound
from telebot.apihelper import ApiTelegramException

from handlers.commands.handlers import get_wantings
from services.spotify import get_top_artists, get_similar_artists, get_artist_by_name
from ui.sentences import _
from utils import utils
from services.database.coverService import Covers

from services import genius
from ui.keyboards import get_covers_propose_keyboard, get_general_info_keyboard, get_participation_propose_keyboard, \
    get_artists_keyboard, get_genres, get_change_artists, get_lang_artists
from utils import exceptions
from utils.exceptions import LevelAccordanceError, CoverExpiredError, MaxParticipationsError, NoPointError, \
    TooManyCoversError, MinParticipationsError, TheSameCover, OnlyForNewbies
from services.database.userService import Users
from services.database.voiceService import Voices
from services.database.artistsService import Artists
from utils.utils import is_song_covered_by_user, check_cp, user_friendly_datetime_format
from settings import *
from ui.sentences import *





def set_current_cover(voice_id, user_id):
    Voices.set_voice_recording(voice_id, user_id)


def handle_wanting_answer(bot, call):
    data = json.loads(call.data)
    cover_id = data['cover_id']
    chosen_points = data['option']
    try:
        cover = Covers.get_cover_by_id(cover_id)
    except NoResultFound:
        bot.answer_callback_query(call.id, 'Нету такого кавера')
        return

    try:
        user = Users.get_user_by_id(call.from_user.id)
    except NoResultFound:
        Users.add_new_user(call.from_user.id, call.from_user.username, call.from_user.language_code)
        bot.answer_callback_query(call.id, _(ERROR_NOT_REGISTERED, call.from_user.language_code))
        return

    # boosting?
    # if cover.status == WANTING and (
    #         cover.targetDate < datetime.now()):
    #     utils.boost_a_cover(bot, cover, foreign_user=True)
    #     return

    check_cp(bot, user)

    try:
        if cover.targetDate < datetime.now():
            raise exceptions.CoverExpiredError(cover)
        if cover.participationsCount == MAX_COVER_PARTICIPANTS:
            raise exceptions.MaxParticipationsError(cover)
        # fake points can be applied by anyone
        if cover.level:
            if user.level != cover.level:
                raise exceptions.LevelAccordanceError(user)
        if user.level:
            if user.points < chosen_points:
                raise exceptions.NoPointError()
        elif not user.level:
            if user.fake_points < chosen_points:
                raise exceptions.NoPointError()
        not_recorded = len(Voices.get_unrecorded_voices(user.telegramUserID))
        if not_recorded > MAX_COVERS_AT_ONCE:
            raise exceptions.TooManyCoversError()
        # kostil'
        is_song_covered_by_user(user.telegramUserID, call.message.text)

    except CoverExpiredError as e:
        bot.answer_callback_query(call.id, _(ERROR_EXPIRED, user.lang) % user_friendly_datetime_format(e.cover.targetDate))
        return
    except LevelAccordanceError as e:
        bot.answer_callback_query(call.id, _(ERROR_LVL_DIFFERENCE, user.lang) % (e.user.level, cover.level))
        return
    except NoPointError:
        bot.answer_callback_query(call.id, _(ERROR_NO_POINTS, user.lang))
        return
    except MaxParticipationsError:
        bot.answer_callback_query(call.id, _(ERROR_MAX_PARTICIPANTS, user.lang))
        return
    except TooManyCoversError as e:
        bot.answer_callback_query(call.id, _(ERROR_TOO_MANY_COVERS, user.lang))
        return
    except TheSameCover:
        bot.answer_callback_query(call.id, _(ERROR_SAME_COVER, user.lang))
        return
    # todo
    #UNCOMMENT!!!!!!!!
    # check if a user participate again
    # try:
    #     voice = Voices.get_voice(cover_id, user.telegramUserID)
    #     voice.points = chosen_points
    #     session.commit()
    # except NoResultFound:
    #     Voices.add_voice(user.telegramUserID, cover.id, points=chosen_points)
    Voices.add_voice(user.telegramUserID, cover.id, points=chosen_points)

    voices = Voices.get_voices_by_cover_id(cover_id)

    if len(voices) == MAX_COVER_PARTICIPANTS or (cover.targetDate < datetime.now()
             and len(voices) >= MIN_COVER_PARTICIPANTS):
        try:
            utils.boost_a_cover(bot, cover, voices[0].points, len(voices))
            try:
                bot.edit_message_text(chat_id=config.DISCUSSION_GROUP_ID, message_id=call.message.id,
                                      text="Учасники выбраны")
                bot.edit_message_reply_markup(chat_id=config.DISCUSSION_GROUP_ID, message_id=call.message.id,
                                              reply_markup=None)
            except ApiTelegramException:
                pass
        except MinParticipationsError:
            return
    else:
        inline_markup = get_participation_propose_keyboard(cover, user.lang)
        bot.edit_message_reply_markup(chat_id=config.DISCUSSION_GROUP_ID, message_id=call.message.id,
                                      reply_markup=inline_markup)


def info_callback(bot, call):
    data = json.loads(call.data)
    try:
        user = Users.get_user_by_id(call.from_user.id)
    except NoResultFound:
        user = Users.add_new_user(call.from_user.id, call.from_user.username, call.from_user.language_code)
    count_voices = Voices.get_voices_count(user.telegramUserID)

    button = data['option']
    if button == 'general':
        place = Users.get_user_place(call.from_user.id)
        user_info = utils.get_user_info_text(user, call.from_user.language_code, place, foreign_user=False)
        bot.send_message(call.message.chat.id, user_info)
    elif button == 'points':
        if user.level != 0:
            bot.send_message(call.from_user.id, _(ADMIN_DIRECT % call.from_user.id))
        else:
            bot.send_message(call.from_user.id, _(MUST_PLAY))

    elif button == 'covers':
        if count_voices:
            page = int(data['page'])
            user_covers = Voices.get_voices_join_cover(call.from_user.id, page)
            reply_markup = get_covers_propose_keyboard(count_voices, page, user_covers, user.lang)

            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.id,
                                  text=_(CHOOSE_COVER, user.lang
                                         ))
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=reply_markup)
        else:
            bot.answer_callback_query(call.id, _(NO_COVERS, user.lang))
    elif button == 'back':
        reply_markup = get_general_info_keyboard(call.from_user.language_code)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=_(CHOOSE_OPTION, user.lang))
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=reply_markup)
    elif button == 'top':
        top_users = Users.get_top_users()
        text_info = '\n'
        for user, place in top_users:
            text_info = text_info + utils.get_user_info_text(user, call.from_user.language_code, place)

        bot.send_message(call.message.chat.id, _(TOP_10, user.lang) + text_info)
    elif button == 'rules':
        bot.send_message(call.message.chat.id, _(RULES_TEXT, user.lang))
    elif button == 'artists':
        user_artists = Artists.get_favorite_artists(call.from_user.id)
        reply_markup = get_change_artists()
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=f"Твои любимые исполнители: {str([artist.artist_name for artist in user_artists]).strip('[]')}", reply_markup=reply_markup)
        # bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=reply_markup)


def handle_chosen_cover(bot, call):
    voice_id = int(json.loads(call.data)['voice_id'])
    voice = Voices.get_voice_by_id(voice_id)
    cover_id = voice.coverID
    cover = Covers.get_cover_by_id(cover_id)
    if cover.resultPostID:
        bot.forward_message(chat_id=call.message.chat.id, from_chat_id=config.GROUP_ID,
                            message_id=cover.resultPostID)
        return
    # if cover.postID:
    #     bot.forward_message(chat_id=call.message.chat.id, from_chat_id=config.GROUP_ID,
    #                         message_id=cover.postID)

    set_current_cover(voice_id, call.from_user.id)

    if cover.status == WANTING:
        if cover.targetDate < datetime.now():
            try:
                utils.boost_a_cover(bot, cover)
            except MinParticipationsError:
                bot.send_message(call.message.chat.id,
                                 _(NOT_ENOUGH_PARTICIPANTS, call.from_user.language_code) % cover.participationsCount)
    if cover.status == COVERING:
        if not voice.telegramVoiceID:
            try:
                lyrics = genius.get_lyrics_for_cover(cover.artist, cover.song)
                bot.send_message(call.message.chat.id, _(LYRICS_TEXT, call.from_user.language_code) % lyrics)
                bot.send_message(call.message.chat.id, _(TIME_LEFT, call.from_user.language_code) %
                                                        (utils.user_friendly_datetime_format(cover.targetDate)))
            except (HTTPError, Timeout):
                bot.send_message(call.message.chat.id, _(LYRICS_ERROR, call.from_user.language_code) + "\n" +
                                                         _(TIME_LEFT, call.from_user.language_code) % (
                                                           utils.user_friendly_datetime_format(cover.targetDate)))

            except MinParticipationsError as e:
                bot.send_message(call.message.chat.id,
                                 _(NOT_ENOUGH_PARTICIPANTS, call.from_user.language_code) % cover.participationsCount + "\n" +
                                   _(TIME_LEFT, call.from_user.language_code) % (
                                     utils.user_friendly_datetime_format(cover.targetDate)))

        else:
            # boost a cover recording if participations != maxCoverParticipations
            if cover.targetDate < datetime.now() and cover.participationsCount > MIN_COVER_PARTICIPANTS:
                try:
                    utils.boost_a_cover(bot, cover)
                except exceptions.MinParticipationsError:
                    voices = Voices.get_voices_by_cover_id(cover.id)
                    bot.send_message(call.from_user.id, _(EARLY_BOOST, call.from_user.language_code) % (
                                                          len([v for v in voices if not v.telegramVoiceID]),
                                                          utils.user_friendly_datetime_format(cover.targetDate)))

    # for immediately appearance of a current voice
    count_voices = Voices.get_voices_count(call.from_user.id)
    page = int(json.loads(call.data)['page'])
    user_covers = Voices.get_voices_join_cover(call.from_user.id, page)
    reply_markup = get_covers_propose_keyboard(count_voices, page, user_covers, call.from_user.language_code)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=reply_markup)
    except ApiTelegramException:
        pass


def handle_points(bot, call):
    data = json.loads(call.data)
    user_id = int(call.message.text.split(' ')[2])
    if data['option'] == 'add':
        Users.add_points(user_id, int(data['value']))
        bot.send_message(user_id, _(POINTS_PRESENT, call.from_user.language_code) % data['value'])


def handle_genre(bot, call):
    data = json.loads(call.data)
    if data.get('option'):
        if data['option'] == 'back':
            reply_markup = get_lang_artists()
            bot.send_message(chat_id=call.from_user.id, text=_(CHOOSE_OPTION),
                             reply_markup=reply_markup)
    else:
        artists = get_top_artists(data['genre'], data['lang'], 0)
        artists_keyboard = get_artists_keyboard(artists, 0, data['genre'], data['lang'], call.from_user.id)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text='Выбери исполнителя:')
        bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id,
                                      reply_markup=artists_keyboard)

def handle_artist(bot, call):
    data = json.loads(call.data)
    try:
        if data.get('option') == 'fullback':
            reply_markup = get_general_info_keyboard()
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text='Выбирай:')
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=reply_markup)
            return
        if data.get('change'):
            if data.get('change') == 1:
                lang = get_lang_artists()
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text='Выбери категорию:')
                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=lang)
                return
            elif data.get('change') == 2:
                Artists.del_favorite_artists(call.from_user.id)
                reply_markup = get_change_artists()
                bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id,
                                      text=f"Удалено",
                                      reply_markup=reply_markup)
                return
        if data.get('genre'):
            if data['genre'] == 'genre':
                genre_keyboard = get_genres(data['lang'])
                bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id,
                                              reply_markup=genre_keyboard)
            elif data.get('page') is not None:
                artists = get_top_artists(data['genre'], data['lang'], data['page'])
                artists_keyboard = get_artists_keyboard(artists, data.get('page'), data['genre'], data['lang'], call.from_user.id)
                bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id,
                                              reply_markup=artists_keyboard)

        elif data.get('lang'):
            send_fav_bands_callbacks(bot, call.from_user.id, data['lang'])
            return

    except ApiTelegramException as e:
        pass


def handle_artist_pressed(bot, call):
    data = json.loads(call.data)

    artist_name = data['n']

    artist = get_artist_by_name(artist_name)
    if data['c'] == 0:
        artist_name = artist['name']
        Artists.add_favorite_artist(call.from_user.id, artist_name, artist['id'])
        similar_artists = get_similar_artists(artist['id'])
        artists_keyboard = get_artists_keyboard(similar_artists, 0, data['g'], data['l'],
                                                call.from_user.id)
        bot.answer_callback_query(call.id, f'{OK} {artist["name"]} добавлен')
        bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id,
                                      reply_markup=artists_keyboard)
    else:
        Artists.del_favorite_artist(call.from_user.id, artist['id'])
        bot.answer_callback_query(call.id, f'{ERROR} {artist["name"]} удален')


def handle_wanting_cover(bot, call):
    data = json.loads(call.data)
    if data.get('cover_id'):
        cover_id = data['cover_id']
        cover = Covers.get_cover_by_id(cover_id)
        points_markup = get_participation_propose_keyboard(cover)
        bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.id, text=f'{cover.artist}{SPLITTER}{cover.song}\nСколько ты готов поставить на себя?')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=points_markup)
    elif data.get('page') is not None:
        get_wantings(bot, call, data.get('page'))

def send_fav_bands_callbacks(bot, chat_id, lang):
    reply_markup = get_genres(lang)
    bot.send_message(chat_id, 'Выбери жанр музыки, который тебе нравится:', reply_markup=reply_markup)