"""Модуль для обработки random fact"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.openai_client import get_random_fact

logger = logging.getLogger(__name__)

async def random_fact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("✅ BEZ VARIANTOV", callback_data="fact_number_one"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("🧠 Chose random fact style!", reply_markup=reply_markup)

async def first_random_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        loading_msg = await query.edit_message_text("Trying to generate fact... Wait!")
        fact = await get_random_fact()
        keyboard = [
            [InlineKeyboardButton("O_O Another fact", callback_data="fact_number_one")],
            [InlineKeyboardButton("Back to menu", callback_data="start")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await loading_msg.edit_text(
            f"🧠 <b>Fact: </b>\n\n{fact}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error while trying to generate fact in first_random_choice: {e}")
        await query.edit_message_text("Fail, sorry, i can not generate a random fact :(")

