from telegram import Update
from telegram.ext import ContextTypes

from handlers.task_handlers import task_new_topic
from handlers.wrapper import ensure_registered
from keyboards import persistent_keyboard
from texts import start_text, help_command_text


@ensure_registered
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /start.
    Регистрирует пользователя и переводит его в режим выбора нового топика,
    автоматически вызывая функцию task_new_topic.
    """
    await update.message.reply_text(
        start_text,
        reply_markup=persistent_keyboard
    )
    await task_new_topic(update, context)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработка команды /help.
    Отправляет описание всех команд.
    """
    help_text = help_command_text
    await update.message.reply_text(help_text, reply_markup=persistent_keyboard)
