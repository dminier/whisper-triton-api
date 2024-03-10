from fastapi import APIRouter,UploadFile, File
from loguru import logger
from ..infrastrusture.speech2text.client import Client

router = APIRouter()


client = Client()

 


@router.post("/speech2text")
async def speech2text(file: UploadFile = File(...)):
    
    b = await file.read()
    
    return await client.infer(b)
