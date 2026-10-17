import os
import boto3
from config.config_vars import config
import structlog
logger = structlog.get_logger()

class AWSS3():
    _singleton = None
    _is_already_initialized = False

    def __init__(self):
        if not self._is_already_initialized:
            self.client = self._get_client()
            self._is_already_initialized = True

    def _get_client(self):
        try:
            logger.info("Initializing AWS S3 Client")
            client = boto3.client(
                "s3",
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                region_name=config.AWS_REGION
            )
            client.list_buckets()
            logger.info("AWS S3 Client Properly Initialized")
            return client
        except Exception as e:
            logger.error("Error connecting to AWS S3", error=str(e), exc_info=True)
            raise Exception(e)

    def get_image_signed_url(self, object_key, bucket):
            # Generates a secure, temporary view link valid for 60 seconds
            image_path = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': object_key},
                ExpiresIn=60
            )
            return image_path
    
    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super(AWSS3, cls).__new__(cls)
        return cls._singleton