reading_prompt_part = """
Мне нужно задание для секции Reading в IELTS. Пожалуйста, создай задание, которое включает:
1. Краткое описание темы или ситуации, отражённой в тексте.
2. Сам текст для чтения, написанный согласно формату IELTS Reading. (250-300 слов)
3. Набор вопросов к тексту, разделённых на разные типы: multiple choice, short answer, fill-in-the-blanks.

ВАЖНО: Пожалуйста, предоставь итоговый вариант задания исключительно на английском языке, без использования русского.
"""

def get_reading_task():
    """
    Возвращает структуру данных для одного (или нескольких) текстов чтения с вопросами.
    """
    return [
        {
        "title": "IELTS Reading – Sample Text",
        "description": (
            "You will be given an extract from a magazine about environmental changes in urban areas. "
            "Read the passage carefully and answer the questions that follow."
        ),
        }
    ]

