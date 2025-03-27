writing_prompt_part = ("\n"
                       "You are an expert in generating IELTS Writing assignments.\n"
                       "Please create a complete writing task specifically for the given writing task number, following the guidelines below:\n"
                       "\n"
                       "**Assignment Structure:**\n"
                       "1. **Title:** Provide a concise title for the task.\n"
                       "2. **Context/Theme:** Write a brief description (1-2 sentences) outlining the context or theme relevant to the task.\n"
                       "3. **Task Instruction:** Clearly state the writing prompt. For Task 1, generate a scenario-based letter prompt (which may be personal, semi-formal, or formal). For Task 2, generate an essay prompt responding to a point of view, argument, or problem.\n"
                       "4. **Style and Tone:** Ensure the prompt adheres to IELTS Writing standards and is entirely in English.\n"
                       "\n"
                       "**Formatting Requirements:**\n"
                       "- Use Markdown formatting (e.g., **bold** headings) that is compatible with Telegram.\n"
                       "- Do not include any Russian text; the final output must be solely in English.\n"
                       "\n"
                       "**Input Provided:**\n"
                       "- **Title:** {title}\n"
                       "- **Description:** {description}\n"
                       "\n"
                       "**Output:**\n"
                       "Generate the complete IELTS Writing assignment for the specified task.\n")


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
