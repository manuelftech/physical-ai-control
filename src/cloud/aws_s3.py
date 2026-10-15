import os
import boto3
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
            client = boto3.client("s3")
            logger.info("AWS S3 Client Properly Initialized")
            return client
        except Exception as e:
            logger.error("Error connecting to AWS IoT")
            raise Exception(e)

    def upload_image(self, file_path, bucket):
        object_name = os.path.basename(file_path) 
        self.client.upload_file(
            file_path,
            bucket,
            object_name,
            ExtraArgs={"ACL": "public-read", "ContentType": "image/jpeg"}
        )

        region = self.client.meta.region_name
        public_url = f"https://{bucket}.s3.{region}://{object_name}"
        return public_url
    
    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super(AWSS3, cls).__new__(cls)
        return cls._singleton

