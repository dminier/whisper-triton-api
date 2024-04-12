from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from speech2text.application.rest.rest_api import rest_router
from speech2text.application.websocket.web_socket_api import websocket_router

app = FastAPI()
logger.info("Attach Endpoints")
app.include_router(router=rest_router)
app.include_router(router=websocket_router)


@app.get("/")
async def root():
    return  {'message': 'Hello Speech2Text!'}


@app.on_event("startup")
async def startup_event():
    logger.info("Application started.")
    pass


@app.get("/health")
async def health_check():
    return {"status": "OK"}


# TODO ONLY DEV
origins = [
    "http://localhost:8501",
    "http://localhost:7000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
