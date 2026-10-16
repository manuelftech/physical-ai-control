from fastapi.encoders import jsonable_encoder
from config.config_vars import config
import boto3
import structlog
logger = structlog.get_logger()

class AutidingDynamoDBRepository():
    def __init__(self):
        self.table = boto3.resource("dynamodb").Table(config.AUDITING_TABLE_DYNAMODB)

    def save_auditing_to_table(self, auditing_mining_predictions):
        logger.info("Saving auditing to DynamoDB Table: %s, Content: %s", config.AUDITING_TABLE_DYNAMODB, auditing_mining_predictions)
        self.table.put_item(Item=jsonable_encoder(auditing_mining_predictions))
        logger.info("Auditing successfully saved to DynamoDB Table: %s", config.AUDITING_TABLE_DYNAMODB)