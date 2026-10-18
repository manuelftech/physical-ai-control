import json
import boto3
from config.config_vars import config
import structlog
logger = structlog.get_logger()

class AWSIoT():
    _singleton = None
    _is_already_initialized = False

    def __init__(self):
        if not self._is_already_initialized:
            self.client = self._get_client()
            self._is_already_initialized = True

    def _get_client(self):
        try:
            logger.info("Initializing AWS IoT Client. Endpoint: %s", config.AWS_IOT_ENDPOINT)
            client = boto3.client("iot-data", endpoint_url=config.AWS_IOT_ENDPOINT)
            logger.info("AWS IoT Client Properly Initialized")
            return client
        except Exception as e:
            logger.error("Error connecting to AWS IoT", error=str(e), exc_info=True)
            raise Exception(e)

    def publish_mqtt(self, topic, payload):
        self.client.publish(
            topic=topic,
            qos=1,
            payload=json.dumps(payload)
        )
    
    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super(AWSIoT, cls).__new__(cls)
        return cls._singleton