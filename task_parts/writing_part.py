writing_prompt_part = """
Мне нужно задание для секции Writing в IELTS. Пожалуйста, создай задание, которое включает:
1. Краткое описание контекста или темы.
2. Чёткое разделение на две части: Task 1 и Task 2.
3. Для выбранной части – собственный вопрос.

ВАЖНО: Пожалуйста, предоставь итоговый вариант задания исключительно на английском языке, без использования русского.
"""

def get_writing_tasks():
    """
    Возвращает две части Writing: Task 1 и Task 2.
    """
    return [
        {
            "task_number": 1,
            "title": "Writing Task 1 – Letter or Situation",
            "description": (
                "You are presented with a situation and asked to write a letter requesting information or "
                "explaining the situation. The letter may be personal, semi-formal or formal in style."
            ),
        },
        {
            "task_number": 2,
            "title": "Writing Task 2 – Essay",
            "description": (
                "You will be asked to write an essay in response to a point of view, argument or problem. "
                "The essay can be fairly personal in style."
            ),
        }
    ]
