from config import config_nvidia
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image as ROSImage
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from cv_bridge import CvBridge
from config.config_vars import config
import ORBSLAM3Python as orbslam
import structlog
logger = structlog.get_logger()

class ORBSLAM3Tracker:
    def __init__(self):
        self.bridge = CvBridge()
        self.node = rclpy.create_node('scan_scene')
        logger.info("Starting ORB-SLAM3")
        self.slam_system = orbslam.System(
            config.ORB_VOCAB_PATH,
            config.ORB_SETTINGS_PATH,
            orbslam.Sensor.MONOCULAR,
            True
        )
        self.pub = self.node.create_publisher(PointCloud2, config.TOPIC_3D_SCENE, 10)
        self.node.create_subscription(ROSImage, config.TOPIC_ROS2_CAMERA, self.retrieve_ros2_image, 10)

    def retrieve_ros2_image(self, msg):
        ros2_captured_image = self.bridge.imgmsg_to_cv2(msg, "passthrough")
        self.detect_object(ros2_captured_image, msg.header.stamp)

    def detect_object(self, ros2_captured_image, stamp):
        timestamp = stamp.sec + (stamp.nanosec * 1e-9)
        self.slam_system.TrackMonocular(ros2_captured_image, timestamp)
        map_points = self.slam_system.GetTrackedMapPoints()

        if config.SEND_TO_CLOUD_SERVICE and map_points:
            current_time = self.node.get_clock().now().to_msg()
            cloud_msg = point_cloud2.create_cloud_xyz32(current_time, [[p.x, p.y, p.z] for p in map_points])
            cloud_msg.header.frame_id = getattr(config, "FOXGLOVE_FRAME_ID", "map")
            self.pub.publish(cloud_msg)

    def destroy(self):
        logger.info("Stopping ORB-SLAM3")
        self.slam_system.Shutdown()
        self.node.destroy_node()

def main():
    rclpy.init()
    tracker = ORBSLAM3Tracker()
    try:
        rclpy.spin(tracker.node)
    except KeyboardInterrupt:
        pass
    finally:
        tracker.destroy()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
