import logging
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from data import registered_users
from task_parts.listening_part import get_listening_tasks, listening_prompt_part, listening_prompt_part_questions
from task_parts.reading_part import reading_prompt_part, get_reading_task
from task_parts.speaking_part import get_speaking_tasks, speaking_prompt_part
from task_parts.writing_part import get_writing_tasks, writing_prompt_part
from tasks import generate_task, generate_feedback, process_voice_task

from telegram import ReplyKeyboardMarkup

persistent_keyboard = ReplyKeyboardMarkup(
    [
        ["/help", "/task_new_topic", "/task_same_topic", "/next_part_of_task"]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)

audio_folder = "records"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /start.
    Регистрирует пользователя и переводит его в режим выбора нового топика,
    автоматически вызывая функцию task_new_topic.
    """
    user_id = update.effective_user.id
    if user_id not in registered_users:
        registered_users[user_id] = {
            "status": "registered",
            "task_type": None,
            "state": "choosing_topic",
            "current_part": 0,
            "current_part_len": 0,
            "current_task": None,
        }
    else:
        registered_users[user_id]["state"] = "choosing_topic"
        registered_users[user_id]["current_part"] = 0
    await update.message.reply_text("Добро пожаловать!\n"
                                    "Этот бот поможет Вам подготовиться к IELTS экзамену по английскому языку\n"
                                    "Он будет присылать Вам задания для подготовки, а в ответ будет ждать от Вас ответы, после которых будет давать фидбек\n"
                                    "Выберите раздел IELTS, над которым хотите потренироваться:",
                                    reply_markup=persistent_keyboard)
    await task_new_topic(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /help.
    Отправляет описание всех команд.
    """
    help_text = (
        "Доступные команды:\n"
        "/start - Регистрация пользователя и выбор нового топика задания.\n"
        "/help - Помогу с ботом. Кря. \n"
        "/task_new_topic - Выбрать новый топик и получить задание.\n"
        "Вы можете выбирать топик как с помощью кнопок, так и отправить его с клавиатуры "
        "(доступные варианты: listening, speaking, reading, writing).\n"
        "/task_same_topic - Получить задание по предыдущему выбранному топику.\n"
        "/send_next_part - Получить следующую часть задания из выбранного топика.\n"
    )
    await update.message.reply_text(help_text, reply_markup=persistent_keyboard)


def get_reply_target(update: Update):
    if update.message:
        return update.message
    elif update.callback_query:
        return update.callback_query.message
    return None


async def task_new_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция для выбора нового топика задания.
    Отправляет сообщение с кнопками для выбора, а также предлагает ввести название топика.
    """
    reply_target = get_reply_target(update)
    user_id = update.effective_user.id
    if user_id not in registered_users:
        await reply_target.reply_text("Сначала введите /start для начала работы.", reply_markup=persistent_keyboard)
        return
    registered_users[user_id]["state"] = "choosing_topic"
    keyboard = [
        [InlineKeyboardButton("Listening", callback_data="listening")],
        [InlineKeyboardButton("Speaking", callback_data="speaking")],
        [InlineKeyboardButton("Reading", callback_data="reading")],
        [InlineKeyboardButton("Writing", callback_data="writing")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await reply_target.reply_text(
        "Выберите топик для нового задания или напишите его с клавиатуры (listening, speaking, reading, writing):",
        reply_markup=reply_markup,
    )


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

    registered_users[user_id]["state"] = "task_in_progress"
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
    user_data = registered_users.get(user_id)
    if not user_data or not user_data.get("task_type"):
        await reply_target.reply_text(
            "Топик не выбран. Пожалуйста, используйте /task_new_topic для выбора нового топика.")
        return
    task_type = user_data["task_type"]
    user_data["state"] = "task_in_progress"
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
    user_data["state"] = "task_in_progress"
    await reply_target.reply_text(
        f"Генерируем следующую часть по топику {task_type.capitalize()}...",
        reply_markup=persistent_keyboard
    )

    await send_next_part(update, context, task_type, user_id)


async def send_next_part(update_or_query, context: ContextTypes.DEFAULT_TYPE, task_type: str, user_id: int):
    """
    Универсальная функция, которая отправляет пользователю следующую часть задания
    в зависимости от task_type и текущего 'current_part'.
    """
    user_id = update_or_query.effective_user.id
    if user_id not in registered_users:
        await update_or_query.message.reply_text("Сначала введите /start для начала работы.",
                                                 reply_markup=persistent_keyboard)
        return

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
                try:

                    await context.bot.send_message(chat_id=chat_id, text=part_data["title"])
                    await context.bot.send_message(chat_id=chat_id, text=part_data["description"])
                    await context.bot.send_message(chat_id=chat_id, text=part_data["instruction"])

                    await context.bot.send_audio(chat_id=chat_id, audio=open(audio_file, 'rb'))
                    await context.bot.send_message(chat_id=chat_id, text=task_content.get("text", ""),
                                                   parse_mode='Markdown')
                    await context.bot.send_message(chat_id=chat_id,
                                                   text="Questions\n" + questions_content.get("text", ""),
                                                   parse_mode='Markdown')
                except Exception as e:
                    print(audio_file)
                    logging.error(f"Ошибка отправки аудио для Listening part {current_part + 1}: {e}")
                    await context.bot.send_message(chat_id=chat_id, text="Ошибка при отправке аудио.",
                                                   reply_markup=persistent_keyboard)
            else:
                await context.bot.send_message(chat_id=chat_id, text="(Аудиофайл не найден или отсутствует.)",
                                               reply_markup=persistent_keyboard)

            user_data["current_part"] += 1

        else:
            await context.bot.send_message(chat_id=chat_id, text="Все части Listening этого задания пройдены!")
            user_data["state"] = "completed"

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
                                           reply_markup=persistent_keyboard, parse_mode='Markdown')

            user_data["current_part"] += 1
        else:
            await context.bot.send_message(chat_id=chat_id, text="Reading заданий больше нет.")
            user_data["state"] = "completed"

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
                                           reply_markup=persistent_keyboard, parse_mode='Markdown')

            user_data["current_part"] += 1
        else:
            await context.bot.send_message(chat_id=chat_id, text="Все части Speaking уже пройдены!")
            user_data["state"] = "completed"

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
                                           reply_markup=persistent_keyboard, parse_mode='Markdown')

            user_data["current_part"] += 1
        else:
            await context.bot.send_message(chat_id=chat_id, text="Все части Writing уже пройдены!")
            user_data["state"] = "completed"
    else:
        await context.bot.send_message(chat_id=chat_id, text="Неизвестный тип задания.")
        user_data["state"] = "completed"


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка текстовых сообщений.
    Если пользователь находится в режиме выбора топика, то его ввод интерпретируется как выбор нового топика.
    Иначе, если задание относится к Reading/Writing, обрабатывается как ответ на задание.
    """
    user_id = update.effective_user.id
    user_data = registered_users.get(user_id)
    if not user_data:
        await update.message.reply_text("Пожалуйста, начните с команды /start для регистрации.",
                                        reply_markup=persistent_keyboard)
        return

    state = user_data.get("state")
    task_type = user_data.get("task_type")

    if state == "choosing_topic":
        topic = update.message.text.lower().strip()
        if topic in ["listening", "speaking", "reading", "writing"]:
            user_data["task_type"] = topic
            user_data["state"] = "task_in_progress"
            user_data["current_part"] = 0
            await update.message.reply_text(
                f"Вы выбрали: {topic.capitalize()}. Генерируем задание...",
                reply_markup=persistent_keyboard
            )
            await send_next_part(update, context, topic, user_id)
        else:
            await update.message.reply_text(
                "Некорректный выбор. Введите listening, speaking, reading или writing.",
                reply_markup=persistent_keyboard
            )
    elif state == "task_in_progress":
        task_type = user_data.get("task_type")
        print(task_type)
        if task_type in ["reading", "writing", "listening"]:

            await update.message.reply_text("Ваш ответ принят, скоро будут результаты!")

            user_answer = update.message.text
            feedback = generate_feedback(task_type, user_answer, user_id)
            await update.message.reply_text(feedback, reply_markup=persistent_keyboard, parse_mode='Markdown')
            if user_data["current_part"] < registered_users[user_id]["current_part_len"]:
                inline_keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Следующая часть задания из топика", callback_data="next_part")]])
                await update.message.reply_text(text="",
                                                reply_markup=inline_keyboard)
            else:
                inline_keyboard = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("Новый топик", callback_data="new_topic")],
                        [InlineKeyboardButton("Повторить задание", callback_data="same_topic")]
                    ]
                )
                await update.message.reply_text(
                    "Все части задания пройдены!\n\nВыберите действие:\n"
                    "• Новый топик - выбрать новый раздел для задания.\n"
                    "• Повторить задание - повторно сгенерировать задание по выбранному ранее топику.",
                    reply_markup=inline_keyboard
                )

        else:
            await update.message.reply_text("Пожалуйста, отправьте голосовое сообщение для speaking задания.",
                                            reply_markup=persistent_keyboard)
    else:
        await update.message.reply_text("Пока ничего не требуется. Используйте /task_new_topic.")


