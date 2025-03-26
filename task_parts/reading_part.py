reading_prompt_part = """
You are an expert in creating IELTS Reading tasks.
Please generate a complete IELTS Reading assignment using the following guidelines:

**Assignment Structure:**
1. **Title:** Provide a concise title for the assignment.
2. **Overview:** Offer a brief description of the theme or situation depicted in the text (1-2 sentences).
3. **Passage:** Create a reading passage written according to IELTS Reading standards, consisting of 350-400 words.
4. **Questions:** Generate 18 questions based on the passage, covering the following types:
   - **Multiple Choice**
   - **Short Answer**
   - **Fill-in-the-Blanks**

**Formatting Requirements:**
- Use Markdown formatting (with clear headings and bullet points) suitable for Telegram.
- The entire output must be entirely in English; do not use any Russian.

**Input Provided:**
Title: {title}
Description: {description}

**Output:**
Provide the full IELTS Reading assignment as described above.
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

