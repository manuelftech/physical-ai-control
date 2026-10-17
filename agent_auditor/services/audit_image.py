from schemas.detection_payload import DetectionPayload
from config.openai_agent import OpenAIAgent
from config.aws_iot import AWSIoT
from config.config_vars import config
from config.aws_s3 import AWSS3
from agents import trace
import asyncio
import urllib.parse
import uuid
import time
import structlog
logger = structlog.get_logger()

def audit_image(image_path, bucket_name):
        """
        Processes Images to verify and audit if the objects were properly detected
        """
        # Obtain a momentary image path from the predicted image
        image_url = AWSS3().get_image_signed_url(
            object_key=urllib.parse.unquote_plus(image_path),
            bucket=bucket_name
        )

        # Configure the initial one shot prompt, followed by the image to audit
        instructions = [
                {"type": "text", "text": config.PROMPT_INSTRUCTIONS},
                {"role": "user", "content": {"type": "image_url", "image_url": {"url": image_url}}}
            ]

        with trace("Json_DetectionPayload_Flow"):
            response = asyncio.get_event_loop().run_until_complete(
                OpenAIAgent().run_agent(
                    name=config.AGENT_NAME,
                    instructions=instructions,
                    output_type=DetectionPayload
                ))

        if not response.final_output.image_properly_predicted:
            logger.warning("Agent rejected prediction. Image URL: %s, Agent Feedback: %s", process_id, image_url, response.final_output.feedback)
            return

        logger.info("Agent aproved prediction. Image URL: %s, Agent Feedback: %s", process_id, image_url, response.final_output.feedback)
        process_id = str(uuid.uuid4())
        AWSIoT().publish_mqtt(
            DetectionPayload(
                device_id=config.AWS_IOT_CLIENT_ID,
                process_id = process_id,
                element_type=config.CLASSIFICATION_ELEMENT_FOUND,
                alert_level=config.ALERT_LEVEL_PREDICTION,
                prediction_confidence=response.final_output.confidence,
                timestamp=int(time.time())
            ))
        logger.info("MQTT payload sent to AWS IoT. Process ID: %s", process_id)
