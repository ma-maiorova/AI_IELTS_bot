import logging
import os

from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from data import registered_users
from handlers.wrapper import ensure_registered
from keyboards import persistent_keyboard, topic_keyboard, inline_keyboard_end_part
from state import UserState
from task_parts.listening_part import get_listening_tasks, listening_prompt_part, \
    listening_prompt_part_questions
from task_parts.reading_part import get_reading_task, reading_prompt_part
from task_parts.speaking_part import get_speaking_tasks, speaking_prompt_part
from task_parts.writing_part import get_writing_tasks, writing_prompt_part
from tasks import generate_task


def get_reply_target(update: Update):
    if update.message:
        return update.message
    elif update.callback_query:
        return update.callback_query.message
    return None


@ensure_registered
async def task_new_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для выбора нового топика задания.
    Отправляет сообщение с кнопками для выбора, а также предлагает ввести название топика.
    """
    reply_target = get_reply_target(update)
    await reply_target.reply_text("Выберите или введите новый топик задания.",
                                  reply_markup=InlineKeyboardMarkup(topic_keyboard))


@ensure_registered
async def task_new_topic_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка нажатий кнопок.
    Сохраняет выбор пользователя и генерирует задание.
    """
    query = update.callback_query
    await query.answer()
    task_type = query.data
    user_id = query.from_user.id
    if user_id not in registered_users:
        registered_users[user_id] = {"status": "registered"}

    registered_users[user_id]["state"] = UserState.TASK_IN_PROGRESS
    registered_users[user_id]["current_part"] = 0
    registered_users[user_id]["task_type"] = task_type

    await query.edit_message_text(
        text=f"Вы выбрали: {task_type.capitalize()}. Пожалуйста, подождите, генерируется задание...")

    await send_next_part(update, context, task_type, user_id)


async def task_same_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для генерации задания по-предыдущему выбранному топику.
    Если топик не выбран, предлагает выбрать новый.
    """
    reply_target = get_reply_target(update)
    user_id = update.effective_user.id
    user_data = registered_users.get(user_id, {})
    if not user_data.get("task_type"):
        await reply_target.reply_text(
            "Топик не выбран. Пожалуйста, используйте /task_new_topic для выбора нового топика.")
        return
    task_type = user_data["task_type"]
    user_data["state"] = UserState.TASK_IN_PROGRESS
    user_data["current_part"] = 0
    await reply_target.reply_text(
        f"Повторно генерируем задание по топику {task_type.capitalize()}...",
        reply_markup=persistent_keyboard
    )

    await send_next_part(update, context, task_type, user_id)


async def next_part_of_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Присылает следующую часть задания.
    """
    reply_target = get_reply_target(update)
    user_id = update.effective_user.id
    user_data = registered_users.get(user_id)
    if not user_data or not user_data.get("task_type"):
        await reply_target.reply_text(
            "Топик не выбран. Пожалуйста, используйте /task_new_topic для выбора нового топика.")
        return

    task_type = user_data["task_type"]
    user_data["state"] = UserState.TASK_IN_PROGRESS
    await reply_target.reply_text(
        f"Генерируем следующую часть по топику {task_type.capitalize()}...",
        reply_markup=persistent_keyboard
    )

    await send_next_part(update, context, task_type, user_id)


