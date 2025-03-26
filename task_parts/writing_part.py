writing_prompt_part =  """
You are an expert in generating IELTS Writing assignments.
Please create a complete writing task specifically for the given writing task number, following the guidelines below:

**Assignment Structure:**
1. **Title:** Provide a concise title for the task.
2. **Context/Theme:** Write a brief description (1-2 sentences) outlining the context or theme relevant to the task.
3. **Task Instruction:** Clearly state the writing prompt. For Task 1, generate a scenario-based letter prompt (which may be personal, semi-formal, or formal). For Task 2, generate an essay prompt responding to a point of view, argument, or problem.
4. **Style and Tone:** Ensure the prompt adheres to IELTS Writing standards and is entirely in English.

**Formatting Requirements:**
- Use Markdown formatting (e.g., **bold** headings) that is compatible with Telegram.
- Do not include any Russian text; the final output must be solely in English.

**Input Provided:**
- **Title:** {title}
- **Description:** {description}

**Output:**
Generate the complete IELTS Writing assignment for the specified task.
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
