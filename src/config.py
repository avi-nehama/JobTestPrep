import os
import logging

from .persistance import FilePayloadStorage, S3PayloadStorage, PayloadStorage


def get_storage_backend() -> PayloadStorage:
    """
    Factory function to get the appropriate storage backend based on configuration.
    
    Returns:
        Configured storage backend instance
    """
    storage_type = os.getenv("STORAGE_TYPE", "file").lower()
    
    if storage_type == "s3":
        bucket_name = os.getenv("S3_BUCKET_NAME")
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        prefix = os.getenv("S3_PREFIX", "payloads/")

        return S3PayloadStorage(
            bucket_name=bucket_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_region=aws_region,
            prefix=prefix,
        )
    elif storage_type == "file":
        data_directory = os.getenv("DATA_DIRECTORY", "./data")
        return FilePayloadStorage(data_directory=data_directory)
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")


# Environment variable documentation
ENV_VARS = {
    "STORAGE_TYPE": "Storage backend to use ('file' or 's3')",
    "DATA_DIRECTORY": "Directory for file storage (default: /code/data)",
    "S3_BUCKET_NAME": "S3 bucket name for S3 storage",
    "AWS_ACCESS_KEY_ID": "AWS access key ID",
    "AWS_SECRET_ACCESS_KEY": "AWS secret access key", 
    "AWS_REGION": "AWS region (default: us-east-1)",
    "S3_PREFIX": "S3 key prefix for stored objects (default: payloads/)"
}
