import os

from telegram import Update
from telegram.ext import ContextTypes

from data import registered_users, audio_folder_record
from handlers.task_handlers import send_next_part
from handlers.wrapper import ensure_registered
from keyboards import persistent_keyboard, inline_keyboard_next_part, inline_keyboard_end_part
from state import UserState
from tasks import generate_feedback, process_voice_task
from texts import end_topic_task_text


async def handle_choosing_topic(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    topic = update.message.text.lower().strip()
    if topic in ["listening", "speaking", "reading", "writing"]:
        user_data["task_type"] = topic
        user_data["state"] = UserState.TASK_IN_PROGRESS
        user_data["current_part"] = 0
        await update.message.reply_text(
            f"Вы выбрали: {topic.capitalize()}. Генерируем задание...",
            reply_markup=persistent_keyboard
        )
        user_id = update.effective_user.id
        await send_next_part(update, context, topic, user_id)
    else:
        await update.message.reply_text(
            "Некорректный выбор. Введите listening, speaking, reading или writing.",
            reply_markup=persistent_keyboard
        )


async def handle_task_in_progress(update: Update, context: ContextTypes.DEFAULT_TYPE, user_data: dict):
    task_type = user_data.get("task_type")
    if task_type in ["reading", "writing", "listening"]:
        await update.message.reply_text("Ваш ответ принят, скоро будут результаты!")
        user_answer = update.message.text
        feedback = generate_feedback(task_type, user_answer, update.effective_user.id)
        await update.message.reply_text(feedback, reply_markup=persistent_keyboard)
        if user_data["current_part"] < user_data["current_part_len"]:
            await update.message.reply_text("Тык", reply_markup=inline_keyboard_next_part)
        else:
            await update.message.reply_text(end_topic_task_text[0], reply_markup=inline_keyboard_end_part)
    else:
        await update.message.reply_text(
            "Пожалуйста, отправьте голосовое сообщение для speaking задания.",
            reply_markup=persistent_keyboard
        )


@ensure_registered
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка текстовых сообщений.
    Если пользователь находится в режиме выбора топика, то его ввод интерпретируется как выбор нового топика.
    Иначе, если задание относится к Reading/Writing, обрабатывается как ответ на задание.
    """
    user_id = update.effective_user.id
    user_data = registered_users.get(user_id)

    state = user_data.get("state")

    if state == UserState.CHOOSING_TOPIC:
        await handle_choosing_topic(update, context, user_data)
    elif state == UserState.TASK_IN_PROGRESS:
        await handle_task_in_progress(update, context, user_data)
    else:
        await update.message.reply_text("Пока ничего не требуется. Используйте /task_new_topic.")


async def handle_incorrect_task_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Пожалуйста, отправьте текстовое сообщение для данного задания.",
        reply_markup=persistent_keyboard
    )


async def download_voice_file(context: ContextTypes.DEFAULT_TYPE, voice, file_id: str) -> str:
    file_obj = await context.bot.get_file(voice.file_id)
    file_path = os.path.join(audio_folder_record, f"voice_{file_id}.ogg")
    await file_obj.download_to_drive(custom_path=file_path)
    return file_path


@ensure_registered
async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка голосовых сообщений.
    Предназначено для получения ответов по заданию Speaking.
    """
    user_id = update.effective_user.id
    user_data = registered_users.get(user_id)

    task_type = user_data.get("task_type")
    if task_type != "speaking":
        await handle_incorrect_task_type(update, context)
        return

    voice = update.message.voice
    file_path = await download_voice_file(context, voice, voice.file_id)
    await update.message.reply_text("Ваш ответ принят, скоро будут результаты!")

    user_answer = process_voice_task(file_path)
    feedback = generate_feedback(task_type, user_answer, user_id)
    await update.message.reply_text(
        f"Транскрипция: {user_answer}\n\nОбратная связь:\n{feedback}"
        , reply_markup=persistent_keyboard, parse_mode='Markdown')

    if user_data["current_part"] < registered_users[user_id]["current_part_len"]:
        await update.message.reply_text(text="Тык",
                                        reply_markup=inline_keyboard_next_part)
    else:
        await update.message.reply_text(
            end_topic_task_text[0], reply_markup=inline_keyboard_end_part
        )

    # if os.path.exists(file_path):
    #     os.remove(file_path)
