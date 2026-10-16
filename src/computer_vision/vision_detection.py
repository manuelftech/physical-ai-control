from config import config_nvidia
from schemas.detection_payload import DetectionPayload
from ultralytics import YOLO
from core.utils import get_latest_predicted_image
from sensor_msgs.msg import Image as ROSImage
from cv_bridge import CvBridge
from config.config_vars import config
from cloud.aws_iot import AWSIoT
from cloud.aws_s3 import AWSS3
from config.logger import configure_logger
import uuid
import rclpy
import time
import structlog
logger = structlog.get_logger()

def detect_object(cv_img):
    model = YOLO(config.COMPUTER_VISION_MODEL)
    results = model.predict(
        cv_img,
        conf=0.25,
        imgsz=640,
        save=config.SAVE_VISION_PREDICTION,
        project=config.VISION_PREDICTION_FOLDER,
        name="predict",
        exist_ok=True
        )

    identify_rock_with_truck(model=model, results=results)

def identify_rock_with_truck(model, results):
    rock_found = False
    truck_found = False

    for box in results[0].boxes:
        name = model.names[int(box.cls)]
        confidence = float(box.conf)

        if name == "rock" and confidence > config.ACCEPTED_CONFIDENCE:
            rock_found = True
        elif name == "truck" and confidence > config.ACCEPTED_CONFIDENCE:
            truck_found = True

    if rock_found and truck_found:
        logger.info("Rock found near Truck")

        file_path = get_latest_predicted_image(config.VISION_PREDICTION_FOLDER)

        process_id = str(uuid.uuid4())
        image_url = AWSS3().upload_image(
            file_path=file_path, 
            bucket=config.IMAGE_DETECTION_BUCKET)

        logger.info("Yolo image sent to AWS S3. Process ID: %s, Image URL: %s", process_id, image_url)

        payload = DetectionPayload(
            process_id = process_id,
            element_type="rock_near_truck",
            alert_level="warning",
            timestamp=int(time.time()),
            image_url=image_url,
            prediction_confidence=confidence
            )
        
        AWSIoT().publish_mqtt(payload)
        logger.info("MQTT payload sent to AWS IoT. Process ID: %s", process_id)
        time.sleep(6)
    else:
        logger.info("No rocks near trucks")

def main():
    rclpy.init()
    node = rclpy.create_node('vision_detection')
    bridge = CvBridge()

    def retreive_ros2_image(msg):
        ros2_captured_image = bridge.imgmsg_to_cv2(msg, "passthrough")
        detect_object(ros2_captured_image)

    node.create_subscription(ROSImage, config.TOPIC_ROS2_CAMERA, retreive_ros2_image, 10)
    rclpy.spin(node)

if __name__ == '__main__':
    main()