async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка голосовых сообщений.
    Предназначено для получения ответов по заданию Speaking.
    """
    user_id = update.effective_user.id
    user_data = registered_users.get(user_id)
    if not user_data:
        await update.message.reply_text("Пожалуйста, начните с команды /start для регистрации.",
                                        reply_markup=persistent_keyboard)
        return

    task_type = user_data.get("task_type")
    if task_type != "speaking":
        await update.message.reply_text("Пожалуйста, отправьте текстовое сообщение для данного задания.",
                                        reply_markup=persistent_keyboard)
        return

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)
    file_path = os.path.join(audio_folder, f"voice_{voice.file_id}.ogg")
    await file.download_to_drive(custom_path=file_path)

    await update.message.reply_text("Ваш ответ принят, скоро будут результаты!")

    user_answer = process_voice_task(file_path)
    feedback = generate_feedback(task_type, user_answer, user_id)
    await update.message.reply_text(
        f"Транскрипция: {user_answer}\n\nОбратная связь:\n{feedback}"
        , reply_markup=persistent_keyboard, parse_mode='Markdown')

    if user_data["current_part"] < registered_users[user_id]["current_part_len"]:
        inline_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Следующая часть задания из топика", callback_data="next_part")]])
        await update.message.reply_text(text="",
                                        reply_markup=inline_keyboard)
    else:
        inline_keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Новый топик", callback_data="new_topic")],
                [InlineKeyboardButton("Повторить задание", callback_data="same_topic")]
            ]
        )
        await update.message.reply_text(
            "Все части задания пройдены!\n\nВыберите действие:\n"
            "• Новый топик - выбрать новый раздел для задания.\n"
            "• Повторить задание - повторно сгенерировать задание по выбранному ранее топику.",
            reply_markup=inline_keyboard
        )

    # if os.path.exists(file_path):
    #     os.remove(file_path)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Глобальный обработчик ошибок, чтобы бот не падал на исключениях.
    """
    logging.error(msg="Произошла ошибка в обработке апдейта:", exc_info=context.error)
