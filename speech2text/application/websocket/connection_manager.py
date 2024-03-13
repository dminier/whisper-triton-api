from typing import Dict

from loguru import logger
from starlette.websockets import WebSocket

from speech2text.application.whisper_spec import WhisperWaveSpec


class WebSocketWaveSession:
    def __init__(self, websocket: WebSocket, user_id: str, prompt: str = WhisperWaveSpec.DEFAULT_PROMPT):
        self.websocket: WebSocket = websocket
        self.prompt = prompt
        self.user_id = user_id
        logger.debug(f"{user_id} open WebSocketSession")

    def update_prompt_if_needed(self, prompt: str):
        if prompt:
            self.prompt = prompt

    async def close(self):
        logger.debug(f"{self.user_id} close WebSocketSession")
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass


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
