import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.openai_client import personality_chatgpt_response
import os
from handlers.flag import *

logger = logging.getLogger(__name__)

CAPTION = (
    "📌 <b>Общение с личностями:</b>\n\n"
    "Выбирайте из галереи великих умов — от гениев науки до визионеров бизнеса.\n\n"
    "💬 <b>Они готовы делиться:</b>\n"
    "• Мудростью\n"
    "• Идеями\n"
    "• Принципами, которые меняли мир\n"
    "• Ответами на любые ваши вопросы\n\n"
    "👇 Нажмите на кнопку ниже, чтобы выбрать личность и начать диалог."
)

TESLA_CAPTION = (
    "🔬 <b>Общение с Николой Теслой:</b>\n\n"
    "Никола Тесла — изобретатель и инженер, чьи открытия в области электричества, магнетизма и беспроводной передачи"
    " энергии изменили ход истории.\n\n"
    "✍️ Напиши свой вопрос в чат, чтобы начать общение."
)

JOBS_CAPTION = (
    "🍏 <b>Общение со Стивом Джобсом:</b>\n\n"
    "Стив Джобс — основатель Apple и один из самых влиятельных визионеров в мире технологий,"
    " известный своим стремлением к простоте, дизайну и силе идей.\n\n"
    "✍️ Напиши свой вопрос в чат, чтобы начать общение."
)
PERELMAN_CAPTION = (
    "🧠 <b>Общение с Григорием Перельманом:</b>\n\n"
    "Григорий Перельман — гениальный математик, решивший гипотезу Пуанкаре и прославившийся своим отказом от наград,"
    " славы и компромиссов с истиной.\n\n"
    "✍️ Напиши свой вопрос в чат, чтобы начать общение."
)

async def per_chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    return await per_chat_menu(update, context)

async def per_chat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["chat_history"] = []
        context.user_data.pop("person_caption", None)

        if update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.message.delete()
            chat = query.message.chat
        elif update.message:
            chat = update.message.chat
        else:
            logger.warning("gpt_start: no valid update source")
            return -1

        current_dir = os.path.dirname(__file__)
        photo_path = os.path.join(current_dir, "..", "pictures", "personality_menu.png")
        image_path = os.path.abspath(photo_path)
        keyboard = [
            [
                InlineKeyboardButton("🔬 Никола Тесла", callback_data="person_talk:tesla"),
                InlineKeyboardButton("🍏 Стив Джобс", callback_data="person_talk:jobs")
            ],
            [InlineKeyboardButton("🧠 Григорий Перельман", callback_data="person_talk:perelman")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await chat.send_photo(
                    photo=photo,
                    caption=CAPTION,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
        else:
            await chat.send_message(
                text=CAPTION,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

    except Exception as e:
        logger.error(f"Ошибка при старте меню с личностями: {e}")

async def per_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_name = None, caption = None):
    try:
        context.user_data.clear()
        context.user_data["chat_history"] = []

        query = update.callback_query
        await query.answer()

        _, personality_type = query.data.split(":", maxsplit=1)

        if personality_type == "tesla" and photo_name is None and caption is None:
            photo_name = "tesla_photo.png"
            caption = TESLA_CAPTION
            person_name = "🔬 Никола Тесла"
            logger.info("Выбрали Теслу")
        elif personality_type == "jobs" and photo_name is None and caption is None:
            photo_name = "jobs_photo.png"
            caption = JOBS_CAPTION
            person_name = "🍏 Стив Джобс"
            logger.info("Выбрали Джобса")
        elif personality_type == "perelman" and photo_name is None and caption is None:
            photo_name = "perelman_photo.png"
            caption = PERELMAN_CAPTION
            person_name = "🧠 Григорий Перельман"
            logger.info("Выбрали Перельмана")
        else:
            logger.info("Личность уже была выбрана")

        context.user_data["person_caption"] = caption
        context.user_data["person_name"] = person_name

        current_dir = os.path.dirname(__file__)
        photo_path = os.path.join(current_dir, "..", "pictures", photo_name)
        photo_path = os.path.abspath(photo_path)

        if update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.message.delete()
            chat = query.message.chat
        elif update.message:
            chat = update.message.chat
        else:
            logger.warning("person_talk_start: no valid update source")
            return -1

        keyboard = [
            [InlineKeyboardButton("💬 Выбрать другую личность", callback_data="talk")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                await chat.send_photo(
                    photo=photo,
                    caption=caption,
                    parse_mode='HTML',
                    reply_markup=reply_markup
                )
        else:
            await chat.send_message(
                text=caption,
                parse_mode='HTML',
                reply_markup=reply_markup
            )

        logger.info(">>> gpt_start: entering why WAITING_FOR_MESSAGE")
        return Flags.PERS_CHAT_FLAG


    except Exception as e:
        logger.error(f"Ошибка при запуске ChatGPT интерфейса: {e}")

async def handle_gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE, caption=None):
    logger.info("handle_gpt_message")
    caption = context.user_data.get("person_caption")
    person_name = context.user_data.get("person_name")

    try:
        user_message = update.message.text

        chat_history = context.user_data.get("chat_history", [])
        chat_history.append({"role": "user", "content": user_message})

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        processing_msg = await update.message.reply_text("🤔 Обрабатываю ваш запрос... ⏳")
        gpt_response = await personality_chatgpt_response(chat_history, caption)
        chat_history.append({"role": "assistant", "content": gpt_response})
        context.user_data["chat_history"] = chat_history
        logger.info(f"processing_msg: {user_message}")

        keyboard = [
            [InlineKeyboardButton("🚪 Выбрать другую личность", callback_data="talk")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await processing_msg.delete()
        await update.message.reply_text(
            f"<b>{person_name} отвечает:</b>\n\n{gpt_response}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        logger.info(f"processing_msg: {user_message}")
        return Flags.PERS_CHAT_FLAG


    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения для ChatGPT: {e}")
        await update.message.reply_text(
            "😔 Произошла ошибка при обработке вашего сообщения. Попробуйте еще раз или вернитесь в главное меню."
        )
        return Flags.PERS_CHAT_FLAG