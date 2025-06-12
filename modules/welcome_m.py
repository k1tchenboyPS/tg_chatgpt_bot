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
            InlineKeyboardButton("✅ Random fact", callback_data="random_fact"),
            InlineKeyboardButton("✅ Say Hi", callback_data="say_hi")
        ],
        [InlineKeyboardButton("❌ Random fact", callback_data="random_fact")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "<b>Bot menu, free to choose any options!</b>"
    )

    logger.info("hi")

    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)
