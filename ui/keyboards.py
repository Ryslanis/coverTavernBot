import json

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from services.database.artistsService import Artists
from services.database.voiceService import Voices
from settings import GIVE_POINTS
from ui.emoji import *
from ui.sentences import *
from ui.sentences import _
from utils.utils import get_place_emoji, user_friendly_datetime_format, get_language
from unidecode import unidecode


def get_participation_propose_keyboard(cover, lang=None):
    cover_id = cover.id
    points = (50, 100, 150)
    points2 = (300, 500)

    return InlineKeyboardMarkup([[
        InlineKeyboardButton(
            f"{i} {POINT if cover.level != 0 else FAKE_POINT}" + (f"({Voices.get_points_count(cover_id, i)})"
                                                                  if Voices.get_points_count(cover_id, i) else ''),
            callback_data=json.dumps({
                'type': 'wanting',
                'option': i,
                'cover_id': cover_id,
            })) for i in points
    ], [
        InlineKeyboardButton(
            f"{i} {POINT if cover.level != 0 else FAKE_POINT}" + (f"({Voices.get_points_count(cover_id, i)})"
                                                                  if Voices.get_points_count(cover_id, i) else ''),
            callback_data=json.dumps({
                'type': 'wanting',
                'option': i,
                'cover_id': cover_id,
            })) for i in points2
    ]])


def get_covers_propose_keyboard(count_voices, page, user_covers, lang):
    covers_buttons = []
    for covers, voices in user_covers:
        icons = " ".join([CUR if voices.current else '',
                          get_place_emoji(voices.place) if voices.place else (
                              OK if voices.telegramMessageID is not None else ''),
                          COVER if not voices.telegramMessageID else '',
                          ])
        covers_buttons.append([InlineKeyboardButton(icons + " " + covers.full_name + " | " +
                                                    user_friendly_datetime_format(covers.targetDate, short=True),
                                                    callback_data=json.dumps({
                                                        'type': 'covers',
                                                        'voice_id': voices.id,
                                                        'page': page
                                                    }))])

    bottom_buttons = []

    if page != 0:
        bottom_buttons.append(InlineKeyboardButton(_(BACK_, lang), callback_data=json.dumps({
            'type': 'info',
            'option': 'covers',
            'page': page - 1
        })))

    bottom_buttons.append(InlineKeyboardButton(_(INFO_, lang), callback_data=json.dumps({
        'type': 'info',
        'option': 'back'
    })))

    if count_voices > page * 4:
        bottom_buttons.append(InlineKeyboardButton(_(NEXT_, lang), callback_data=json.dumps({
            'type': 'info',
            'option': 'covers',
            'page': page + 1
        })))

    return InlineKeyboardMarkup(covers_buttons + [bottom_buttons])


def get_admin_points_propose():
    return InlineKeyboardMarkup([list([
        InlineKeyboardButton(f'Give {i}', callback_data=json.dumps({
            'type': 'points',
            'option': 'add',
            'value': i,
        })) for i in GIVE_POINTS

    ])])


def get_general_info_keyboard(lang=None):
    button_list = [
        [InlineKeyboardButton(_(MY_STATISTICS, lang), callback_data=json.dumps({
            'type': 'info',
            'option': 'general'
        }))],
        [InlineKeyboardButton(_(MY_COVERS, lang), callback_data=json.dumps(({
            'type': 'info',
            'option': 'covers',
            'page': 0
        })))],
        [InlineKeyboardButton(_(GET_POINTS, lang), callback_data=json.dumps(({
            'type': 'info',
            'option': 'points'
        })))],
        [InlineKeyboardButton(_(TOP_10, lang), callback_data=json.dumps(({
            'type': 'info',
            'option': 'top'
        })))],
        [InlineKeyboardButton(_(RULES_, lang), callback_data=json.dumps(({
            'type': 'info',
            'option': 'rules'
        })))],
        [InlineKeyboardButton("Любимые исполнители 📼", callback_data=json.dumps(({
            'type': 'info',
            'option': 'artists'
        })))],
    ]
    return InlineKeyboardMarkup(button_list)


