import tempfile
import wave
from typing import Dict

from loguru import logger
from starlette.websockets import WebSocket

from speech2text.application.whisper_spec import WhisperWaveSpec


class WebSocketWaveSession:
    """
        First time that I work with sounds and Python Websockets.
        Something like simple buffer and pure numpy would be better.
    """

    def __init__(self, websocket: WebSocket, user_id: str, prompt: str = WhisperWaveSpec.DEFAULT_PROMPT):
        self._init_temp_wave()
        self.websocket: WebSocket = websocket
        self.prompt = prompt
        self.user_id = user_id
        logger.debug(f"{user_id} open WebSocketSession")

    def _init_temp_wave(self):
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.wave = self._build_wave()

    def update_prompt_if_needed(self, prompt: str):
        if prompt:
            self.prompt = prompt

    def _build_wave(self):
        wav_file = wave.open(self.temp_file.name, 'wb')
        wav_file.setnchannels(WhisperWaveSpec.CHANNELS)
        wav_file.setsampwidth(WhisperWaveSpec.BITS_PER_SAMPLE // 8)
        wav_file.setframerate(WhisperWaveSpec.FRAME_RATE)
        return wav_file

    def flush(self, bytes_received):
        self.wave.writeframes(bytes_received)

    def read(self):
        data = self.temp_file.read()
        self._close_temp_wave()
        self._init_temp_wave()
        return data

    async def close(self):
        logger.debug(f"{self.user_id} close WebSocketSession")
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
        self._close_temp_wave()

    def _close_temp_wave(self):
        if self.wave:
            self.wave.close()
        if self.temp_file:
            self.temp_file.close()


class ConnectionManager:
    def __init__(self):
        self.active_sessions: Dict[str, WebSocketWaveSession] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> WebSocketWaveSession:
        # websocket_wave_session: WebSocketWaveSession = self.active_sessions.get(user_id)
        # if websocket_wave_session:
        #     await websocket_wave_session.close()
        await websocket.accept()
        session = WebSocketWaveSession(websocket, user_id)
        self.active_sessions[user_id] = session
        return session

    async def disconnect(self, user_id: str):
        session = self.active_sessions.get(user_id)
        if session:
            self.active_sessions.pop(user_id)
