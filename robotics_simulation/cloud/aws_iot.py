import json
from config.config_vars import config
import json
from awscrt import mqtt
from awsiot import mqtt_connection_builder
import structlog
logger = structlog.get_logger()

class AWSIoT():
    _singleton = None
    _is_already_initialized = False

    def __init__(self):
        if not self._is_already_initialized:
            self.connection = self._get_client()
            self._is_already_initialized = True

    def _get_client(self):
        try:
            logger.info("Initializing AWS IoT Connection")
            connection = mqtt_connection_builder.mtls_from_path(
                endpoint=config.AWS_IOT_ENDPOINT,
                cert_filepath=config.AWS_IOT_PATH_TO_CERTIFICATE,
                pri_key_filepath=config.AWS_IOT_PATH_TO_PRIVATE_KEY,
                ca_filepath=config.AWS_IOT_PATH_TO_AMAZON_ROOT_CA,
                client_id=config.AWS_IOT_CLIENT_ID,
                clean_session=False,
                keep_alive_secs=30
            )
            connection.connect().result()
            logger.info("AWS IoT connection Properly Initialized")
            return connection
        except Exception as e:
            logger.error("Error connecting to AWS IoT", error=str(e), exc_info=True)
            raise Exception(e)

    def publish_mqtt(self, payload, topic):
        self.connection.publish(
            topic=topic,
            payload=payload,
            qos=mqtt.QoS.AT_LEAST_ONCE
        )
        logger.info("MQTT payload sent to AWS IoT. Payload: %s", payload)

    def disconnect(self):
        self.connection.disconnect().result()
        logger.info("AWS IoT connection successfully closed")
    
    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super(AWSIoT, cls).__new__(cls)
        return cls._singleton
