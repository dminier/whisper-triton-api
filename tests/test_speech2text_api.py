import time

from fastapi.testclient import TestClient
from loguru import logger
from pydub import AudioSegment

from speech2text.application.app import app

client = TestClient(app)


def test_simple_dual_channel():
    rtf = call(endpoint="/rest/transcribe-simple",
               data={"language_code": 'fr'})

    print(f"RTF = {rtf}")


def test_simple_mono_channel():
    rtf = call(endpoint="/rest/transcribe-simple",
               data={"language_code": 'fr',
                     "channel_number": '1'
                     })

    print(f"RTF = {rtf}")


def test_transcribe_with_sentence_timestamp_method_1():
    rtf = call(endpoint="/rest/transcribe-with-sentence-timestamp",
               data={"language_code": 'fr'
                     })

    print(f"RTF = {rtf}")


def call(endpoint, data):
    filename = 'tests/dataset/call/5110.mp3'
    seg = AudioSegment.from_file(filename)
    assert seg.channels == 2
    start = time.time()
    with open(filename, "rb") as f:
        response = client.post(endpoint,
                               files={"file": ("filename", f, "audio/x-wav")},
                               data=data
                               )
        logger.debug(f"{filename} = {response.text}")
    end = time.time()
    duration = end - start
    audio_duration = response.json()["audio_duration"]
    rtf = duration / audio_duration
    return rtf
