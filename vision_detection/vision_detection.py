import nvidia_config
from ultralytics import YOLO
import config
import rclpy
from sensor_msgs.msg import Image as ROSImage
from cv_bridge import CvBridge

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
    ACCEPTED_CONFIDENCE = 0.90

    for box in results[0].boxes:
        name = model.names[int(box.cls)]
        confidence = float(box.conf)
            
        if name == "rock" and confidence > ACCEPTED_CONFIDENCE:
            rock_found = True
        elif name == "truck" and confidence > ACCEPTED_CONFIDENCE:
            truck_found = True
    
    if rock_found and truck_found:
        print("Rock found near Truck")
    else:
        print("No rocks near trucks")

def main():
    print("Step 1")
    rclpy.init()
    print("Step 2")
    node = rclpy.create_node('vision_detection')
    print("Step 3")
    bridge = CvBridge()

    def retreive_ros2_image(msg):
        print("Step Inside loop")
        ros2_captured_image = bridge.imgmsg_to_cv2(msg, "passthrough")
        detect_object(ros2_captured_image)

    print("Step 4")
    node.create_subscription(ROSImage, config.TOPIC_ROS2_CAMERA, retreive_ros2_image, 10)
    print("Step 5")
    rclpy.spin(node)
    print("Step Finished")

if __name__ == '__main__':
    print("Starting it")
    main()