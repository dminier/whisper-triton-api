import uvicorn

PORT = 7000

if __name__ == "__main__":

    uvicorn.run("speech2text.application.app:app", host="0.0.0.0", port=PORT, reload=True, log_level="error")
