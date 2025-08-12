from abc import ABC, abstractmethod
from typing import Dict, Any


class PayloadStorage(ABC):
    """Abstract base class for payload storage implementations."""
    
    @abstractmethod
    async def store(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a payload and return storage metadata.
        
        Args:
            payload: The payload dictionary to store
            
        Returns:
            Dictionary containing storage metadata (e.g., path, id, status)
            
        Raises:
            StorageError: If storage operation fails
        """
        pass

class StorageError(Exception):
    """Base exception for storage-related errors."""
    pass

