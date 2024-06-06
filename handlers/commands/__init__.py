import time

import config
from handlers.commands.handlers import send_inline_info_panel, send_statistics, set_random_fake_cover, handle_start, \
    get_wantings
from services.database import session, Settings
from services.faking.faking import get_random_covers_from_youtube
from ui.sentences import *
from ui.sentences import _


def commands_register(bot):
    # COMMANDS HANDLERS
    @bot.message_handler(commands=['cpanel'])
    def get_info(message):
        if message.chat.type == 'private':
            send_inline_info_panel(bot, message)

    @bot.message_handler(commands=['start'])
    def start(message):
        if message.chat.type == 'private':
            handle_start(bot, message)


    @bot.message_handler(commands=['statistics'], func=lambda message: message.chat.id == config.ADMIN_ID)
    def statistics(message):
        send_statistics(bot, message)

    @bot.message_handler(commands=['random', 'randomoff'], func=lambda message: message.from_user.id == config.ADMIN_ID and
                         message.chat.type == 'private')
    def get_random_covers(message):
        if message.text == '/random':
            set_random_fake_cover(bot)
        elif message.text == '/randomoff':
            randomization = session.query(Settings).filter_by(id=1).one()
            randomization.value = 0
            session.commit()

    @bot.message_handler(commands=['sing'])
    def statistics(message):
        if message.chat.type == 'private':
            get_wantings(bot, message)


