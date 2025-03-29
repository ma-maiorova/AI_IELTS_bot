import logging

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters, ContextTypes
)

from config import TELEGRAM_BOT_TOKEN
from handlers.command_handlers import start, help_command
from handlers.processing_handlers import text_handler, voice_handler
from handlers.task_handlers import task_new_topic_button_handler, task_new_topic, task_same_topic, \
    next_part_of_task

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("task_new_topic", task_new_topic))
application.add_handler(CommandHandler("task_same_topic", task_same_topic))
application.add_handler(CommandHandler("next_part_of_task", next_part_of_task))
application.add_handler(
    CallbackQueryHandler(task_new_topic_button_handler, pattern="^(listening|speaking|reading|writing)$"))
application.add_handler(CallbackQueryHandler(next_part_of_task, pattern="^next_part$"))
application.add_handler(CallbackQueryHandler(task_new_topic, pattern="^new_topic$"))
application.add_handler(CallbackQueryHandler(task_same_topic, pattern="^same_topic$"))

# Обработчики текстовых сообщений и голосовых сообщений
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
application.add_handler(MessageHandler(filters.VOICE, voice_handler))


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Глобальный обработчик ошибок, чтобы бот не падал на исключениях.
    """
    logging.error(msg="Произошла ошибка в обработке апдейта:", exc_info=context.error)


application.add_error_handler(error_handler)


def main():
    application.run_polling()


if __name__ == '__main__':
    main()
