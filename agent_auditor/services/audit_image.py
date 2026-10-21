from schemas.detection_payload import DetectionPayload
from schemas.audit_response import AuditResponse
from config.openai_agent import OpenAIAgent
from config.aws_iot import AWSIoT
from config.config_vars import config
from config.aws_s3 import AWSS3
from core.utils import read_file
from agents import trace
import asyncio
import urllib.parse
import json
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
            {"type": "message","role": "system", 
             "content": [{"type": "input_text", "text": read_file(config.PROMPT_INSTRUCTIONS_FILE)}]},
            {"type": "message", "role": "user", 
             "content": [{"type": "input_image", "image_url": image_url}]}
        ]

        with trace("Json_DetectionPayload_Flow"):
            response = asyncio.run(
                OpenAIAgent().run_agent(
                    name=config.AGENT_NAME,
                    instructions=instructions,
                    output_type=AuditResponse
                ))

        if not response.final_output.image_properly_predicted:
            logger.warning("Agent rejected prediction. Image URL: %s, Agent Feedback: %s", image_url, response.final_output.feedback)
            return

        logger.info("Agent aproved prediction. Image URL: %s, Agent Feedback: %s", image_url, response.final_output.feedback)
        process_id = str(uuid.uuid4())
        payload = DetectionPayload(
                device_id=config.AWS_IOT_CLIENT_ID,
                process_id = process_id,
                element_type=config.CLASSIFICATION_ELEMENT_FOUND,
                alert_level=config.ALERT_LEVEL_PREDICTION,
                prediction_confidence=response.final_output.confidence,
                timestamp=int(time.time())
            )
        AWSIoT().publish_mqtt(
            topic=config.AWS_IOT_TOPIC,
            payload=json.dumps(payload.model_dump())
            )
        logger.info("MQTT payload sent to AWS IoT. Topic: %s, Process ID: %s", config.AWS_IOT_CLIENT_ID, process_id)
