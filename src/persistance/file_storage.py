import json
import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Any

from .base import PayloadStorage, StorageError

logger = logging.getLogger(__name__)


class FilePayloadStorage(PayloadStorage):
    """File-based implementation of payload storage."""
    
    def __init__(self, data_directory: str = "/code/data"):
        """
        Initialize file-based storage.
        
        Args:
            data_directory: Directory where payload files will be stored
        """
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"File storage initialized at {self.data_directory}")
    
    async def store(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store payload as a JSON file.
        
        Args:
            payload: The payload dictionary to store
            
        Returns:
            Dictionary containing storage metadata
            
        Raises:
            StorageError: If storage operation fails
        """
        try:
            # Generate unique filename
            file_name = f"{int(time.time())}_{uuid.uuid4().hex}.json"
            file_path = self.data_directory / file_name
            
            logger.info("Storing payload to file")
            
            # Write payload to file
            with file_path.open("w", encoding="utf-8") as file_handle:
                json.dump(payload, file_handle, ensure_ascii=False, indent=2)
            
            logger.info("Payload stored successfully", extra={"path": str(file_path)})
            
            return {
                "status": "stored",
                "path": str(file_path),
                "filename": file_name,
                "timestamp": int(time.time())
            }
            
        except Exception as error:
            logger.exception("Failed to store payload to file")
            raise StorageError(f"Failed to store payload: {str(error)}")
    