from modules import random_fact_m, welcome_m, chatgpt_interface_m, personality_chat_m, quiz_m, describe_picture_m
from telegram.ext import CallbackQueryHandler
import logging

logger = logging.getLogger(__name__)

def listing(application):
    application.add_handler(
        CallbackQueryHandler(random_fact_m.random_fact_callback, pattern="^random_fact$")
    )
    application.add_handler(
        CallbackQueryHandler(random_fact_m.generate_random_fact, pattern="^generate_fact:(.+)$")
    )
    application.add_handler(
        CallbackQueryHandler(welcome_m.start, pattern="^start$")
    )
    application.add_handler(
        CallbackQueryHandler(chatgpt_interface_m.gpt_command, pattern="^gpt$")
    )
    application.add_handler(
        CallbackQueryHandler(personality_chat_m.per_chat_command, pattern="^talk$")
    )
    application.add_handler(
        CallbackQueryHandler(personality_chat_m.per_chat_start, pattern="^person_talk:(.+)$")
    )
