from handlers.polls.handlers import handle_newbie_rating_polls

def polls_register(bot):
    @bot.poll_answer_handler()
    def handle_poll_answer(poll_answer):
        """Handle non-anonymous polls (newbies, ratings)"""
        # if a poll was revoked there are empty option_ids
        if len(poll_answer.option_ids):
            handle_newbie_rating_polls(bot, poll_answer)
