import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

"""
logging — модуль для логирования.
Update — объект, содержащий информацию о входящем сообщении или действии пользователя.
InlineKeyboardButton, InlineKeyboardMarkup — кнопки, которые отображаются под сообщением.
ContextTypes — тип контекста
"""

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start handler"""
    keyboard=[
        [
            InlineKeyboardButton("🎲 Факт", callback_data="random_fact"),
            InlineKeyboardButton("😎 Привет!", callback_data="say_hi")
        ],
        [InlineKeyboardButton("❌ В процессе", callback_data="random_fact")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "<b>Добро пожаловать в меню бота!🙋</b>"
    )

    if update.message:
        # /start — это обычное текстовое сообщение
        await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

    # await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)
