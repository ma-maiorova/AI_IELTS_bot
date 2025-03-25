import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)
from handlers import start, task_new_topic_button_handler, text_handler, voice_handler, error_handler, help_command, \
    task_new_topic, \
    task_same_topic, next_part_of_task

from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("task_new_topic", task_new_topic))
    application.add_handler(CommandHandler("task_same_topic", task_same_topic))
    application.add_handler(CommandHandler("next_part_of_task", next_part_of_task))
    application.add_handler(CallbackQueryHandler(task_new_topic_button_handler))

    # Обработчики текстовых сообщений и голосовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(MessageHandler(filters.VOICE, voice_handler))


    application.add_error_handler(error_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
