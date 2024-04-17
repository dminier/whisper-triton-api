from dataclasses import dataclass
from typing import List

from fastapi import UploadFile

from speech2text.application import TRITON_CLIENT
from speech2text.domain.preprocessing.preprocessing import preprocess_silence


@dataclass
class Transcription:
    channel_name: str
    text: str
    start: int
    end: int


class TranscribeService:
    def __init__(self):
        self._triton_client = TRITON_CLIENT
        pass

    async def transcribe(self, file: UploadFile, prompt):
        b = await file.read()
        channels, duration = await preprocess_silence(b, 16000)
        transcriptions: List[Transcription] = []
        for channel in channels:
            text = await self._triton_client.infer(channel.samples, 16000, whisper_prompt=prompt)
            transcriptions.append(
                Transcription(
                    text=text,
                    channel_name=channel.channel_name,
                    start=channel.start,
                    end=channel.end
                )
            )

        return transcriptions
