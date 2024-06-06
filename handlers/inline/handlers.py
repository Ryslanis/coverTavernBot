from telebot.types import InlineQueryResultArticle, InputTextMessageContent

import config
import settings
from services.database import session, Cover
from services.database.userService import Users
from services.spotify import sp
from settings import *
from ui.sentences import COVER_ADDED_PRIVATE, COVER_ADDED_PUBLIC
from ui.sentences import _
from utils.utils import level_to_word


def spotify_tracks_search(bot, query):
    fake = False
    if query.query:
        try:
            next_cover_id = session.query(Cover.id).order_by(Cover.id.desc()).first()[0] + 1
        except TypeError:
            next_cover_id = 0
        if query.from_user.id == config.ADMIN_ID and query.chat_type == 'channel':
                try:
                    level, query_text = query.query.split(' ', maxsplit=1)
                    level = int(level)
                except ValueError:
                    return
                except TypeError:
                    next_cover_id = 1
        else:
            if query.query.startswith('Fake'):
                fake = True
                query_text = query.query.removeprefix('Fake ')
            else:
                try:
                    query_text = query.query
                except ValueError:
                    return

        results = sp.search(q=query_text or ' ', limit=20, type='track')

        inline_query_result_articles = []
        for idx, track in enumerate(results['tracks']['items']):
            artist = track['album']['artists'][0]['name']
            song = track['name']
            image = track['album']['images'][-1]['url']

            if not track['preview_url'] or not track['duration_ms']:
                continue

            article = InlineQueryResultArticle(
                id=idx,
                title=artist,
                input_message_content=(InputTextMessageContent(_(COVER_ADDED_PUBLIC) % (str(next_cover_id), artist + SPLITTER + song, POINT if level else FAKE_POINT,
                                                                     level_to_word(int(level)), track['preview_url']))

                if query.chat_type == 'channel' and query.from_user.id == config.ADMIN_ID
                                        else InputTextMessageContent(_(COVER_ADDED_PRIVATE) % (artist + SPLITTER + song, track['preview_url']))) if not fake
        else InputTextMessageContent(FAKE_INDICATOR + artist + SPLITTER + song)
                ,
                thumbnail_url=image if image else '',
                description=song
            )
            inline_query_result_articles.append(article)

        bot.answer_inline_query(query.id, inline_query_result_articles, cache_time=60)

    # try:
    #     Users.get_user_by_id(query.from_user.id)
    # except NoResultFound:
    #     utils.send_subscribe(bot, query.from_user.id)


def do_to_users(bot, query_id, page, option=None, parameter=None):
    results = Users.get_users(page)
    inline_query_result_users = []
    for user in results:
        message_content = [
            USERS_ACTIONS_COMMAND,
            option,
            parameter,
            f'{user.username}' if user.username else '...',
            str(user.telegramUserID)
        ]
        message_content = " ".join(list(filter(lambda x: x is not None, message_content)))
        article = InlineQueryResultArticle(
            id=user.id,
            title=user.username if user.username else '...',
            input_message_content=InputTextMessageContent(message_content),
            description=message_content
        )
        inline_query_result_users.append(article)

    bot.answer_inline_query(query_id, inline_query_result_users, cache_time=60)
