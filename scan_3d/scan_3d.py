import rclpy
import config
from sensor_msgs.msg import Image as ROSImage
from sensor_msgs.msg import PointCloud2, PointField
import std_msgs.msg
from cv_bridge import CvBridge
import orbslam3
from geometry_msgs.msg import PoseStamped
from geometry_msgs.msg import TransformStamped
from tf2_ros import StaticTransformBroadcaster
import numpy as np
import struct

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
        self.slam.initialize()

        self.node.create_subscription(ROSImage, config.TOPIC_ROS2_CAMERA, self.scan_mujoco_camera_frame, 10)
        # Send the Camera position
        self.pose_pub = self.node.create_publisher(PoseStamped, config.TOPIC_ROS2_ROBOT_POSITION, 10)
        # Send the point cloud (3D space)
        self.cloud_pub = self.node.create_publisher(PointCloud2, config.TOPIC_ROS2_3D_SCENE, 10)
        # Send video frames
        self.debug_img_pub = self.node.create_publisher(ROSImage, config.TOPIC_ROS2_VIDEO, 10)

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
        try:
            raw_img = self.bridge.imgmsg_to_cv2(msg, "passthrough")
            if raw_img is None or raw_img.size == 0:
                            print("[DIAGNOSTIC] Received an empty image buffer from MuJoCo.")
                            return

            cv_img = raw_img[:, :, ::-1].copy() if len(raw_img.shape) == 3 else raw_img.copy()
            timestamp = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9

            # Process image and capture the matrix output
            t_raw = self.slam.process_image_mono(cv_img, timestamp)
            print(f"[ORB-SLAM-3] Image processed. Matrix return type: {type(t_raw)}")

            # Overlay tracking features onto the original image manually using your wrapper API
            import cv2
            debug_frame = raw_img.copy()
            features = None
            if hasattr(self.slam, 'get_current_points'):
                features = self.slam.get_current_points()
            elif hasattr(self.slam, 'get_keyframe_points'):
                features = self.slam.get_keyframe_points()
            
            # Draw green circles on every tracked 2D feature location found by the wrapper
            if features is not None:
                print(f"[DIAGNOSTIC] Extractor found {len(features)} active keypoints.")
                for pt in features:
                    if hasattr(pt, 'x') and hasattr(pt, 'y'):
                        cv2.circle(debug_frame, (int(pt.x), int(pt.y)), 3, (0, 255, 0), -1)
                    elif hasattr(pt, 'pt'):
                        cv2.circle(debug_frame, (int(pt.pt[0]), int(pt.pt[1])), 3, (0, 255, 0), -1)
                    elif isinstance(pt, (list, tuple, np.ndarray)) and len(pt) >= 2:
                        cv2.circle(debug_frame, (int(pt[0]), int(pt[1])), 3, (0, 255, 0), -1)
            else:
                print("[DIAGNOSTIC] Feature list is completely empty. Checker is failing.")

            debug_msg = self.bridge.cv2_to_imgmsg(debug_frame, "rgb8")
            debug_msg.header.stamp = self.node.get_clock().now().to_msg()
            debug_msg.header.frame_id = "map"
            self.debug_img_pub.publish(debug_msg)

            # Extract spatial orientation if ORB-SLAM3 has a valid tracking lock
            if t_raw is not None and isinstance(t_raw, np.ndarray) and t_raw.shape == (4, 4):                 
                print("[ORB-SLAM-3] TRACKING LOCK ACQUIRED! Publishing 3D data...")
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

                # Send camera position
                self.pose_pub.publish(pose_msg)
                # Send 3D space
                self.publish_tracked_points()
            else:
                print("[ORB-SLAM-3] Searching for tracking lock... (Drive the robot side-to-side to initialize)")

        except Exception as runtime_error:
           print(f"[CRITICAL ERROR] Crash inside callback loop: {runtime_error}")

    def publish_tracked_points(self):
        # Retrieve tracked map point arrays from active ORB-SLAM3 backend tracking context
        tracked_points = None
        if hasattr(self.slam, 'get_tracked_mappoints'):
            tracked_points = self.slam.get_tracked_mappoints()
        elif hasattr(self.slam, 'get_current_points'):
            tracked_points = self.slam.get_current_points()
        if not tracked_points or len(tracked_points) == 0:
            return

        msg = PointCloud2()
        msg.header.stamp = self.node.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.height = 1
        msg.width = len(tracked_points)
        msg.is_bigendian = False
        msg.point_step = 12
        msg.row_step = msg.point_step * msg.width
        msg.is_dense = False
        
        msg.fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1)
        ]
        
        # Flatten and pack numerical 3D structures cleanly into binary sequences
        buffer = []
        for p in tracked_points:
            if hasattr(p, 'x') and hasattr(p, 'y') and hasattr(p, 'z'):
                buffer.append(struct.pack('fff', float(p.x), float(p.y), float(p.z)))
            elif isinstance(p, (list, tuple, np.ndarray)) and len(p) >= 3:
                buffer.append(struct.pack('fff', float(p[0]), float(p[1]), float(p[2])))
        
        if len(buffer) > 0:
            msg.data = b''.join(buffer)
            self.cloud_pub.publish(msg)

    def start_scan(self):
        rclpy.spin(self.node)
        self.slam.shutdown()

if __name__ == '__main__':
    Scan3D().start_scan()
