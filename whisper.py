from datasets import Audio, Dataset
from transformers import WhisperForConditionalGeneration
from transformers import WhisperProcessor, pipeline


class WhisperModel:
    def __init__(self, language):
        self.language = None
        self.processor = WhisperProcessor.from_pretrained(
            "openai/whisper-small", language=self.language, task="transcribe"
        )
        self.sampling_rate = self.processor.feature_extractor.sampling_rate
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")

    def launch(self, audio_path):
        audio = Dataset.from_dict({"audio": [audio_path]}).cast_column("audio", Audio(sampling_rate=self.sampling_rate))
        audio = audio["audio"]
        generated_kwargs = {"task": "transcribe", "language": "english"}
        pipe = pipeline("automatic-speech-recognition", model=self.model, tokenizer=self.processor.tokenizer,
                        feature_extractor=self.processor.feature_extractor)
        return pipe(audio, generate_kwargs=generated_kwargs, return_timestamps=True)
