import rclpy
import config
from sensor_msgs.msg import Image as ROSImage
from cv_bridge import CvBridge
import orbslam3
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import TransformStamped
from tf2_ros import StaticTransformBroadcaster
import numpy as np

class Scan3D:
    def __init__(self):
        rclpy.init()
        self.node = rclpy.create_node("scan_3d")
        self.bridge = CvBridge()

        # Initialize the broadcaster and publish the map transform hierarchy
        self.tf_static_broadcaster = StaticTransformBroadcaster(self.node)
        self.publish_static_transform()

        # Reference the vocabulary file and your newly generated YAML settings
        self.slam = orbslam3.System(
            "config_orbslam3/ORBvoc.txt", 
            "config_orbslam3/mujoco_camera_config.yaml",  # Handled natively by ORB-SLAM3 here
            orbslam3.Sensor.MONOCULAR
        )
        self.node.create_subscription(ROSImage, config.CAMERA_TOPIC_ROS2, self.scan_mujoco_camera_frame, 10)
        # Global Publishers for Foxglove Bridge to listen to
        self.pose_pub = self.node.create_publisher(PoseStamped, '/mining_terrain_4', 10)

    def publish_static_transform(self):
        t = TransformStamped()
        t.header.stamp = self.node.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'map'
        
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 0.0
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 1.0

        self.tf_static_broadcaster.sendTransform(t)
        
    def scan_mujoco_camera_frame(self, msg):
        cv_img = self.bridge.imgmsg_to_cv2(msg, "passthrough")
        timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

        # Process image and capture the matrix output
        t_raw = self.slam.process_image_mono(cv_img, timestamp)
        print("[ORB-SLAM-3] Image extracted from ROS2 topic")
        # Extract spatial orientation if ORB-SLAM3 has a valid tracking lock
        if t_raw is not None and isinstance(t_raw, np.ndarray) and t_raw.shape == (4, 4):
            pose_msg = PoseStamped()
            pose_msg.header.stamp = self.node.get_clock().now().to_msg()
            pose_msg.header.frame_id = "map"
            
            # Correctly slice indices for 3D coordinates to prevent single scalar exceptions
            pose_msg.pose.position.x, pose_msg.pose.position.y, pose_msg.pose.position.z = t_raw[0:3, 3].astype(float)
            
            # Extract rotation slice
            r = t_raw[0:3, 0:3]
            
            # Vectorized mapping for conversion algorithm
            qw = np.sqrt(max(0.0, 1.0 + r[0,0] + r[1,1] + r[2,2])) / 2.0
            qx = np.sqrt(max(0.0, 1.0 + r[0,0] - r[1,1] - r[2,2])) / 2.0
            qy = np.sqrt(max(0.0, 1.0 - r[0,0] + r[1,1] - r[2,2])) / 2.0
            qz = np.sqrt(max(0.0, 1.0 - r[0,0] - r[1,1] + r[2,2])) / 2.0
            
            # Pack attributes cleanly using tuple unpacking expressions
            pose_msg.pose.orientation.x = float(np.copysign(qx, r[2,1] - r[1,2]))
            pose_msg.pose.orientation.y = float(np.copysign(qy, r[0,2] - r[2,0]))
            pose_msg.pose.orientation.z = float(np.copysign(qz, r[1,0] - r[0,1]))
            pose_msg.pose.orientation.w = float(qw)
            
            self.pose_pub.publish(pose_msg)

    def start_scan(self):
        rclpy.spin(self.node)
        self.slam.shutdown()

if __name__ == '__main__':
    Scan3D().start_scan()
