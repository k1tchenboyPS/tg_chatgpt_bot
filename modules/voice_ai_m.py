import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from services.openai_client import get_chatgpt_response
from handlers.flag import Flags
from services.whisper_client import transcribe_audio
from gtts import gTTS


logger = logging.getLogger(__name__)

CAPTION = (
    "📌 <b>Голосовой ChatGPT:</b>\n\n"
    "Вы можете пообщаться с ChatGPT с помощью голосовых сообщений.\n\n"
    "👇 Чтобы начать, отправьте голосовое сообщение в чат."
)

async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.chat_data.clear()
    logger.warning("📥 des_picture_command вызван")
    return await voice_menu(update, context)

async def voice_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logger.warning("📥 des_picture_menu вызван")

        current_dir = os.path.dirname(__file__)
        photo_path = os.path.join(current_dir, "..", "pictures", "voice_menu.png")
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

        keyboard = [[InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await chat.send_photo(
            photo=photo_path,
            caption=CAPTION,
            parse_mode='HTML',
            reply_markup=reply_markup
        )

        logger.warning("✅ Возврат Flags.DESCRIBE_PICTURE")
        return Flags.VOICE_CHAT

    except Exception as e:
        logger.error(f"❌ Ошибка в des_picture_menu: {e}")
        return ConversationHandler.END

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("🎙 Голосовое сообщение получено")

    try:
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            await query.message.delete()
            chat = query.message.chat
        elif update.message:
            chat = update.message.chat
        else:
            logger.warning("❌ handle_voice: нет источника update")
            return ConversationHandler.END

        menu_msg_id = context.chat_data.pop("menu_msg_id", None)
        if menu_msg_id:
            try:
                await context.bot.delete_message(chat_id=chat.id, message_id=menu_msg_id)
            except Exception as e:
                logger.warning(f"⚠️ Не удалось удалить старое меню: {e}")

        voice = update.message.voice
        file = await voice.get_file()
        voice_path = f"/tmp/{file.file_id}.ogg"
        await file.download_to_drive(voice_path)

        processing_msg = await update.message.reply_text(
            "🎙 Настраиваю микрофон и нагружаю процессор, пытаясь сформулировать предложение..."
        )

        wav_path = voice_path.replace(".ogg", ".wav")
        os.system(f"ffmpeg -i {voice_path} -ar 16000 -ac 1 {wav_path}")

        text = await transcribe_audio(wav_path)
        logger.info(f"📝 Распознанный текст: {text}")

        chat_history = context.user_data.get("chat_history", [])
        chat_history.append({"role": "user", "content": text})

        gpt_response = await get_chatgpt_response(chat_history)
        logger.info(f"GPT ответ: {gpt_response}")

        chat_history.append({"role": "assistant", "content": gpt_response})
        context.user_data["chat_history"] = chat_history

        tts = gTTS(gpt_response, lang="ru")
        tts_path = f"/tmp/response_{file.file_id}.mp3"
        tts.save(tts_path)

        await processing_msg.delete()

        with open(tts_path, "rb") as voice_reply:
            await update.message.reply_voice(voice=voice_reply)

        keyboard = [
            [InlineKeyboardButton("🎧 Начать сначала", callback_data="voice")],
            [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        menu_message = await chat.send_message(
            "<b>📌 Голосовой ChatGPT:</b>\n\n"
            "Отправьте голосовое сообщение, чтобы продолжить.",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        context.chat_data["menu_msg_id"] = menu_message.message_id

        for path in [voice_path, wav_path, tts_path]:
            try:
                os.remove(path)
            except FileNotFoundError:
                pass

        return Flags.VOICE_CHAT

    except Exception as e:
        logger.error(f"❌ Ошибка в голосовом диалоге: {e}")
        await update.message.reply_text("⚠️ Ошибка при обработке голосового сообщения.")
        return ConversationHandler.END