def get_admin_panel():
    option_list = [
        InlineKeyboardButton("Give points", callback_data=json.dumps({
            'type': 'admin',
            'option': 'points',
            'action': 'add'
        }))
    ]

    return InlineKeyboardMarkup([option_list])


def get_genres(lan):
    language = get_language(lan, translate=True)
    button_list = [
        [InlineKeyboardButton(f'{language} поп', callback_data=json.dumps({
            'type': 'genre',
            'genre': 'pop',
            'lang': lan
        }))],
        [InlineKeyboardButton(f"{language} рок", callback_data=json.dumps(({
            'type': 'genre',
            'genre': 'rock',
            'lang': lan
        })))],
        [InlineKeyboardButton(f"{language} инди", callback_data=json.dumps(({
            'type': 'genre',
            'genre': 'indie',
            'lang': lan
        })))],
        [InlineKeyboardButton(f"{language} метал", callback_data=json.dumps(({
            'type': 'genre',
            'genre': 'metal',
            'lang': lan
        })))],
        [InlineKeyboardButton(BACK_, callback_data=json.dumps(({
            'type': 'genre',
            'option': 'back',
            'lang': lan
        })))]
    ]
    return InlineKeyboardMarkup(button_list)


def get_artists_keyboard(artists, page, genre, lang, user_id):
    user_artists = Artists.get_artists(user_id)
    artist_list = []
    for artist in artists:
        check = ''
        for user_artist in user_artists:
            if user_artist.artist_name == artist['name']:
                check = OK

        artist_list.append([InlineKeyboardButton(f"{check} {artist['name']}", callback_data=json.dumps({
            'type': 'ar',
            'g': genre,
            'n': unidecode(artist['name'][0:6]),
            'c': 1 if check else 0,
            'l': lang
        }))])

    button_list = []
    button_list.append(InlineKeyboardButton('Жанры', callback_data=json.dumps({
        'type': 'ar',
        'genre': 'genre',
        'lang': lang
    })))

    if page != 0:
        button_list.append(InlineKeyboardButton(_(BACK_), callback_data=json.dumps({
            'type': 'ar',
            'genre': genre,
            'page': page - 1,
            'lang': lang
        })))

    button_list.append(InlineKeyboardButton(_(NEXT), callback_data=json.dumps({
        'type': 'ar',
        'genre': genre,
        'page': page + 1,
        'lang': lang
    })))

    return InlineKeyboardMarkup(artist_list + [button_list])


def get_wantings_keyboard(wantings, page):
    songs = []
    for cover, voice in wantings:
        songs.append([InlineKeyboardButton(cover.artist + SPLITTER + cover.song, callback_data=json.dumps({
            'type': 'wanting_private',
            'cover_id': cover.id,
        }))])

    button_list = []

    if page != 0:
        button_list.append(InlineKeyboardButton(_(BACK_), callback_data=json.dumps({
            'type': 'wanting_private',
            'page': page - 1
        })))

    button_list.append(InlineKeyboardButton(_(NEXT), callback_data=json.dumps({
        'type': 'wanting_private',
        'page': page + 1
    })))

    return InlineKeyboardMarkup(songs + [button_list])


def get_change_artists():
    return InlineKeyboardMarkup([[InlineKeyboardButton('Изменить', callback_data=json.dumps({
            'type': 'ar',
            'change': 1
        }))], [InlineKeyboardButton('Удалить все', callback_data=json.dumps({
            'type': 'ar',
            'change': 2
        }))]
                                 ])


def get_lang_artists():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton('Зарубежные', callback_data=json.dumps({
            'type': 'ar',
            'lang': 'en'
        }))],
        [InlineKeyboardButton('Российские', callback_data=json.dumps({
            'type': 'ar',
            'lang': 'ru'
        }))],
        [InlineKeyboardButton('Украинские', callback_data=json.dumps({
            'type': 'ar',
            'lang': 'uk'
        }))],
        [InlineKeyboardButton(BACK_, callback_data=json.dumps({
            'type': 'ar',
            'option': 'fullback'
        }))]
    ])