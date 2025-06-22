from modules import welcome_m, random_fact_m, chatgpt_interface_m, personality_chat_m, quiz_m, describe_picture_m, voice_ai_m
from telegram.ext import CommandHandler, ConversationHandler
import logging

logger = logging.getLogger(__name__)

def listing(application):
    application.add_handler(CommandHandler("start", welcome_m.start))
    application.add_handler(CommandHandler("random", random_fact_m.random_fact_callback))
    application.add_handler(CommandHandler("gpt", chatgpt_interface_m.gpt_command))
    application.add_handler(CommandHandler("talk", personality_chat_m.per_chat_command))
    application.add_handler(CommandHandler("quiz", quiz_m.quiz_command))
    application.add_handler(CommandHandler("picture", describe_picture_m.des_picture_command))
    application.add_handler(CommandHandler("voice", voice_ai_m.voice_command))
