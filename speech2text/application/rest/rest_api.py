from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form
from loguru import logger

from speech2text.domain import TRANSCRIBE_SERVICE

rest_router = APIRouter()

logger.info("Load Speech2Text Rest API")


@rest_router.post("/rest/speech2text/{language_code}")
async def speech2text_given_language(language_code: str, file: UploadFile = File(...)):
    prompt = f"<|startoftranscript|><|{language_code}|><|transcribe|>"
    return await TRANSCRIBE_SERVICE.transcribe(file, prompt)


@rest_router.post("/rest/speech2text")
async def speech2text_given_language(prompt: Optional[str] = Form(None), file: UploadFile = File(...)):
    return await TRANSCRIBE_SERVICE.transcribe(file, prompt)


@rest_router.post("/rest/call2script/{language_code}")
async def speech2text_given_language(language_code: str, file: UploadFile = File(...)):
    prompt = f"<|startoftranscript|><|{language_code}|><|transcribe|><|notimestamps|>"

    return await TRANSCRIBE_SERVICE.transcribe(file, prompt)
