listening_prompt_part = """
Мне нужно задание для секции Listening в IELTS. Пожалуйста, создай задание, которое включает 
текст , написанный согласно формату IELTS Listening. (300-400 слов) по заданному title, БЕЗ ВОПРОСОВ, только сам текст

ВАЖНО: Пожалуйста, предоставь итоговый вариант задания исключительно на английском языке, без использования русского.
"""

listening_prompt_part_questions = ("Напиши 9 вопросов к тексту, данному ниже, разделённых на разные типы: "
                                   "вопросы с множественным выбором, задания на заполнение пропусков и "
                                   "вопросы с коротким ответом. "
                                   "вопросы должны быть на английском языке, без ответов"
                                   "Вопросы должны быть по тексту:")


def get_listening_tasks():
    """
    Возвращает структуру данных со всеми 4 частями (Recording 1-4).
    Каждая часть – это словарь с описанием, списком (или текстом) вопросов,
    и (опционально) ссылкой на аудиофайл.
    Здесь для упрощённого примера – статический текст.
    Вы можете реализовать генерацию через GPT на основе listening_prompt.
    """

    return [
        {
            "title": "Recording 1 – a conversation between two people in an everyday social context",
            "description": (
                "You will hear a conversation between two people discussing travel plans.\n"
                "Answer the following questions based on the conversation."
            ),
            "instruction": "Please listen to Recording 1 and answer the following question:\nWhat is the main topic of the conversation?"
        },
        {
            "title": "Recording 2 – a monologue set in an everyday social context",
            "description": (
                "You will hear a short speech about local facilities.\n"
                "Please answer the questions below."
            ),
            "instruction": "Please listen to Recording 2 and answer the following question:\nWhat advantages regarding local facilities are mentioned?"
        },
        {
            "title": "Recording 3 – a conversation in an educational or training context",
            "description": (
                "Listen to a conversation between a university tutor and a student discussing an assignment.\n"
                "Answer the following questions."
            ),
            "instruction": "Please listen to Recording 3 and answer the following question:\nWhat challenges were discussed?"
        },
        {
            "title": "Recording 4 – a monologue on an academic subject",
            "description": (
                "You will hear part of a lecture on an academic subject.\n"
                "Answer the questions below."
            ),
            "instruction": "Please listen to Recording 4 and answer the following question:\nWhat is the main argument presented in the lecture?"
        },
    ]

def get_listening_part(part_index):
    if 0 <= part_index < len(get_listening_tasks()):
        return get_listening_tasks()[part_index]
    return None

def total_listening_parts():
    return len(get_listening_tasks())