
import uvicorn
import webbrowser


PORT = 7000

if __name__ == "__main__":
    webbrowser.open_new(f"http://localhost:{PORT}/docs")
    uvicorn.run("speech2text.application.app:app", host="0.0.0.0", port=PORT, reload=True, log_level="debug")

