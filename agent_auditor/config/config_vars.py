from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()

class ConfigVar(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- AWS IoT Configuration ---
    ALERT_LEVEL_PREDICTION: str
    CLASSIFICATION_ELEMENT_FOUND: str

    # --- OpenAI Configuration ---
    LLM_MODEL: str
    AGENT_NAME: str

config = ConfigVar()