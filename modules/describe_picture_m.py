import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.openai_client import describe_image_with_gpt
from handlers.flag import Flags

logger = logging.getLogger(__name__)

CAPTION = (
    "📌 <b>Распознавание изображений:</b>\n\n"
    "ChatGPT может определить, что находится на изображении и описать это в текстовом виде.\n\n"
    "👇 Чтобы начать, отправьте любое изображение в чат."
)

async def des_picture_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()
    logger.warning("📥 des_picture_command вызван")
    return await des_picture_menu(update, context)

async def des_picture_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.warning("📥 des_picture_menu вызван")

        current_dir = os.path.dirname(__file__)
        photo_path = os.path.join(current_dir, "..", "pictures", "des_picture_menu.png")
        photo_path = os.path.abspath(photo_path)

        if update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.message.delete()
            chat = query.message.chat
        elif update.message:
            chat = update.message.chat
        else:
            logger.warning("❌ des_picture_menu: no valid update source")
            return ConversationHandler.END

        # Меню с кнопкой
        keyboard = [[InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await chat.send_photo(
            photo=photo_path,
            caption=CAPTION,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        logger.warning("✅ Возврат Flags.DESCRIBE_PICTURE")
        return Flags.DESCRIBE_PICTURE

    except Exception as e:
        logger.error(f"❌ Ошибка в des_picture_menu: {e}")
        return ConversationHandler.END

async def handle_picture(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning("📸 handle_picture вызван")

    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        path = f"/tmp/{file.file_id}.jpg"
        await file.download_to_drive(path)
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        processing_msg = await update.message.reply_text("🤔 Обрабатываю ваш запрос... ⏳")

        keyboard = [
            [InlineKeyboardButton("🖼 Начать сначала", callback_data="picture")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        response = await describe_image_with_gpt(path)
        await processing_msg.delete()
        await update.message.reply_text(
            f"🤖 <b>GPT смог определить:</b>\n\n{response}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        return ConversationHandler.END

    except Exception as e:
        logger.error(f"❌ Ошибка при обработке изображения: {e}")
        await update.message.reply_text("❌ Ошибка при обработке изображения.")
        return ConversationHandler.END
