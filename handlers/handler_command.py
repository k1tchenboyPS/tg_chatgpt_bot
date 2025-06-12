from modules import welcome_m
from telegram.ext import CommandHandler
import logging

logger = logging.getLogger(__name__)

def listing(application):
    application.add_handler(CommandHandler("start", welcome_m.start))

