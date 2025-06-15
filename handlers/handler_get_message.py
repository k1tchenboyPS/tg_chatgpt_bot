from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from modules import chatgpt_interface_m as chat
from modules import personality_chat_m as pers_chat
import logging

logger = logging.getLogger(__name__)
""""Нужно дописать fallbck для возрата в меню"""
def listing(application):
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("gpt", chat.gpt_command),
            CallbackQueryHandler(chat.gpt_command, pattern="^gpt$"),
            CallbackQueryHandler(pers_chat.per_chat_start, pattern="^person_talk:(.+)$")
        ],
        states={
            chat.WAITING_FOR_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat.handle_gpt_message)
            ],
            pers_chat.WAITING_FOR_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, pers_chat.handle_gpt_message)
            ]
        },
        fallbacks=[
        ],
        per_chat=True
    )

    application.add_handler(conv_handler)
