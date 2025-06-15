from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from modules import chatgpt_interface_m as chat
import logging

logger = logging.getLogger(__name__)

def listing(application):
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("gpt", chat.gpt_command),
            CallbackQueryHandler(chat.gpt_command, pattern="^gpt$")
        ],
        states={
            chat.WAITING_FOR_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat.handle_gpt_message)
            ]
        },
        fallbacks=[
        ],
        per_chat=True
    )

    application.add_handler(conv_handler)
