"""Модуль для обработки random fact"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.openai_client import get_random_fact
from services.gpt_promts import RANDOM_FACT_PROMPTS

logger = logging.getLogger(__name__)

async def random_fact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            show_random_choice = query.edit_message_text
        else:
            show_random_choice = update.message.reply_text

        keyboard = [
            [InlineKeyboardButton("⭐ Обычные факты о всем", callback_data="generate_fact:general")],
            [InlineKeyboardButton("🔥 Факты, если у тебя выгорание", callback_data="generate_fact:burnout")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await show_random_choice("📌 Выберите случайный факт!", reply_markup=reply_markup)
    except Exception as e:
        logger.info(f"Error in random_fact_callback: {e}")

async def generate_random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        callback_data = query.data
        _, fact_type = callback_data.split(":", maxsplit=1)

        loading_msg = await query.edit_message_text("⌛ Пытаюсь найти что-то интересное...")

        prompts = RANDOM_FACT_PROMPTS.get(fact_type, RANDOM_FACT_PROMPTS["general"])
        fact = await get_random_fact(
            sys_conten=prompts["system"],
            user_content=prompts["user"]
        )

        keyboard = [
            [InlineKeyboardButton("🎲 Новый факт ", callback_data=f"generate_fact:{fact_type}")],
            [InlineKeyboardButton("🚪 Другой формат фактов", callback_data="random_fact")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await loading_msg.edit_text(
            f"🧠 <b>Теперь ты знаешь чуть больше: </b>\n\n{fact}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Error while trying to generate fact in first_random_choice: {e}")
        await query.edit_message_text("Fail, sorry, i can not generate a random fact :(")

