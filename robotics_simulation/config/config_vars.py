from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
load_dotenv()

class ConfigVar(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Robotics Configuration - MuJoCo ---
    ROBOT_SCENE: str
    SIMULATE_DT:float
    CAMERA_ACTIVATED: bool
    AI_DETECT_OBJECTS: bool
    FORWARD: str
    BACKWARDS: str
    STOP: str
    LEFT_UP: str
    RIGHT_UP: str
    LEFT_DOWN: str
    RIGHT_DOWN: str
    CAMERA_WIDTH: int
    CAMERA_HEIGHT: int
    XML_CAMERA_NAME: str
    TOPIC_ROS2_CAMERA: str

    # Computer Vision Configuration
    COMPUTER_VISION_MODEL: str
    VISION_PREDICTION_FOLDER: str
    SAVE_VISION_PREDICTION: bool
    PREFERRED_CONFIDENCE: float
    AWS_IOT_ENDPOINT: str
    IMAGE_DETECTION_BUCKET: str

    # Nvidia Configuration
    CUDNN_LIBRARY_PATH: str
    CUDNN_ENABLED: bool
    CUDNN_BENCHMARK: bool
    CUDNN_DETERMINISTIC: bool

    # Cloud
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_IOT_ENDPOINT: str
    AWS_IOT_CLIENT_ID = "robot_truck_01"
    AWS_IOT_TOPIC = "robotics/vision/detections"
    AWS_IOT_PATH_TO_CERTIFICATE = "certs/device.pem.crt"
    AWS_IOT_PATH_TO_PRIVATE_KEY = "certs/private.pem.key"
    AWS_IOT_PATH_TO_AMAZON_ROOT_CA = "certs/AmazonRootCA1.pem"
    IMAGE_DETECTION_BUCKET: str

config = ConfigVar()