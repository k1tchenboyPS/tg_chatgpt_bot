"""Модуль для обработки random fact"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.openai_client import get_random_fact
from services.gpt_promts import RANDOM_FACT_PROMPTS
import os

logger = logging.getLogger(__name__)

async def random_fact_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        current_dir = os.path.dirname(__file__)
        photo_path = os.path.join(current_dir, "..", "pictures", "random_fact.png")
        photo_path = os.path.abspath(photo_path)

        caption = "📌 <b>Выберите тип факта:</b>"
        keyboard = [
            [InlineKeyboardButton("🐍 Факты про Python", callback_data="generate_fact:python")],
            [InlineKeyboardButton("❔ Обычные факты о всем", callback_data="generate_fact:general")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.message.delete()
            chat = query.message.chat
        elif update.message:
            chat = update.message.chat
        else:
            logger.warning("random_fact_callback: no valid update source")
            return

        with open(photo_path, 'rb') as photo:
            await chat.send_photo(
                photo=photo,
                caption=caption,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.exception(f"Error in random_fact_callback: {e}")


async def generate_random_fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        _, fact_type = query.data.split(":", maxsplit=1)

        can_edit = query.message.text is not None

        if can_edit:
            await query.edit_message_text("⌛ Пытаюсь найти что-то интересное...")
            loading_msg = query
        else:
            await query.message.delete()
            loading_msg = await query.message.chat.send_message("⌛ Пытаюсь найти что-то интересное...")  # Message

        prompts = RANDOM_FACT_PROMPTS.get(fact_type, RANDOM_FACT_PROMPTS["general"])
        fact = await get_random_fact(
            sys_conten=prompts["system"],
            user_content=prompts["user"]
        )

        # Кнопки
        keyboard = [
            [InlineKeyboardButton("🎲 Новый факт", callback_data=f"generate_fact:{fact_type}")],
            [InlineKeyboardButton("🚪 Другой формат фактов", callback_data="random_fact")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message_text = f"🧠 <b>Теперь ты знаешь чуть больше:</b>\n\n{fact}"

        if isinstance(loading_msg, type(query)):
            await loading_msg.edit_message_text(
                message_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        else:
            await loading_msg.edit_text(
                message_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.error(f"Error in generate_random_fact: {e}")
        await query.message.chat.send_message("❌ Не удалось сгенерировать факт.")
