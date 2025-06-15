from modules import welcome_m, random_fact_m, chatgpt_interface_m
from telegram.ext import CommandHandler
import logging

logger = logging.getLogger(__name__)

def listing(application):
    application.add_handler(CommandHandler("start", welcome_m.start))
    application.add_handler(CommandHandler("random", random_fact_m.random_fact_callback))
    application.add_handler(CommandHandler("gpt", chatgpt_interface_m.gpt_command))


