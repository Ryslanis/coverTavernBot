import json

from settings import WANTING
from handlers.callbacks.handlers import handle_wanting_answer, set_current_cover, info_callback, handle_points, \
    handle_genre, handle_artist, handle_wanting_cover, handle_artist_pressed


def callbacks_register(bot):
    # INLINE CALLBACKS
    @bot.callback_query_handler(func=lambda call: json.loads(call.data)['type'] == WANTING)
    def handle_wanting(call):
        handle_wanting_answer(bot, call)

    @bot.callback_query_handler(func=lambda call: json.loads(call.data)['type'] == 'covers')
    def handle_chosen_cover(call):
        if call.message.chat.type == 'private':
            handlers.handle_chosen_cover(bot, call)

    @bot.callback_query_handler(func=lambda call: json.loads(call.data)['type'] == 'info')
    def handle_info_query(call):
        info_callback(bot, call)

    @bot.callback_query_handler(func=lambda call: json.loads(call.data)['type'] == 'points')
    def handle_info_query(call):
        handle_points(bot, call)

    @bot.callback_query_handler(func=lambda call: json.loads(call.data)['type'] == 'genre')
    def handle_info_query(call):
        handle_genre(bot, call)

    @bot.callback_query_handler(func=lambda call: json.loads(call.data)['type'] == 'ar' and json.loads(call.data).get('n'))
    def handle_info_query(call):
        handle_artist_pressed(bot, call)

    @bot.callback_query_handler(func=lambda call: json.loads(call.data)['type'] == 'ar')
    def handle_info_query(call):
        handle_artist(bot, call)

    @bot.callback_query_handler(func=lambda call: json.loads(call.data)['type'] == 'wanting_private')
    def handle_wanting(call):
        handle_wanting_cover(bot, call)
