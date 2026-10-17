from config import config_nvidia
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image as ROSImage
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2
from cv_bridge import CvBridge
from config.config_vars import config
import cv2
import open3d as o3d
import numpy as np

class Scene3DNode(Node):
    def __init__(self):
        super().__init__('scene_3d')
        self.bridge = CvBridge()
        self.intrinsics = o3d.camera.PinholeCameraIntrinsic(
            config.CAMERA_WIDTH, 
            config.CAMERA_HEIGHT, 
            530.0, 
            530.0, 
            config.CAMERA_WIDTH / 2.0, 
            config.CAMERA_HEIGHT / 2.0)
        
        self.pub = self.create_publisher(PointCloud2, config.TOPIC_3D_SCENE, 10)
        self.sub = self.create_subscription(ROSImage, config.TOPIC_ROS2_CAMERA, self.retreive_ros2_image, 10)

    def retreive_ros2_image(self, msg):
        cv_img = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        self.scan_3d_cloud_points(cv_img)

    def scan_3d_cloud_points(self, cv_img):
        rgb_o3d = o3d.geometry.Image(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
        
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        depth_matrix = np.uint16(10000.0 / (cv2.Laplacian(gray, cv2.CV_64F) + 1.0))
        depth_o3d = o3d.geometry.Image(depth_matrix)
        
        rgbd = o3d.geometry.RGBDImage.create_from_color_and_depth(rgb_o3d, depth_o3d, depth_scale=1000.0, convert_rgb_to_intensity=False)
        pcd = o3d.geometry.PointCloud.create_from_rgbd_image(rgbd, self.intrinsics)

        if config.SEND_TO_CLOUD_SERVICE and pcd.has_points():
            self.send_to_cloud(np.asarray(pcd.points).tolist())

    def send_to_cloud(self, points_list):
        msg = point_cloud2.create_cloud_xyz32(self.get_clock().now().to_msg(), points_list)
        msg.header.frame_id = "map"
        self.pub.publish(msg)

def main():
    rclpy.init()
    rclpy.spin(Scene3DNode())
    rclpy.shutdown()

if __name__ == '__main__':
    main()