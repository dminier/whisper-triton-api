import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form
from loguru import logger

from speech2text.application import TRITON_CLIENT

rest_router = APIRouter()

logger.info("Load Speech2Text Rest API")


@rest_router.post("/rest/speech2text/{language_code}")
async def speech2text_given_language(language_code: str, file: UploadFile = File(...)):
    prompt = f"<|startoftranscript|><|{language_code}|><|transcribe|><|notimestamps|>"
    return await _call_whisper_model(file, prompt)


@rest_router.post("/rest/speech2text")
async def speech2text_given_language( prompt: Optional[str] = Form(None), file: UploadFile = File(...)):
    return await _call_whisper_model(file, prompt)


async def _call_whisper_model(file, prompt):
    b: bytes = await file.read()
    t1 = datetime.datetime.now()
    text = await TRITON_CLIENT.infer(audio_bytes=b,
                                     whisper_prompt=prompt)
    t2 = datetime.datetime.now()
    delta = t2 - t1
    logger.debug(
        f"{delta.total_seconds() * 1000} ms to transcribe {file.filename} of size {file.size / 1000} kB and content-type {file.content_type}")
    logger.debug(text)
    return text
