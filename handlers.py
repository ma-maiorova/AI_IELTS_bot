import logging
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from tasks import generate_task, generate_feedback, process_voice_task

registered_users = {}
audio_folder = "records"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /start.
    Регистрирует пользователя и предлагает выбрать раздел IELTS.
    """

    user_id = update.effective_user.id
    if user_id not in registered_users:
        registered_users[user_id] = {
            "status": "registered",
            "task_type": None
        }

    keyboard = [
        [InlineKeyboardButton("Listening", callback_data="listening")],
        [InlineKeyboardButton("Speaking", callback_data="speaking")],
        [InlineKeyboardButton("Reading", callback_data="reading")],
        [InlineKeyboardButton("Writing", callback_data="writing")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать! Выберите раздел IELTS, над которым хотите потренироваться:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    registered_users[user_id]["task_type"] = task_type
    await query.edit_message_text(text=f"Вы выбрали: {task_type.capitalize()}. Пожалуйста, подождите, генерируется задание...")

    task_content = generate_task(task_type)
    chat_id = query.message.chat_id

    if task_type == "listening":
        await context.bot.send_message(chat_id=chat_id, text=task_content.get("text", ""))
        audio_file = task_content.get("audio_file")
        if audio_file and os.path.exists(audio_file):
            try:
                await context.bot.send_audio(chat_id=chat_id, audio=open(audio_file, 'rb'))
            except Exception as e:
                logging.error(f"Ошибка при отправке аудио Listening: {e}")
        else:
            await context.bot.send_message(chat_id=chat_id, text="Ошибка: аудиофайл не найден.")
    elif task_type == "speaking":
        await context.bot.send_message(chat_id=chat_id, text=task_content.get("text", ""))
    elif task_type == "reading":
        await context.bot.send_message(chat_id=chat_id, text=task_content.get("text", ""))
    elif task_type == "writing":
        await context.bot.send_message(chat_id=chat_id, text=task_content.get("text", ""))
    else:
        await context.bot.send_message(chat_id=chat_id, text="Неизвестный тип задания.")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка текстовых сообщений.
    Предназначено для получения ответов по заданиям Reading и Writing.
    """
    user_id = update.effective_user.id
    user_data = registered_users.get(user_id)
    if not user_data:
        await update.message.reply_text("Пожалуйста, начните с команды /start для регистрации.")
        return

    task_type = user_data.get("task_type")
    if task_type in ["reading", "writing"]:
        user_answer = update.message.text
        feedback = generate_feedback(task_type, user_answer)
        await update.message.reply_text(feedback)
    else:
        await update.message.reply_text("Пожалуйста, отправьте голосовое сообщение для speaking задания.")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка голосовых сообщений.
    Предназначено для получения ответов по заданию Speaking.
    """
    user_id = update.effective_user.id
    user_data = registered_users.get(user_id)
    if not user_data:
        await update.message.reply_text("Пожалуйста, начните с команды /start для регистрации.")
        return

    task_type = user_data.get("task_type")
    if task_type != "speaking":
        await update.message.reply_text("Пожалуйста, отправьте текстовое сообщение для данного задания.")
        return

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    file_path = os.path.join(audio_folder, f"voice_{voice.file_id}.ogg")
    await file.download_to_drive(custom_path=file_path)

    transcription = process_voice_task(file_path)
    feedback = generate_feedback(task_type, transcription)
    await update.message.reply_text(
        f"Транскрипция: {transcription}\n\nОбратная связь:\n{feedback}"
    )

    # if os.path.exists(file_path):
    #     os.remove(file_path)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Глобальный обработчик ошибок, чтобы бот не падал на исключениях.
    """
    logging.error(msg="Произошла ошибка в обработке апдейта:", exc_info=context.error)
