from settings import ADMIN_OPTIONS
from handlers.inline.handlers import spotify_tracks_search, do_to_users


def inline_register(bot):
    @bot.inline_handler(func=lambda query: all(not query.query.startswith(opt) for opt in ADMIN_OPTIONS))
    def song_query(query):
        spotify_tracks_search(bot, query)

    @bot.inline_handler(func=lambda query: all([query.query.startswith(opt) for opt in ADMIN_OPTIONS]))
    def admin_users_query(query):
        page = '0'
        try:
            command, page, option, parameter = query.query.split(' ', maxsplit=3)
            page = int(page)
            do_to_users(bot, query.id, page, option, parameter)
        except ValueError:
            do_to_users(bot, query.id, page)
