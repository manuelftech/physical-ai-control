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
            logger.info("AWS S3 Client Properly Initialized")
            return client
        except Exception as e:
            logger.error("Error connecting to AWS S3", error=str(e), exc_info=True)
            raise Exception(e)

    def upload_image(self, file_path, bucket, object_name):
        with open(file_path, 'rb') as data:
            self.client.put_object(
                Bucket=bucket,
                Key=object_name,
                Body=data,
                ContentType="image/jpeg"
            )
        region = self.client.meta.region_name
        public_url = f"https://{bucket}.s3.{region}://{object_name}"
        logger.info("Image successfully uploaded to Bucket. Path: %s", public_url)
    
    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super(AWSS3, cls).__new__(cls)
        return cls._singleton