import os
import random

from yandex_cloud_ml_sdk import YCloudML

from config import KEY_YANDEX_GPT, FOLDER_YANDEX_GPT
from data import audio_folder_synthesize
from feedback_prompt import get_prompt_feedback
from recognize import synthesize_speech, recognize_speech

sdk = YCloudML(
    folder_id=FOLDER_YANDEX_GPT, auth=KEY_YANDEX_GPT
)

base_model = sdk.models.completions("yandexgpt", model_version="rc")


def generate_task(task_type, prompt='', part=0):
    """
    Генерирует задание для выбранного раздела IELTS с помощью моделей Hugging Face.
    Для Listening возвращает словарь с ключами 'textи 'audio_file'.
    Для остальных разделов возвращает текст задания.
    """

    temperature_value = round(random.uniform(0.5, 0.9), 2)
    model = base_model.configure(temperature=temperature_value)

    result = model.run(
        [
            {"role": "system", "text": "Генерируй текст по промту"},
            {"role": "user", "text": prompt},
        ]
    )

    task_text = result[0].text
    print(task_text)

    if task_type == "listening":

        output_audio = os.path.join(audio_folder_synthesize, f"synthesized_speech_{os.getpid()}_part{part + 1}")

        # open(output_audio, 'wb').close()
        # audio_output = synthesize_speech(task_text, output_audio)
        # return {"text": task_text, "audio_file": audio_output}

        synthesize_speech(task_text, output_audio, lang="en-US", voice="john")
        return {
            "text": task_text,
            "audio_file": output_audio
        }

    else:
        return {"text": task_text}


def generate_feedback(task_type, user_answer, user_id):
    """
    Генерирует обратную связь по ответу пользователя.
    Анализирует ошибки, предлагает исправления и советы по улучшению.
    """

    temperature_value = round(random.uniform(0.5, 0.9), 2)
    model = base_model.configure(temperature=temperature_value)

    prompt = get_prompt_feedback(task_type, user_answer, user_id)

    result = model.run([
        {"role": "system", "text": "Инструкции: анализируй ответ студента по выбранному заданию."},
        {"role": "user", "text": prompt},
    ])

    if not result:
        return "Ошибка при генерации обратной связи."

    feedback_text = result[0].text.strip()
    return feedback_text


def process_voice_task(file_path):
    """
    Обрабатывает голосовое сообщение: транскрибирует аудиофайл через Yandex SpeechKit (v3).
    Возвращает текст транскрипции.
    """
    transcription = recognize_speech(file_path)
    if isinstance(transcription, dict) and "text" in transcription:
        return transcription["text"]
    else:
        return str(transcription)
