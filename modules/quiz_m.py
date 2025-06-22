import logging
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.openai_client import get_chatgpt_response
from services.quiz_topics import get_quiz_topics_keyboard, get_quiz_topic_data, get_quiz_continue_keyboard
from handlers.flag import *
logger = logging.getLogger(__name__)

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('Обрабатываю нажатие на /quiz')
    return await quiz_start(update, context)

async def quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info('Обрабатываю quiz_start')
    try:
        current_dir = os.path.dirname(__file__)
        photo_path = os.path.join(current_dir, "..", "pictures", "quiz_menu.png")
        photo_path = os.path.abspath(photo_path)
        message_text = (
            "🧠 <b>Квиз - проверь свои знания!</b>\n\n"
            "Выберите тему для квиза:\n\n"
            "💻 <b>Программирование</b> - вопросы о коде и технологиях\n"
            "🏛️ <b>История</b> - исторические факты и события\n"
            "🔬 <b>Наука</b> - физика, химия, биология\n"
            "🌍 <b>География</b> - страны, столицы, природа\n"
            "🎬 <b>Кино</b> - фильмы и актеры\n\n"
            "Выберите тему:"
        )

        keyboard = get_quiz_topics_keyboard()

        if 'quiz_score' not in context.user_data:
            context.user_data['quiz_score'] = 0
            context.user_data['quiz_total'] = 0

        if update.callback_query:
            if os.path.exists(photo_path):
                await update.callback_query.message.delete()
                with open(photo_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=update.callback_query.message.chat_id,
                        photo=photo,
                        caption=message_text,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
            else:
                await update.callback_query.edit_message_text(
                    message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
            await update.callback_query.answer()

        else:
            if os.path.exists(photo_path):
                with open(photo_path, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo,
                        caption=message_text,
                        parse_mode='HTML',
                        reply_markup=keyboard
                    )
            else:
                await update.message.reply_text(
                    message_text,
                    parse_mode='HTML',
                    reply_markup=keyboard
                )
        logger.info("return >> Flags.SELECTING_TOPIC")
        return Flags.SELECTING_TOPIC

    except Exception as e:
        logger.error(f"Ошибка при запуске квиза: {e}")
        error_text = "😔 Произошла ошибка при запуске квиза. Попробуйте позже."

        if update.callback_query:
            await update.callback_query.edit_message_text(error_text)
        else:
            await update.message.reply_text(error_text)

        return -1


async def topic_selected(update: Update, context: ContextTypes.DEFAULT_TYPE, topic_key: str = None):
    query = update.callback_query
    await query.answer()

    try:
        if not topic_key:
            topic_key = query.data.replace("quiz_topic_", "")

        topic_data = get_quiz_topic_data(topic_key)

        if not topic_data:
            if query.message.photo:
                await query.edit_message_caption("❌ Ошибка: тема не найдена.")
            else:
                await query.edit_message_text("❌ Ошибка: тема не найдена.")
            return -1

        context.user_data['current_quiz_topic'] = topic_key
        context.user_data['quiz_topic_data'] = topic_data
        processing_text = f"{topic_data['emoji']} Генерирую вопрос по теме {topic_data['name']}... ⏳"
        if query.message.photo:
            await query.edit_message_caption(processing_text, parse_mode='HTML')
        else:
            await query.edit_message_text(processing_text, parse_mode='HTML')

        chat_history = context.user_data.get("chat_history", [])
        chat_history.append({"role": "user", "content": topic_data['prompt']})

        question_raw = await get_chatgpt_response(chat_history)
        question = re.sub(r'Правильный ответ.*', '', question_raw, flags=re.IGNORECASE).strip()
        context.user_data['current_question'] = question

        correct_answer = extract_correct_answer(question_raw)
        context.user_data['correct_answer'] = correct_answer

        message_text = (
            f"📌 <b>Квиз: {topic_data['name']}</b>\n\n"
            f"{question}\n\n"
            f"📊 <b>Счет:</b> {context.user_data['quiz_score']}/{context.user_data['quiz_total']}\n\n"
            "✍️ Напишите ваш ответ (A, B, C или D):"
        )

        if query.message.photo:
            await query.edit_message_caption(
                caption=message_text,
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(
                text=message_text,
                parse_mode='HTML'
            )
        logger.info(">>> returning ANSWERING_QUESTION IN TOPIC SELECTED")
        return Flags.ANSWERING_QUESTION

    except Exception as e:
        logger.error(f"Ошибка при выборе темы квиза: {e}")
        try:
            if query.message.photo:
                await query.edit_message_caption("😔 Произошла ошибка при генерации вопроса. Попробуйте еще раз.")
            else:
                await query.edit_message_text("😔 Произошла ошибка при генерации вопроса. Попробуйте еще раз.")
        except Exception:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="😔 Произошла ошибка при генерации вопроса. Попробуйте еще раз."
            )
        return -1


async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(">>> handle_quiz_answer TRIGGERED")
    try:
        user_answer = update.message.text.strip().upper()
        correct_answer = context.user_data.get('correct_answer', '').upper()
        topic_data = context.user_data.get('quiz_topic_data')
        current_question = context.user_data.get('current_question', '')

        if not topic_data or not correct_answer:
            await update.message.reply_text(
                "❌ Произошла ошибка: данные квиза не найдены. Используйте /quiz для начала."
            )
            return -1

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        is_correct = user_answer == correct_answer

        context.user_data['quiz_total'] += 1
        if is_correct:
            context.user_data['quiz_score'] += 1

        processing_msg = await update.message.reply_text(
            f"{topic_data['emoji']} Проверяю ответ... ⏳"
        )

        analysis_prompt = f"""Пользователь ответил '{user_answer}' на вопрос:
        {current_question}

        Правильный ответ: {correct_answer}

        Дай краткое объяснение (2-3 предложения), почему ответ правильный или неправильный, и интересный факт по теме."""

        chat_history = context.user_data.get("chat_history", [])
        chat_history.append({"role": "user", "content": analysis_prompt + "Ты эксперт по квизам, объясняешь ответы понятно и интересно."})
        detailed_response = await get_chatgpt_response(chat_history)

        if is_correct:
            result_text = f"✅ <b>Правильно!</b>\n\n{detailed_response}"
        else:
            result_text = f"❌ <b>Неправильно!</b>\n\nПравильный ответ: <b>{correct_answer}</b>\n\n{detailed_response}"

        keyboard = get_quiz_continue_keyboard(context.user_data['current_quiz_topic'])

        await processing_msg.delete()
        await update.message.reply_text(
            f"{topic_data['emoji']} <b>Результат квиза</b>\n\n"
            f"{result_text}\n\n"
            f"📊 <b>Ваш счет:</b> {context.user_data['quiz_score']}/{context.user_data['quiz_total']}",
            parse_mode='HTML',
            reply_markup=keyboard
        )
        logger.info(">>> returning ANSWERING_QUESTION")
        return Flags.ANSWERING_QUESTION

    except Exception as e:
        logger.error(f"Ошибка при обработке ответа квиза: {e}")
        await update.message.reply_text(
            "😔 Произошла ошибка при проверке ответа. Попробуйте еще раз."
        )
        logger.info(">>> returning ANSWERING_QUESTION")
        return Flags.ANSWERING_QUESTION


async def handle_quiz_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        logger.info(f"[DATA] {query.data}")
        if query.data.startswith("quiz_continue_"):
            topic_key = query.data.replace("quiz_continue_", "")
            return await topic_selected(update, context, topic_key=topic_key)

        elif query.data == "quiz_change_topic":
            return await quiz_start(update, context)

        elif query.data == "quiz_finish":
            score = context.user_data.get('quiz_score', 0)
            total = context.user_data.get('quiz_total', 0)

            if total > 0:
                percentage = round((score / total) * 100)
                if percentage >= 80:
                    emoji = "🏆"
                    grade = "Отлично!"
                elif percentage >= 60:
                    emoji = "🥈"
                    grade = "Хорошо!"
                elif percentage >= 40:
                    emoji = "🥉"
                    grade = "Неплохо!"
                else:
                    emoji = "📚"
                    grade = "Есть куда расти!"
            else:
                percentage = 0
                emoji = "🤔"
                grade = "Попробуйте еще раз!"

            final_text = (
                f"{emoji} <b>Квиз завершен!</b>\n\n"
                f"📊 <b>Финальный результат:</b>\n"
                f"Правильных ответов: {score} из {total}\n"
                f"Процент: {percentage}%\n\n"
                f"<b>{grade}</b>\n\n"
                "Спасибо за участие! 🎉"
            )

            context.user_data.pop('quiz_score', None)
            context.user_data.pop('quiz_total', None)
            context.user_data.pop('current_quiz_topic', None)
            context.user_data.pop('quiz_topic_data', None)
            context.user_data.pop('current_question', None)
            context.user_data.pop('correct_answer', None)

            keyboard = [
                [InlineKeyboardButton("🧠 Новый квиз", callback_data="quiz_interface")],
                [InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                final_text,
                parse_mode='HTML',
                reply_markup=reply_markup
            )
            return -1

    except Exception as e:
        logger.error(f"Ошибка в quiz callback: {e}")
        await query.edit_message_text("😔 Произошла ошибка. Попробуйте еще раз.")
        return -1

    return Flags.ANSWERING_QUESTION


def extract_correct_answer(question_text):
    try:
        lines = question_text.split('\n')
        for line in lines:
            if 'правильный ответ' in line.lower():
                match = re.search(r'[ABCD]', line.upper())
                if match:
                    return match.group()

        match = re.search(r'ответ:\s*([ABCD])', question_text.upper())
        if match:
            return match.group(1)

        return 'A'
    except Exception as e:
        logger.error(f"Ошибка при извлечении правильного ответа: {e}")
        return 'A'