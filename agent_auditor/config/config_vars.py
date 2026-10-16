from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()

class ConfigVar(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- DynamoDB Configuration ---
    AUDITING_TABLE_DYNAMODB: str

    # --- OpenAI Configuration ---
    LLM_MODEL: str

config = ConfigVar()