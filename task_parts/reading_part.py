reading_prompt_part = ("\n"
                       "You are an expert in creating IELTS Reading tasks.\n"
                       "Please generate a complete IELTS Reading assignment using the following guidelines:\n"
                       "\n"
                       "**Assignment Structure:**\n"
                       "1. **Title:** Provide a concise title for the assignment.\n"
                       "2. **Overview:** Offer a brief description of the theme or situation depicted in the text (1-2 sentences).\n"
                       "3. **Passage:** Create a reading passage written according to IELTS Reading standards, consisting of 350-400 words.\n"
                       "4. **Questions:** Generate 18 questions based on the passage, covering the following types:\n"
                       "   - **Multiple Choice**\n"
                       "   - **Short Answer**\n"
                       "   - **Fill-in-the-Blanks**\n"
                       "\n"
                       "**Formatting Requirements:**\n"
                       "- Use Markdown formatting (with clear headings and bullet points) suitable for Telegram.\n"
                       "- The entire output must be entirely in English; do not use any Russian.\n"
                       "- In the \"Fill in the blanks\" questions, show where to insert the word using the \"_\" characters.\n"
                       "\n"
                       "**Input Provided:**\n"
                       "Title: {title}\n"
                       "Description: {description}\n"
                       "\n"
                       "**Output:**\n"
                       "Provide the full IELTS Reading assignment as described above.\n")


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
