from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
import logging
import os

from .security.sanitizer import sanitize_json, remove_dollar_from_keys
from .persistance import StorageError
from .config import get_storage_backend

# Minimal, production-friendly logging setup
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
logger = logging.getLogger("app")

app = FastAPI()

# Initialize the payload storage using configuration
try:
    payload_storage = get_storage_backend()
    logger.info(f"Storage backend initialized: {type(payload_storage).__name__}")
except Exception as error:
    logger.error(f"Failed to initialize storage backend: {error}")
    raise

@app.get("/", status_code=200, response_class=PlainTextResponse)
def read_root():
    logger.info("root endpoint served")
    return "200OK"


@app.post("/payloads", status_code=201)
async def store_payload(payload: dict):
    """Accepts arbitrary JSON and stores it using the configured storage backend."""
    try:
        # Reject empty JSON objects
        if not payload:
            raise HTTPException(status_code=400, detail="Empty JSON body is not allowed")
        
        payload = remove_dollar_from_keys(payload)
        sanitized_payload = sanitize_json(payload)
        
        logger.info("storing payload")
        result = await payload_storage.store(sanitized_payload)
        logger.info("payload stored successfully")
        return result
    except StorageError as error:
        logger.exception("failed to process payload")
        raise HTTPException(status_code=500, detail=str(error))