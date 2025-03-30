import os
from dotenv import load_dotenv

load_dotenv()

V3_SPEECHKIT_RECOGNIZE = "https://stt.api.cloud.yandex.net/stt/v3/recognizeFileAsync"
V1_SPEECHKIT_SYNTHESIZE = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
KEY_YANDEX_GPT = os.getenv("KEY_YANDEX_GPT")
FOLDER_YANDEX_GPT = os.getenv("FOLDER_YANDEX_GPT")
KEY_YANDEX_SPEECHKIT = os.getenv("KEY_YANDEX_SPEECHKIT")