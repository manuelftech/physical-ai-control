from config import config_nvidia
from schemas.detection_payload import DetectionPayload
from ultralytics import YOLO
from core.utils import get_latest_predicted_image, remove_folder
from sensor_msgs.msg import Image as ROSImage
from cv_bridge import CvBridge
from config.config_vars import config
from cloud.aws_iot import AWSIoT
from cloud.aws_s3 import AWSS3
from config.logger import configure_logger
from rclpy.node import Node
from datetime import datetime, timezone
import json
import uuid
import rclpy
import time
import structlog
logger = structlog.get_logger()

class VisionDetectionNode(Node):
    def __init__(self):
        super().__init__('vision_detection')
        self.bridge = CvBridge()
        self.model = YOLO(config.COMPUTER_VISION_MODEL)
        
        # ROS2 Subscription listening directly to your configured camera topic
        self.subscription = self.create_subscription(
            ROSImage, 
            config.TOPIC_ROS2_CAMERA, 
            self.retrieve_ros2_image, 
            10
        )
        logger.info("Vision Detection Node initialized successfully.")

    def retrieve_ros2_image(self, msg):
        ros2_captured_image = self.bridge.imgmsg_to_cv2(msg, "passthrough")
        self.detect_object(ros2_captured_image)

    def detect_object(self, cv_img):
        remove_folder(config.VISION_PREDICTION_FOLDER)
        results = self.model.predict(
            cv_img,
            conf=0.25,
            imgsz=640,
            save=config.SAVE_VISION_PREDICTION,
            project=config.VISION_PREDICTION_FOLDER,
            name="predict",
            exist_ok=True
        )
        self.identify_rock_with_truck(results)

    def identify_rock_with_truck(self, results):
        rock_found = False
        truck_found = False
        confidence = 0.0

        for box in results[0].boxes:
            name = self.model.names[int(box.cls)]
            confidence = float(box.conf)
            if name == "rock":
                rock_found = True
            elif name == "truck":
                truck_found = True

        if not rock_found or not truck_found:
            logger.info("No rocks near trucks")
            return

        process_id = str(uuid.uuid4())
        logger.info("Rock found near Truck")

        if confidence < config.PREFERRED_CONFIDENCE:
            logger.info("Image predicted with confidence below threshold. Confidence: %s", confidence)
            # Route lower confidence visuals out to the external asynchronous Agent auditor
            file_path = get_latest_predicted_image(config.VISION_PREDICTION_FOLDER)
            date_prefix = datetime.now(timezone.utc).strftime(config.DATE_FORMAT_BUCKET_FOLDER)
            
            AWSS3().upload_image(
                object_name=f"{date_prefix}/{process_id}",
                file_path=file_path,
                bucket=config.IMAGE_DETECTION_BUCKET
            )
        else:
            logger.info("Image predicted with high confidence. Confidence: %s", confidence)
            payload = DetectionPayload(
                device_id=config.AWS_IOT_CLIENT_ID,
                process_id=process_id,
                element_type="rock_near_truck",
                alert_level="warning",
                timestamp=int(time.time()),
                prediction_confidence=confidence
            )
            AWSIoT().publish_mqtt(
                topic=config.AWS_IOT_TOPIC,
                payload=json.dumps(payload.model_dump()))
        # Standard execution buffering window to limit stream notification flooding
        time.sleep(config.TIME_BEFORE_NEXT_PREDICTION)

def main():
    logger.info("Starting Vision Detection Process")
    AWSS3()
    AWSIoT()
    rclpy.init()
    node = VisionDetectionNode()
    try:
        rclpy.spin(node)
    finally:
        AWSIoT().disconnect()
        node.destroy_node()
        rclpy.shutdown()
        logger.info("Vision Detection Process Stopped")

if __name__ == '__main__':
    main()
