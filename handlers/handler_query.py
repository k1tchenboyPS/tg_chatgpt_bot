from modules import random_fact_m, say_hi_m, welcome_m
from telegram.ext import CallbackQueryHandler
import logging

logger = logging.getLogger(__name__)

# def listing(application):
#     application.add_handler(
#         CallbackQueryHandler(welcome_m.random_fact_callback, pattern="^random_fact$")
#     )
#
def listing(application):
    application.add_handler(
        CallbackQueryHandler(random_fact_m.random_fact_callback, pattern="^random_fact$")
    )
    application.add_handler(
        CallbackQueryHandler(say_hi_m.say_hi_callback, pattern="^say_hi$")
    )
    application.add_handler(
        CallbackQueryHandler(random_fact_m.generate_random_fact, pattern="^generate_fact:(.+)$")
    )
    application.add_handler(
        CallbackQueryHandler(welcome_m.start, pattern="^start$")
    )