import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

"""
logging — модуль для логирования.
Update — объект, содержащий информацию о входящем сообщении или действии пользователя.
InlineKeyboardButton, InlineKeyboardMarkup — кнопки, которые отображаются под сообщением.
ContextTypes — тип контекста
"""

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start handler"""
    context.user_data.clear()
    return_code = ConversationHandler.END
    keyboard = [
        [
            InlineKeyboardButton("🎲 Факт", callback_data="random_fact"),
            InlineKeyboardButton("🤖 GPT-чат", callback_data="gpt")
        ],
        [InlineKeyboardButton("💬 Общение с личностями", callback_data="talk")],
        [InlineKeyboardButton("🧠 Играть в quiz", callback_data="quiz")],
        [InlineKeyboardButton("🖼 Распознавание изображений", callback_data="picture")],
        [InlineKeyboardButton("🎧 Голосовой ChatGPT", callback_data="voice")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = "<b>Добро пожаловать в меню бота!🙋</b>"

    if update.message:
        await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

    elif update.callback_query:
        query = update.callback_query
        await query.answer()

        can_edit = query.message and query.message.text is not None

        if can_edit:
            await query.edit_message_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)
        else:
            await query.message.delete()
            await query.message.chat.send_message(welcome_text, parse_mode='HTML', reply_markup=reply_markup)
    return return_code