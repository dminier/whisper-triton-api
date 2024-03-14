import base64
import tempfile
import wave

from fastapi import WebSocket, APIRouter
from loguru import logger
from starlette.websockets import WebSocketDisconnect

from speech2text.application import TRITON_CLIENT
from speech2text.application.websocket.connection_manager import ConnectionManager, WebSocketWaveSession

logger.info("Load Speech2Text Websocket API")

websocket_router = APIRouter()

MANAGER = ConnectionManager()


def _get_audio_byte(b):
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as temp_file:
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setparams((1, 2, 16000, 0, 'NONE', 'NONE'))
            wav_file.writeframes(b)
            return temp_file.read()


@websocket_router.websocket("/ws/speech2text")
async def websocket_endpoint(websocket: WebSocket):
    # todo access_token
    fake_user_id = "mcazerty"

    """
    client_id should be replaced with id from access token.
    """
    wws: WebSocketWaveSession = await MANAGER.connect(websocket, fake_user_id)

    try:
        while True:
            data = await wws.websocket.receive_json()

            if data:
                data_bytes = base64.b64decode(data['audio_data'])

                result = await TRITON_CLIENT.infer(audio_bytes=_get_audio_byte(data_bytes),
                                                   whisper_prompt=wws.prompt)
                logger.debug(result)
                await wws.websocket.send_json(
                    {
                        "text": result,
                        "message_type": "FinalTranscript"
                    }
                )
    except WebSocketDisconnect:
        logger.debug("Normal disconnection")
    except Exception as re:
        logger.exception("Error")
    finally:
        await MANAGER.disconnect(fake_user_id)
        try:
            await websocket.close()
        except:
            pass
