listening_prompt_part = ("\n"
                         "You are an expert in generating IELTS Listening tasks. Please create a listening passage based on the provided title with the following specifications:\n"
                         "\n"
                         "**Task Requirements:**\n"
                         "1. Generate a listening passage in English following IELTS Listening standards (300-400 words).\n"
                         "2. Structure the passage with clear sections and headings formatted using Markdown (e.g., **Title**, **Section**, etc.) for Telegram.\n"
                         "3. Do not include any questions in this output; only provide the listening passage text.\n"
                         "\n"
                         "**Input:**\n"
                         "Title: {title}\n"
                         "\n"
                         "**Output:**\n"
                         "Provide the final listening passage as specified.\n")

listening_prompt_part_questions = ("\n"
                                   "You are an expert in creating IELTS Listening questions. Based on the provided listening passage, generate exactly 9 questions in English covering different types, including:\n"
                                   "\n"
                                   "- Multiple Choice Questions\n"
                                   "- Fill-in-the-Blanks\n"
                                   "- Short Answer Questions\n"
                                   "\n"
                                   "**Requirements:**\n"
                                   "1. Number the questions clearly.\n"
                                   "2. Format the output using Markdown for Telegram.\n"
                                   "3. Ensure that each question directly relates to the provided listening passage.\n"
                                   "4. In the \"Fill in the blanks\" questions, show where to insert the word using the \"_\" characters.\n"
                                   "\n"
                                   "**Input Text:**\n"
                                   "{text}\n"
                                   "\n"
                                   "**Output:**\n"
                                   "Provide the 9 questions in a clear, structured format.\n")


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
                'You will hear a conversation between two people discussing travel plans.\n'
                'Answer the following questions based on the conversation.'
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
