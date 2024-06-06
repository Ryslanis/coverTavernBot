from handlers.content_types.handlers import handle_voice


def content_types_register(bot):
    # CONTENT_TYPES HANDLERS
    @bot.message_handler(content_types=['voice'])
    def send_newbie_cover(message):
        if message.chat.type == 'private':
            handle_voice(bot, message)
            