import base64
import json
import time

import requests
from config import KEY_YANDEX_SPEECHKIT, FOLDER_YANDEX_GPT
from whisper import WhisperModel


def synthesize_speech(text, output_file, lang="en-US",
                      voice="john", speed=1.0, audio_format="oggopus"):
    """
    Синтез речи через Yandex SpeechKit (TTS).

    Аргументы:
      text: текст, который необходимо озвучить.
      output_file: путь для сохранения полученного аудиофайла.
      lang: язык синтеза (например, "ru-RU").
      voice: выбранный голос (например, "oksana", "jane", "alyss" и т.д.).
      speed: скорость произношения (обычно от 0.1 до 3.0).
      audio_format: формат аудио (например, "wav" или "oggopus").
    """
    url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
    headers = {
        "Authorization": f"Api-Key {KEY_YANDEX_SPEECHKIT}"
    }
    data = {
        "text": text,
        "lang": lang,
        "voice": voice,
        "speed": str(speed),
        "format": audio_format,
        'folderId': FOLDER_YANDEX_GPT
    }
    resp = requests.post(url, headers=headers, data=data, stream=True)
    if resp.status_code != 200:
        raise RuntimeError("Invalid response received: code: %d, message: %s" % (resp.status_code, resp.text))

    with open(output_file, "wb") as f:
        for chunk in resp.iter_content(chunk_size=None):
            f.write(chunk)

    print(f"Синтезированный файл сохранён: {output_file}")


def recognize_speech(input_file, lang="en-US"):
    """
    Распознавание речи через локальный whisper.

    Аргументы:
      input_file: путь к аудиофайлу для распознавания.
      lang: язык распознавания (например, "ru-RU").

    Возвращает:
      Строку с распознанным текстом или пустую строку в случае ошибки.
    """
    filepath = input_file
    model = WhisperModel("english")
    full_text = model.launch(filepath)[0]['text']
    return full_text


def recognize_speech_SpeechKit(input_file, lang="en-US"):
    """
    Распознавание речи через Yandex SpeechKit (ASR, v3).

    Аргументы:
      input_file: путь к аудиофайлу для распознавания.
      lang: язык распознавания (например, "ru-RU").

    Возвращает:
      Строку с распознанным текстом или пустую строку в случае ошибки.
    """
    url = "https://stt.api.cloud.yandex.net/stt/v3/recognizeFileAsync"
    headers = {
        "Authorization": f"Api-Key {KEY_YANDEX_SPEECHKIT}",
        "Content-Type": "application/json"
    }

    with open(input_file, "rb") as f:
        audio_data = f.read()
    audio_base64 = base64.b64encode(audio_data).decode("utf-8")

    payload = {
        "folderId": FOLDER_YANDEX_GPT,
        "content": audio_base64,
        "recognitionModel": {
            "model": "general",
            "audioFormat": {
                "containerAudio": {
                    "containerAudioType": "OGG_OPUS"
                }
            },
            "languageRestriction": {
                "restrictionType": "WHITELIST",
                "languageCode": ["en-US"]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("Ошибка распознавания речи1:", response.text)
        return ""

    operation = response.json()
    if "id" not in operation:
        return f"Ошибка: нет operation_id: {operation}"

    operation_id = operation["id"]

    get_url = "https://stt.api.cloud.yandex.net/stt/v3/getRecognition"
    params = {"operationId": operation_id}

    recognized_chunks = []

    find = False
    while not find:
        time.sleep(3)
        get_response = requests.get(get_url, headers=headers, params=params)
        if get_response.status_code != 200:
            print("Ошибка при получении результата:", get_response.text)
            continue

        # print(get_response)

        for line in get_response.iter_lines():
            # print("line ", line)
            if not line:
                continue
            try:
                result_data = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError as e:
                print("Ошибка парсинга JSON:", e)
                continue

            result_data = result_data["result"]

            if "final" in result_data:
                final_data = result_data["final"]
                if "alternatives" in final_data:
                    final_text = final_data["alternatives"][0].get("text", "")
                    # print("[FINAL]", final_text)
                    recognized_chunks.append(final_text)
                    find = True
                    break

            if "statusCode" in result_data and result_data["statusCode"].get("codeType") == "CLOSED":
                find = True
                break

    full_text = " ".join(recognized_chunks)
    return full_text


if __name__ == "__main__":
    sample_text = ("The Great Barrier Reef is one of the seven wonders of the natural world. "
                   "It is the largest reef system in the world, stretching over 2,300 kilometres along the northeastern coast of Australia. "
                   "The reef supports an incredible diversity of marine life, including corals, fish, and marine mammals. "
                   "However, it is facing serious threats from climate change, pollution, and human activities such as tourism and fishing. "

                   "The reef has been suffering from coral bleaching events caused by rising sea temperatures. "
                   "This occurs when the corals expel the algae that live in their tissues, leaving them white and vulnerable to disease and death. "
                   "Additionally, pollution from rivers and runoff from agricultural activities can harm the delicate ecosystem of the reef. "

                   "Tourism is a significant contributor to the reef's health, but overcrowding and the discharge of waste by tourists can damage the reef. "
                   "Fishing activities, both recreational and commercial, can also have a negative impact on the reef by depleting fish populations and disturbing the coral habitats. "

                   "Conservation efforts are underway to protect the Great Barrier Reef. "
                   "These include the establishment of marine parks, the regulation of fishing activities, and the reduction of pollution. "
                   "Scientists and environmentalists are working together to monitor the health of the reef and develop strategies to mitigate the impacts of climate change."
                   )
    output_audio = "synthesized_speech.oggopus"
    synthesize_speech(sample_text, output_audio)

    input_audio = output_audio
    recognized_text = recognize_speech(input_audio)
    print("Распознанный текст:", recognized_text)
