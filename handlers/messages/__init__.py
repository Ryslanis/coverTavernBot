import config
from services.database.coverService import Covers
from services.faking.faking import get_random_covers_from_youtube
from settings import NEW_COVER_INDICATOR, NEW_COVER_INDICATOR_CHANNEL, NEWBIE_INDICATOR, RATING_INDICATOR, \
    USERS_ACTIONS_COMMAND, FAKE_INDICATOR, MIN_COVER_PARTICIPANTS
from handlers.messages.handlers import add_new_cover, send_inline_poll, send_group_message__poll_cover, \
    handle_admin_users_actions_command, send_fake_covers


def messages_register(bot):
    # @bot.message_handler(
    #     func=lambda message: True)
    # def test(message):
    #     print(message)
    #     return

    @bot.message_handler(
        func=lambda message: NEW_COVER_INDICATOR in message.text and message.via_bot)
    def new_cover_private(message):
        if message.chat.type == 'private' and message.via_bot.id == config.BOT_ID:
            add_new_cover(bot, message)

    @bot.message_handler(
        func=lambda message: NEW_COVER_INDICATOR_CHANNEL in message.text)
    def new_cover_public(message):
        if message.chat.id == config.DISCUSSION_GROUP_ID:
            send_inline_poll(bot, message)

    # @bot.message_handler(func=lambda message: NEWBIE_INDICATOR in message.text and message.chat.id == config.DISCUSSION_GROUP_ID)
    # def send_poll_newbie(message):
    #     if message.chat.id == config.DISCUSSION_GROUP_ID:
    #         send_group_message__poll_newbie_voice(bot, message)

    @bot.message_handler(
        func=lambda message: RATING_INDICATOR in message.text and message.chat.id == config.DISCUSSION_GROUP_ID)
    def handle_new_rating(message):
        cover_id = message.text.split('.')[0]
        cover = Covers.get_cover_by_id(cover_id)
        if cover.participationsCount >= MIN_COVER_PARTICIPANTS:
            send_group_message__poll_cover(bot, message)
        else:
            send_fake_covers(bot, message)


    # Admin massages handlers
    @bot.message_handler(func=lambda message: message.text.startswith(USERS_ACTIONS_COMMAND)
                                              and message.from_user.id == config.ADMIN_ID)
    def handle_users_actions_command(message):
        handle_admin_users_actions_command(bot, message)

    @bot.message_handler(func=lambda message: message.text.startswith(FAKE_INDICATOR) and message.via_bot and message.chat.id == config.ADMIN_ID)
    def handle_adding_fake_covers(message):
        song_full_name = message.text.removeprefix(FAKE_INDICATOR)
        get_random_covers_from_youtube(bot, song_full_name)
