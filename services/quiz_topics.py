from telegram import InlineKeyboardButton, InlineKeyboardMarkup

QUIZ_TOPICS = {
    "programming": {
        "name": "💻 Программирование",
        "emoji": "💻",
        "prompt": """Ты создаешь вопросы для квиза по программированию. 
Создай один интересный вопрос средней сложности с 4 вариантами ответа (A, B, C, D). 
Укажи правильный ответ в конце. 
Формат:
Вопрос: [твой вопрос]
A) [вариант 1]
B) [вариант 2] 
C) [вариант 3]
D) [вариант 4]
Правильный ответ: [буква]"""
    },
    "history": {
        "name": "🏛️ История",
        "emoji": "🏛️",
        "prompt": """Ты создаешь вопросы для квиза по истории.
Создай один интересный исторический вопрос средней сложности с 4 вариантами ответа (A, B, C, D).
Укажи правильный ответ в конце.
Формат:
Вопрос: [твой вопрос]
A) [вариант 1]
B) [вариант 2]
C) [вариант 3] 
D) [вариант 4]
Правильный ответ: [буква]"""
    },
    "science": {
        "name": "🔬 Наука",
        "emoji": "🔬",
        "prompt": """Ты создаешь вопросы для квиза по науке (физика, химия, биология).
Создай один интересный научный вопрос средней сложности с 4 вариантами ответа (A, B, C, D).
Укажи правильный ответ в конце.
Формат:
Вопрос: [твой вопрос]
A) [вариант 1]
B) [вариант 2]
C) [вариант 3]
D) [вариант 4] 
Правильный ответ: [буква]"""
    },
    "geography": {
        "name": "🌍 География",
        "emoji": "🌍",
        "prompt": """Ты создаешь вопросы для квиза по географии.
Создай один интересный географический вопрос средней сложности с 4 вариантами ответа (A, B, C, D).
Укажи правильный ответ в конце.
Формат:
Вопрос: [твой вопрос]
A) [вариант 1]
B) [вариант 2]
C) [вариант 3]
D) [вариант 4]
Правильный ответ: [буква]"""
    },
    "movies": {
        "name": "🎬 Кино",
        "emoji": "🎬",
        "prompt": """Ты создаешь вопросы для квиза о кино и фильмах.
Создай один интересный вопрос о фильмах средней сложности с 4 вариантами ответа (A, B, C, D).
Укажи правильный ответ в конце.
Формат:
Вопрос: [твой вопрос]
A) [вариант 1]
B) [вариант 2]
C) [вариант 3]
D) [вариант 4]
Правильный ответ: [буква]"""
    }
}


def get_quiz_topics_keyboard():
    """Возвращает клавиатуру с темами квиза"""
    keyboard = []
    for topic_key, topic_data in QUIZ_TOPICS.items():
        keyboard.append([InlineKeyboardButton(topic_data["name"], callback_data=f"quiz_topic_{topic_key}")])

    keyboard.append([InlineKeyboardButton("🏠 Вернуться в меню", callback_data="start")])
    return InlineKeyboardMarkup(keyboard)


def get_quiz_topic_data(topic_key):
    """Возвращает данные темы по ключу"""
    return QUIZ_TOPICS.get(topic_key)


def get_quiz_continue_keyboard(topic_key):
    """Возвращает клавиатуру для продолжения квиза"""
    keyboard = [
        [InlineKeyboardButton("🎯 Ещё вопрос", callback_data=f"quiz_continue_{topic_key}")],
        [InlineKeyboardButton("🔄 Сменить тему", callback_data="quiz_change_topic")],
        [InlineKeyboardButton("🏁 Закончить квиз", callback_data="quiz_finish")]
    ]
    return InlineKeyboardMarkup(keyboard)