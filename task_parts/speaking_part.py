speaking_prompt_part = """
You are an expert in generating IELTS Speaking tasks. Please create a tailored speaking assignment for the specified part of the exam based on the following guidelines:

**Assignment Requirements:**
1. **Context Introduction:** Provide a brief context or introduction for the speaking task.
2. **Task Description:** Clearly state the specific task or question for the selected part.
3. **Detailed Questions and Prompts:** Include comprehensive questions and prompts (with hints provided at the end) for the candidate to address.
4. **Part Specificity:** Ensure that the assignment is exclusively for the given part (e.g., Part 1, Part 2, or Part 3) and does not include elements for other parts.

**Formatting Instructions:**
- Use Markdown formatting (e.g., **bold** headings, bullet points) suitable for Telegram.
- Provide the final output entirely in English without any Russian text.

**Input Provided:**
- **Title:** {title}
- **Description:** {description}

**Output:**
Generate the complete IELTS Speaking task for the specified part, following the above guidelines.
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
