import logging
import uvicorn
from api import app  # Import the FastAPI app from `api/__init__.py`

def start_app():
    # loging
    logging.basicConfig(level=logging.DEBUG)

    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    start_app()

