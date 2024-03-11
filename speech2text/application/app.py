from fastapi import FastAPI

from .api import router

app = FastAPI()

app.include_router(router=router)


@app.get("/")
async def root():
    return {"message": "Hello Speech2Text!"}
