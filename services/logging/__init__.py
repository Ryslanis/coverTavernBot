import logging
from dotenv import load_dotenv
import os
import telebot

load_dotenv()


def get_logger():
    logger = telebot.logger
    logger.setLevel(os.getenv("LOG_LEVEL"))
    handler = logging.FileHandler('services/logging/error.log')
    handler.setLevel(os.getenv("LOG_LEVEL"))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


logger = get_logger()
