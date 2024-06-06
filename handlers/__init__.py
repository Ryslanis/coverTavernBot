from handlers.callbacks import callbacks_register
from handlers.commands import commands_register
from handlers.content_types import content_types_register
from handlers.inline import inline_register
from handlers.messages import messages_register
from handlers.middleware import middleware_register
from handlers.polls import polls_register


def handlers_register(bot):
    middleware_register(bot)
    callbacks_register(bot)
    commands_register(bot)
    content_types_register(bot)
    messages_register(bot)
    polls_register(bot)
    inline_register(bot)
