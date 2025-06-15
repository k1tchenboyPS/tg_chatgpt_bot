import logging
from openai import AsyncOpenAI
from config import GPT_TOKEN

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=GPT_TOKEN)

async def get_random_fact(sys_conten=None, user_content=None):
    try:
        if sys_conten is None:
            sys_conten = (
                "Ты — суперэрудированный AI, прочитавший миллионы книг, знаешь редкие, удивительные факты "
                "по истории, науке, технологиям и жизни. Ты не пишешь вступлений и не используешь шаблоны "
                "вроде 'вот интересный факт'. Ты сразу выдаёшь факт — коротко, мощно, удивительно. "
                "Без объяснений, без размытой формулировки. Никаких слов типа 'возможно', 'вероятно'. "
                "Факт должен быть конкретным, новым и необычным."
            )

        if user_content is None:
            user_content = (
                "Мне нужен уникальный и редкий факт, который прямо взорвёт мозг. "
                "Не пиши ничего кроме самого факта. Ни вступлений, ни объяснений."
            )

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_conten},
                {"role": "user", "content": user_content}
            ],
            max_tokens=200,
            temperature=0.8
        )

        fact = response.choices[0].message.content.strip()
        logger.info("Факт успешно получен от OpenAI")
        return fact

    except Exception as e:
        logger.error(f"Error while trying to get response from chatGPT: {e}")
        return "⚠️ Не удалось получить факт"

async def get_chatgpt_response(chat_history: list[dict]):
    """Получить ответ от ChatGPT с учетом истории сообщений"""
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты полезный помощник. Отвечай на русском языке, будь дружелюбным и информативным. Если не знаешь ответ, честно об этом скажи."}
            ] + chat_history,
            max_tokens=1000,
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()
        logger.info("Ответ успешно получен от OpenAI")
        return answer

    except Exception as e:
        logger.error(f"Ошибка при получении ответа от OpenAI: {e}")
        return "😔 Извините, произошла ошибка при обращении к ChatGPT. Попробуйте позже!"

async def personality_chatgpt_response(chat_history: list[dict], chose_personal_conten=None):
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                         {"role": "system",
                          "content": f"Ты {chose_personal_conten}. Полносью превратись в личность человека. Ты должен забыть"
                                     f", что ты робот, ты личность. Не показывай в общении, что ты ассистент, чтобы тебе не пытались доказать"
                                     f"Отвечай на русском языке, будь дружелюбным и информативным. Если не знаешь ответ, "
                                     f"честно об этом скажи."}
                     ] + chat_history,
            max_tokens=1000,
            temperature=0.7
        )

        answer = response.choices[0].message.content.strip()
        logger.info("Ответ успешно получен от OpenAI")
        return answer

    except Exception as e:
        logger.error(f"Ошибка при получении ответа от OpenAI: {e}")
        return "😔 Извините, произошла ошибка при обращении к ChatGPT. Попробуйте позже!"