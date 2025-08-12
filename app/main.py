from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pathlib import Path
import json
import time
import uuid

app = FastAPI()

@app.get("/", status_code=200, response_class=PlainTextResponse)
def read_root():
    return "200OK"


@app.post("/store", status_code=201)
async def store_payload(payload: dict):
    """Accepts arbitrary JSON and stores it on the filesystem.

    Files are written to /code/data inside the container/host volume.
    """
    try:
        data_directory = Path("/code/data")
        data_directory.mkdir(parents=True, exist_ok=True)

        file_name = f"{int(time.time())}_{uuid.uuid4().hex}.json"
        file_path = data_directory / file_name

        with file_path.open("w", encoding="utf-8") as file_handle:
            json.dump(payload, file_handle, ensure_ascii=False, indent=2)

        return {"status": "stored", "path": str(file_path)}
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))