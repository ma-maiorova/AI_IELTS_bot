speaking_prompt_part = """
Мне нужно задание для секции Speaking в IELTS. Пожалуйста, создай задание, которое включает:
1. Краткое описание (контекста).
2. Четкое задание из выбранной части.
3. Полные вопросы для задания и подсказки для каждой части, подсказки в самом конце.

ВАЖНО: Пожалуйста, предоставь итоговый вариант задания только на английском языке, без использования русского.
"""

def get_speaking_tasks():
    """
    Возвращает список частей для Speaking: Part 1, Part 2, Part 3.
    """
    return [
        {
            "part": 1,
            "title": "Part 1 – Introduction and general questions",
            "description": (
                "The examiner will ask general questions about yourself and a range of familiar topics, "
                "such as home, family, work, studies and interests."
            ),
        },
        {
            "part": 2,
            "title": "Part 2 – Long turn",
            "description": (
                "You will be given a cue card which asks you to talk about a particular topic. "
                "You have one minute to prepare before speaking for up to two minutes."
            ),
        },
        {
            "part": 3,
            "title": "Part 3 – Discussion",
            "description": (
                "You will be asked further questions about the topic in Part 2. "
                "These will give you the opportunity to discuss more abstract ideas and issues."
            ),
        }
    ]
