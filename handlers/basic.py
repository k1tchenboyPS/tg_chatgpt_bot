import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start handler"""
    keyboard=[
        [InlineKeyboardButton("Random fact", callback_data="random_fact")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "<b>Hi, this is my frist Telegram Bot</b>"
    )

    logger.info("hi")

    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

