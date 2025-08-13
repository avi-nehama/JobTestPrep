import json
import time
import uuid
import logging
from typing import Dict, Any
import os

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

from .base import PayloadStorage, StorageError

logger = logging.getLogger(__name__)


class S3PayloadStorage(PayloadStorage):
    """S3-based implementation of payload storage."""
    
    def __init__(self, 
                 bucket_name: str = None,
                 aws_access_key_id: str = None,
                 aws_secret_access_key: str = None,
                 aws_region: str = None,
                 prefix: str = "payloads/"):
        """
        Initialize S3 storage.
        
        Args:
            bucket_name: S3 bucket name (defaults to env var S3_BUCKET_NAME)
            aws_access_key_id: AWS access key (defaults to env var AWS_ACCESS_KEY_ID)
            aws_secret_access_key: AWS secret key (defaults to env var AWS_SECRET_ACCESS_KEY)
            aws_region: AWS region (defaults to env var AWS_REGION)
            prefix: Key prefix for stored objects
        """
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for S3 storage. Install with: pip install boto3")
        
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME")
        if not self.bucket_name:
            raise ValueError("S3_BUCKET_NAME environment variable or bucket_name parameter is required")
        
        self.aws_access_key_id = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = aws_region or os.getenv("AWS_REGION", "us-east-1")
        self.prefix = prefix.rstrip("/") + "/"
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region
        )
        
        logger.info(f"S3 storage initialized for bucket: {self.bucket_name}")
    
    async def store(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store payload as JSON in S3.
        
        Args:
            payload: The payload dictionary to store
            
        Returns:
            Dictionary containing storage metadata
            
        Raises:
            StorageError: If storage operation fails
        """
        try:
            # Generate unique key
            timestamp = int(time.time())
            unique_id = uuid.uuid4().hex
            key = f"{self.prefix}{timestamp}_{unique_id}.json"
            
            logger.info(f"Storing payload to S3: {key}")
            
            # Convert payload to JSON string
            payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=payload_json,
                ContentType='application/json'
            )
            
            logger.info("Payload stored successfully in S3", extra={"key": key})
            
            return {
                "status": "stored",
                "bucket": self.bucket_name,
                "key": key,
                "url": f"s3://{self.bucket_name}/{key}",
                "timestamp": timestamp,
                "storage_type": "s3"
            }
            
        except NoCredentialsError as error:
            logger.error("AWS credentials not found")
            raise StorageError("AWS credentials not configured properly")
        except ClientError as error:
            error_code = error.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                logger.error(f"S3 bucket not found: {self.bucket_name}")
                raise StorageError(f"S3 bucket not found: {self.bucket_name}")
            elif error_code == 'AccessDenied':
                logger.error("Access denied to S3 bucket")
                raise StorageError("Access denied to S3 bucket")
            else:
                logger.exception("S3 client error")
                raise StorageError(f"S3 storage failed: {str(error)}")
        except Exception as error:
            logger.exception("Failed to store payload to S3")
            raise StorageError(f"Failed to store payload: {str(error)}")
    
