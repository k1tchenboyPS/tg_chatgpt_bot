import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.openai_client import get_chatgpt_response
import os
from handlers.reset_conversation_handler import reset_conv_handler

from handlers.flag import *
logger = logging.getLogger(__name__)


# WAITING_FOR_MESSAGE = 1

CAPTION = ("🤖 <b>Чат с GPT:</b>\n\n"
           "🤔<b>Не знаешь, с чего начать?</b>\n"
           "Напиши первое, что приходит в голову.\n"
           "💬 Любой вопрос, тема, идея — здесь всё приветствуется.\n"
           "💡 Пора включить воображение на максимум!")

async def gpt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    return await gpt_start(update, context)


async def gpt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # reset_conv_handler()
        # Сброс истории для текущего пользователя
        context.user_data["chat_history"] = []

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
        photo_path = os.path.join(current_dir, "..", "pictures", "gpt_menu.png")
        image_path = os.path.abspath(photo_path)

        keyboard = [
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

        logger.info(">>> gpt_start: entering WAITING_FOR_MESSAGE")
        # return WAITING_FOR_MESSAGE
        return Flags.WAITING_FOR_MESSAGE

    except Exception as e:
        logger.error(f"Ошибка при запуске ChatGPT интерфейса: {e}")
        error_text = "😔 Произошла ошибка при запуске ChatGPT интерфейса. Попробуйте позже."

        try:
            if update.callback_query:
                await update.callback_query.edit_message_text(error_text)
            else:
                await update.message.reply_text(error_text)
        except Exception as inner_e:
            logger.error(f"Не удалось отправить сообщение об ошибке: {inner_e}")

        return -1

    except Exception as e:
        logger.error(f"Ошибка при запуске ChatGPT интерфейса: {e}")
        error_text = "😔 Произошла ошибка при запуске ChatGPT интерфейса. Попробуйте позже."

        if update.callback_query:
            await update.callback_query.edit_message_text(error_text)
        else:
            await update.message.reply_text(error_text)
        return -1


async def handle_gpt_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщения пользователя для ChatGPT"""
    logger.info("chatgpt answer, not personality")
    try:
        user_message = update.message.text

        if user_message in ["/talk", "/gpt", "/start"]:
            logger.info(f"[GPT]: {user_message}")
            return reset_conv_handler()

        chat_history = context.user_data.get("chat_history", [])
        chat_history.append({"role": "user", "content": user_message})

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        processing_msg = await update.message.reply_text("🤔 Обрабатываю ваш запрос... ⏳")

        gpt_response = await get_chatgpt_response(chat_history)
        chat_history.append({"role": "assistant", "content": gpt_response})
        context.user_data["chat_history"] = chat_history

        keyboard = [
            [InlineKeyboardButton("💣 Начать сначала", callback_data="gpt")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await processing_msg.delete()
        await update.message.reply_text(
            f"🤖 <b>ChatGPT отвечает:</b>\n\n{gpt_response}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        # return WAITING_FOR_MESSAGE
        # return Flags.WAITING_FOR_MESSAGE
        return Flags.WAITING_FOR_MESSAGE

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения для ChatGPT: {e}")
        await update.message.reply_text(
            "😔 Произошла ошибка при обработке вашего сообщения. Попробуйте еще раз или вернитесь в главное меню."
        )
        # return WAITING_FOR_MESSAGE
        # return Flags.WAITING_FOR_MESSAGE
        return reset_conv_handler()