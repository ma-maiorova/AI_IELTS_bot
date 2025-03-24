import os
import random

import torch

from config import KEY_YANDEX_GPT, FOLDER_YANDEX_GPT
import soundfile as sf
from transformers import pipeline
from recognize import synthesize_speech, recognize_speech

from yandex_cloud_ml_sdk import YCloudML

sdk = YCloudML(
    folder_id=FOLDER_YANDEX_GPT, auth=KEY_YANDEX_GPT
)

base_model = sdk.models.completions("yandexgpt-lite")

from promts import reading_promt, speaking_promt, listening_promt, writing_promt

audio_folder = "synthesized"


def generate_task(task_type):
    """
    Генерирует задание для выбранного раздела IELTS с помощью моделей Hugging Face.
    Для Listening возвращает словарь с ключами 'text' и 'audio_file'.
    Для остальных разделов возвращает текст задания.
    """
    prompt = ""
    if task_type == "listening":
        prompt = listening_promt
    elif task_type == "speaking":
        prompt = speaking_promt
    elif task_type == "reading":
        prompt = reading_promt
    elif task_type == "writing":
        prompt = writing_promt
    else:
        return {"text": "Неизвестный тип задания."}

    temperature_value = round(random.uniform(0.5, 0.9), 2)
    model = base_model.configure(temperature=temperature_value)

    result = model.run(
        [
            {"role": "system", "text": "Инструкции: генерируй задания для IELTS."},
            {"role": "user", "text": prompt},
        ]
    )

    task_text = result[0].text
    print(task_text)


    if task_type == "listening":

        output_audio = os.path.join(audio_folder, f"synthesized_speech_{os.getpid()}.ogg")

        # open(output_audio, 'wb').close()
        #
        # audio_output = synthesize_speech(task_text, output_audio)
        #
        # return {"text": task_text, "audio_file": audio_output}

        synthesize_speech(task_text, output_audio, lang="en-US", voice="john")
        return {
            "text": task_text,
            "audio_file": output_audio
        }

    else:
        return {"text": task_text}


def generate_feedback(task_type, user_answer):
    """
    Генерирует обратную связь по ответу пользователя.
    Анализирует ошибки, предлагает исправления и советы по улучшению.
    """

    temperature_value = round(random.uniform(0.5, 0.9), 2)
    model = base_model.configure(temperature=temperature_value)

    prompt = (
        f"Пользователь выполнил задание по разделу {task_type.capitalize()} IELTS.\n"
        f"Вот его ответ:\n\n{user_answer}\n\n"
        "Проанализируй ответ, укажи основные ошибки, предоставь исправления и рекомендации."
        "Структурируй ответ в виде списка (Ошибки -> Исправления -> Советы -> Ответы на задания)."
    )

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
