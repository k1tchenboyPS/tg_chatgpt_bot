from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
from modules import chatgpt_interface_m as chat
from modules import personality_chat_m as pers_chat
from modules import welcome_m, quiz_m
from modules import describe_picture_m
import logging
from handlers.flag import *
import asyncio
from telegram.ext import ContextTypes
from telegram import Update

logger = logging.getLogger(__name__)
async def exit_and_prompt_gpt(update, context):
    await update.message.reply_text("😔 Мне пришлось отменить твою команду,"
                                    " чтобы завершить предыдущий диалог.\n\n"
                                    "🤖 Повтори команду /gpt.")
    return ConversationHandler.END

async def exit_and_prompt_talk(update, context):
    await update.message.reply_text("😔 Мне пришлось отменить твою команду,"
                                    " чтобы завершить предыдущий диалог.\n\n"
                                    "💬 Повтори команду /talk.")
    return ConversationHandler.END

async def exit_and_prompt_quiz(update, context):
    await update.message.reply_text("😔 Мне пришлось отменить твою команду,"
                                    " чтобы завершить предыдущий диалог.\n\n"
                                    "🧠 Повтори команду /quiz.")
    return ConversationHandler.END

# async def des_picture_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     logger.warning("📥 des_picture_command вызван")
#
#     key = _conversation_session_key(update, context)
#     logger.warning(f"🔑 CONV SESSION KEY = {key}")
#
#     context.user_data.clear()
#     context.chat_data.clear()
#
#     return await des_picture_menu(update, context)
def listing(application):
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("gpt", chat.gpt_command),
            CallbackQueryHandler(chat.gpt_command, pattern="^gpt$"),
        ],
        states={
            Flags.WAITING_FOR_MESSAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, chat.handle_gpt_message)
            ]
        },
        fallbacks=[
            CommandHandler("start", welcome_m.start),
            CommandHandler("gpt", exit_and_prompt_gpt),
            CommandHandler("talk", exit_and_prompt_talk),
            CommandHandler("quiz", exit_and_prompt_quiz),
            CallbackQueryHandler(welcome_m.start, pattern="^start$")
        ],
        per_chat=True
    )

    personality_mes_handler = ConversationHandler(
        entry_points=[
            CommandHandler("talk", pers_chat.per_chat_command),
            CallbackQueryHandler(pers_chat.per_chat_start, pattern="^person_talk:(.+)$")
        ],
        states={
            Flags.PERS_CHAT_FLAG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, pers_chat.handle_gpt_message)
            ]
        },
        fallbacks=[
            CommandHandler("start", welcome_m.start),
            CommandHandler("gpt", exit_and_prompt_gpt),
            CommandHandler("talk", exit_and_prompt_talk),
            CommandHandler("quiz", exit_and_prompt_quiz),
            CallbackQueryHandler(welcome_m.start, pattern="^start$")
        ],
        per_chat=True
    )

    quiz_conversation = ConversationHandler(
        entry_points=[
            CommandHandler("quiz", quiz_m.quiz_command),
            CallbackQueryHandler(quiz_m.quiz_start, pattern="^quiz$"),
            CallbackQueryHandler(quiz_m.quiz_start, pattern="^quiz_interface$")
        ],
        states={
            Flags.SELECTING_TOPIC: [
                CallbackQueryHandler(quiz_m.topic_selected, pattern="^quiz_topic_")
            ],
            Flags.ANSWERING_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_m.handle_quiz_answer),
                CallbackQueryHandler(quiz_m.handle_quiz_callback,
                                     pattern="^(quiz_continue_.*|quiz_change_topic|quiz_finish)$")
            ],
        },
        fallbacks=[
            CommandHandler("start", welcome_m.start),
            CommandHandler("gpt", exit_and_prompt_gpt),
            CommandHandler("talk", exit_and_prompt_talk),
            CallbackQueryHandler(welcome_m.start, pattern="^start$"),
            CommandHandler("quiz", exit_and_prompt_quiz)
        ],
        per_chat=True
    )

    describe_picture_handler = ConversationHandler(
        entry_points=[
            CommandHandler("picture", describe_picture_m.des_picture_command),
            CallbackQueryHandler(describe_picture_m.des_picture_command, pattern="^picture$"),
        ],
        states={
            Flags.DESCRIBE_PICTURE: [
                MessageHandler(filters.PHOTO, describe_picture_m.handle_picture)
            ]
        },
        fallbacks=[
            CommandHandler("start", welcome_m.start),
            CallbackQueryHandler(welcome_m.start, pattern="^start$")
        ],
        per_chat=True,
        allow_reentry=True
    )

    application.add_handler(conv_handler)
    application.add_handler(personality_mes_handler)
    application.add_handler(quiz_conversation)
    application.add_handler(describe_picture_handler)


