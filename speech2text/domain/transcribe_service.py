import asyncio
from dataclasses import dataclass
from typing import List

from fastapi import UploadFile

from speech2text.application import TRITON_CLIENT
from speech2text.domain.preprocessing.preprocessing import preprocess_silence_with_sentence_timestamp, \
    preprocess_simple_chunks, PreprocessedAudio

RATE = 16000


@dataclass
class ChunkOfTranscription:
    channel_name: str
    text: str
    start: int
    end: int


@dataclass
class Transcription:
    chunks: List[ChunkOfTranscription]
    audio_duration: float


class TranscribeService:
    def __init__(self):
        self._triton_client = TRITON_CLIENT

    async def transcribe_with_sentence_timestamp_method_1(self, file: UploadFile, language_code: str, prompt: str):
        """
        Transcribe using preprocess silence with AudioSegment.
        """
        _prompt = _get_prompt(language_code, prompt)

        b = await file.read()
        # use a dedicated preprocessing CPU depend
        preprocessed_audio: PreprocessedAudio = await preprocess_silence_with_sentence_timestamp(b, RATE)

        texts = await asyncio.gather(
            *[
                self._triton_client.infer(chunk.samples, 16000, whisper_prompt=_prompt)
                for chunk in preprocessed_audio.chunks
            ]
        )

        chunks_of_transcription = [
            ChunkOfTranscription(
                text=text,
                channel_name=chunk.channel_name,
                start=chunk.start,
                end=chunk.end
            ) for (chunk, text) in zip(preprocessed_audio.chunks, texts)
        ]
        return Transcription(
            chunks=chunks_of_transcription,
            audio_duration=preprocessed_audio.durations
        )

    async def transcribe_simple(self, file: UploadFile, language_code: str, prompt: str,
                                channel_number: int = -1):
        """
        Transcribe a channel number if > 0 else all channel.
        """
        _prompt = _get_prompt(language_code, prompt)

        b = await file.read()
        preprocessed_audio: PreprocessedAudio = await preprocess_simple_chunks(b, RATE, channel_number)
        texts = await asyncio.gather(
            *[
                self._triton_client.infer(chunk.samples, 16000, whisper_prompt=_prompt)
                for chunk in preprocessed_audio.chunks
            ]
        )

        chunks_of_transcription = [
            ChunkOfTranscription(
                text=text,
                channel_name=chunk.channel_name,
                start=-1,
                end=-1
            ) for (chunk, text) in zip(preprocessed_audio.chunks, texts)
        ]
        return Transcription(
            chunks=chunks_of_transcription,
            audio_duration=preprocessed_audio.durations
        )


def _get_prompt(language_code, prompt):
    _prompt = prompt

    if language_code and not prompt:
        _prompt = f"<|startoftranscript|><|{language_code}|><|transcribe|><|notimestamps|>"

    if not language_code and not prompt:
        _prompt = "<|startoftranscript|><|fr|><|transcribe|><|notimestamps|>"

    return _prompt
