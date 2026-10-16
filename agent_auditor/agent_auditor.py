from schemas.auditing_mining_predictions import AuditingMiningPredictions
from repositories.auditing_repository import AutidingDynamoDBRepository
from agents import trace
from config.openai_agent import OpenAIAgent
from config.config_vars import config
import time
from config.aws_s3 import AWSS3
import asyncio
import urllib.parse
import uuid
import structlog
logger = structlog.get_logger()

def lambda_handler(event, context):
        """
        Processes Images to verify and audit if the objects were properly detected
        """

        s3_record = event['Records'][0]['s3']

        image_url = AWSS3().get_image_signed_url(
            object_key=urllib.parse.unquote_plus(s3_record['object']['key']), 
            bucket=s3_record['bucket']['name'])

        instructions = [{"type": "text", "text": config.PROMPT_INSTRUCTIONS}]
        instructions.append({"type": "image_url", "image_url": {"url": image_url }})
        instructions = [{"role": "user", "content": instructions}]
        
        with trace("Json_Template_Generation_Flow"): 
                    coroutine = OpenAIAgent().run_agent(
                        name=config.AGENT_TEMPLATE,
                        instructions=instructions,
                        output_type=AuditingMiningPredictions
                    )
                    
                    response = asyncio.get_event_loop().run_until_complete(coroutine)
        process_id = str(uuid.uuid4())
        response.final_output.process_id = process_id
        response.final_output.audit_timestamp = int(time.time())
        response.final_output.image_url = image_url

        logger.info("Agent Auditor processed incoming image. Process ID: %s, Image URL: %s", process_id, image_url)

        return response.final_output