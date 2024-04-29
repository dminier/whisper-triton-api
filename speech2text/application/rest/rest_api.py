from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form
from loguru import logger

from speech2text.domain import TRANSCRIBE_SERVICE

rest_router = APIRouter()

logger.info("Load Speech2Text Rest API")


@rest_router.post("/rest/transcribe-with-sentence-timestamp")
async def transcribe_with_sentence_timestamp_method_1(
        file: UploadFile = File(...),
        language_code: Optional[str] = Form(None),
        prompt: Optional[str] = Form(None)
):
    return await TRANSCRIBE_SERVICE.transcribe_with_sentence_timestamp_method_1(file, language_code, prompt)


@rest_router.post("/rest/transcribe-simple")
async def transcribe_simple(
        file: UploadFile = File(...),
        language_code: Optional[str] = Form(None),
        prompt: Optional[str] = Form(None),
        channel_number: Optional[int] = Form(-1)
):
    return await TRANSCRIBE_SERVICE.transcribe_simple(file, language_code, prompt, channel_number)
