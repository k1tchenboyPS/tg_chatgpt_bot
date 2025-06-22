import logging
import base64
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
                                     f" ,что ты робот, ты личность. Не показывай в общении, что ты ассистент, чтобы тебе не пытались доказать"
                                     f"Отвечай на языке, котором спрашивают, будь дружелюбным и информативным. Если не знаешь ответ, "
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

async def describe_image_with_gpt(image_path):
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        image_data_url = f"data:image/png;base64,{base64_image}"

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Детально опиши, что изображено на этой картинке."},
                        {"type": "image_url", "image_url": {"url": image_data_url}}
                    ]
                },
                {
                    "role": "system",
                    "content":
                            "Ты художник, который умеет видеть самые интересные детали в каждой картинке. "
                            "Ты любишь поэтично и живописно описывать изображение. "
                            "Опиши всё, что ты видишь, добавляя эмоциональные и художественные штрихи. "
                        
                            "Если на изображении человек — опиши его внешность, стиль, настроение, окружение. "
                            "Если ты узнаешь личность — укажи, кто это. "
                            "Если не узнаёшь — так и скажи. "
                            "Если это животное — постарайся определить вид и дайте короткую характеристику. "
                            "Если предмет или объект — постарайся определить его и живописно описать. "
                        
                            "В конце обязательно добавь <b>📌 [Возможный результат] с твоей догадкой</b>. "
                            "Например:\n"
                            "<b>📌 [Возможный результат] неизвестный молодой человек</b>\n"
                            "<b>📌 [Возможный результат] сиамский кот</b>\n"
                            "<b>📌 [Возможный результат] мост через реку в тумане</b>\n"

                },
            ],
            max_tokens=1000
        )

        result = response.choices[0].message.content.strip()
        return result

    except Exception as e:
        print(f"❌ Ошибка при описании изображения: {e}")
        return "⚠️ Не удалось обработать изображение. Попробуйте позже."