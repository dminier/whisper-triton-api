
import uvicorn

if __name__ == "__main__":
    uvicorn.run("speech2text.application.app:app", host="0.0.0.0", port=7000, reload=False, log_level="error")