@ensure_registered
async def send_next_part(update_or_query, context: ContextTypes.DEFAULT_TYPE, task_type: str, user_id: int):
    """
    Универсальная функция, которая отправляет пользователю следующую часть задания
    в зависимости от task_type и текущего 'current_part'.
    """

    user_data = registered_users.get(user_id)
    if not user_data or not user_data.get("task_type"):
        await update_or_query.message.reply_text(
            "Топик не выбран. Пожалуйста, используйте /task_new_topic для выбора нового топика.")
        return

    current_part = user_data["current_part"]

    chat_id = None
    if hasattr(update_or_query, "message") and update_or_query.message is not None:
        chat_id = update_or_query.message.chat_id
    else:
        chat_id = update_or_query.callback_query.message.chat_id

    if task_type == "listening":
        tasks = get_listening_tasks()
        if current_part < len(tasks):
            registered_users[user_id]["current_part_len"] = len(tasks)
            part_data = tasks[current_part]

            prompt = listening_prompt_part + f" title : {part_data['title']}"
            task_content = generate_task(task_type, prompt, current_part)
            audio_file = task_content.get("audio_file")

            prompt_questions = listening_prompt_part_questions + task_content.get("text")
            questions_content = generate_task('questions', prompt_questions, current_part)

            registered_users[user_id]["current_task"] = task_content.get("text", "") + questions_content.get("text", "")

            if audio_file and os.path.exists(audio_file):

                await context.bot.send_message(chat_id=chat_id, text=part_data["title"])
                await context.bot.send_message(chat_id=chat_id, text=part_data["description"])
                await context.bot.send_message(chat_id=chat_id, text=part_data["instruction"])

                try:
                    await context.bot.send_audio(chat_id=chat_id, audio=open(audio_file, 'rb'))
                except Exception as e:
                    print(audio_file)
                    logging.error(f"Ошибка отправки аудио для Listening part {current_part + 1}: {e}")
                    await context.bot.send_message(chat_id=chat_id, text="Ошибка при отправке аудио.",
                                                   reply_markup=persistent_keyboard)

                await context.bot.send_message(chat_id=chat_id, text=task_content.get("text", ""))
                await context.bot.send_message(chat_id=chat_id,
                                               text="Questions\n" + questions_content.get("text", ""))
            else:
                await context.bot.send_message(chat_id=chat_id, text="(Аудиофайл не найден или отсутствует.)",
                                               reply_markup=persistent_keyboard)

            user_data["current_part"] += 1

        else:
            await context.bot.send_message(chat_id=chat_id, text="Все части Listening этого задания пройдены!",
                                           reply_markup=inline_keyboard_end_part)
            user_data["state"] = UserState.COMPLETED

    elif task_type == "reading":
        tasks = get_reading_task()
        if current_part == 0:

            registered_users[user_id]["current_part_len"] = 0
            part_data = tasks[current_part]

            prompt = reading_prompt_part + f" title : {part_data['title']} , description: {part_data['description']}"
            task_content = generate_task(task_type, prompt)
            registered_users[user_id]["current_task"] = task_content.get("text", "")

            await context.bot.send_message(chat_id=chat_id, text=part_data["title"])
            await context.bot.send_message(chat_id=chat_id, text=part_data["description"])

            await context.bot.send_message(chat_id=chat_id, text=task_content.get("text", ""),
                                           reply_markup=persistent_keyboard)

            user_data["current_part"] += 1
        else:
            await context.bot.send_message(chat_id=chat_id, text="Reading заданий больше нет.",
                                           reply_markup=inline_keyboard_end_part)
            user_data["state"] = UserState.COMPLETED

    elif task_type == "speaking":
        tasks = get_speaking_tasks()
        if current_part < len(tasks):
            registered_users[user_id]["current_part_len"] = len(tasks)

            part_data = tasks[current_part]

            prompt = speaking_prompt_part + f" title : {part_data['title']} , description: {part_data['description']}"
            task_content = generate_task(task_type, prompt, current_part)
            registered_users[user_id]["current_task"] = task_content.get("text", "")

            await context.bot.send_message(chat_id=chat_id, text=f"Speaking Part {part_data['part']}")
            await context.bot.send_message(chat_id=chat_id, text=part_data["description"])

            await context.bot.send_message(chat_id=chat_id, text=task_content.get("text", ""),
                                           reply_markup=persistent_keyboard)

            user_data["current_part"] += 1
        else:
            await context.bot.send_message(chat_id=chat_id, text="Все части Speaking уже пройдены!",
                                           reply_markup=inline_keyboard_end_part)
            user_data["state"] = UserState.COMPLETED

    elif task_type == "writing":
        tasks = get_writing_tasks()
        if current_part < len(tasks):
            registered_users[user_id]["current_part_len"] = len(tasks)

            part_data = tasks[current_part]

            prompt = writing_prompt_part + f" title : {part_data['title']} , description: {part_data['description']}"
            task_content = generate_task(task_type, prompt, current_part)
            registered_users[user_id]["current_task"] = task_content.get("text", "")

            await context.bot.send_message(chat_id=chat_id, text=part_data["title"])
            await context.bot.send_message(chat_id=chat_id, text=part_data["description"])

            await context.bot.send_message(chat_id=chat_id, text=task_content.get("text", ""),
                                           reply_markup=persistent_keyboard)

            user_data["current_part"] += 1
        else:
            await context.bot.send_message(chat_id=chat_id, text="Все части Writing уже пройдены!",
                                           reply_markup=inline_keyboard_end_part)
            user_data["state"] = UserState.COMPLETED
    else:
        await context.bot.send_message(chat_id=chat_id, text="Неизвестный тип задания.")
        user_data["state"] = UserState.COMPLETED
