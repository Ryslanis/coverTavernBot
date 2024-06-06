import flask as flask
import telebot
from dotenv import load_dotenv
import os
import handlers
from handlers.commands.handlers import set_random_fake_cover
from services.logging import logger

telebot.apihelper.ENABLE_MIDDLEWARE = True
bot = telebot.TeleBot(os.getenv("API_TOKEN"))

handlers.handlers_register(bot)


if os.getenv("ENVIRONMENT") == 'production':
    app = flask.Flask(__name__)
    app.config['DEBUG'] = False

    @app.errorhandler(Exception)
    def handle_error(e):
        logger.exception("An error occurred: %s", e)
        # bot.send_message(config.ADMIN_ID, f"An error occurred: {e}")
        return 'Something'


    @app.route('/', methods=['GET', 'HEAD'])
    def index():
        return ''

    # Process webhook calls
    @app.route(os.getenv("WEBHOOK_URL_PATH"), methods=['POST'])
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            flask.abort(403)


    bot.set_webhook(url=os.getenv("WEBHOOK_URL_BASE") + os.getenv("WEBHOOK_URL_PATH"),
                    certificate=open(os.getenv("WEBHOOK_SSL_CERT"), 'r'))
    app.run(host=os.getenv("WEBHOOK_LISTEN"),
            port=os.getenv("WEBHOOK_PORT"),
            ssl_context=(os.getenv("WEBHOOK_SSL_CERT", os.getenv("WEBHOOK_SSL_KEY")))
            )

elif os.getenv("ENVIRONMENT") == 'development':
    # bot.remove_webhook()
    bot.polling()

