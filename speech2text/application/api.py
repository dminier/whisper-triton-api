import datetime

from fastapi import APIRouter, UploadFile, File
from loguru import logger

from ..infrastrusture.speech2text.client import Client

router = APIRouter()

client = Client()


@router.post("/speech2text")
async def speech2text(file: UploadFile = File(...), language_code: str = "en"):
    b: bytes = await file.read()

    t1 = datetime.datetime.now()

    text = await client.infer(audio_bytes=b,
                              whisper_prompt=f"<|startoftranscript|><|{language_code}|><|transcribe|><|notimestamps|>")
    t2 = datetime.datetime.now()

    delta = t2 - t1

    logger.debug(
        f"{delta.total_seconds() * 1000} ms to transcribe {file.filename} of size {file.size / 1000} kB and content-type {file.content_type}")

    return text
