import logging
from openai import AsyncOpenAI
from config import GPT_TOKEN

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=GPT_TOKEN)

async def get_random_fact():
    try:
        response = await client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Ты — суперэрудированный AI, прочитавший миллионы книг, знаешь редкие, удивительные факты"
                               "по истории, науке, технологиям и жизни. Ты не пишешь вступлений и не используешь шаблоны"
                               "вроде 'вот интересный факт'. Ты сразу выдаёшь факт — коротко, мощно, удивительно."
                               "Без объяснений, без размытой формулировки. Никаких слов типа 'возможно', 'вероятно'."
                               "Факт должен быть конкретным, новым и необычным."

                },
                {
                    "role": "user",
                    "content": "Мне нужен уникальный и редкий факт, который прямо взорвёт мозг."
                                "Не пиши ничего кроме самого факта. Ни вступлений, ни объяснений."
                }
            ],
            max_tokens=200,
            temperature=0.8
        )

        fact = response.choices[0].message.content.strip()
        logger.info("Факт успешно получен от OpenAI")
        return fact

    except Exception as e:
        logger.error(f"Error while trying to get response from chatGPT: {e}")

