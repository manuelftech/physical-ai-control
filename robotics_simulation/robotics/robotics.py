from config import config_nvidia
from movement_config import stabilize_robot
from interface_config import add_gui_movement_buttons
from sensor_msgs.msg import Image as ROSImage
from cv_bridge import CvBridge
from config.config_vars import config
from mjviser import Viewer
from PIL import Image
import threading
import mujoco
import shutil
import rclpy
import time
import os
import structlog
logger = structlog.get_logger()

locker = threading.Lock()
mj_model = mujoco.MjModel.from_xml_path(config.ROBOT_SCENE)
mj_data = mujoco.MjData(mj_model)
mj_model.opt.timestep = config.SIMULATE_DT
num_motor_ = mj_model.nu
dim_motor_sensor_ = 3 * num_motor_
time.sleep(0.2)

rclpy.init()
node = rclpy.create_node("robotics_simulation")
pub = node.create_publisher(ROSImage, config.TOPIC_ROS2_CAMERA, 10)
bridge = CvBridge()

def record_camera():
    renderer = mujoco.Renderer(mj_model, width=config.CAMERA_WIDTH, height=config.CAMERA_HEIGHT)

    frame_count = 0
    while True:
        # Configure amount of images captured per second
        time.sleep(0.3)

        with locker:
            # Synchronize model data state into the renderer instance
            renderer.update_scene(mj_data, camera=config.XML_CAMERA_NAME)

        # Sending image to ROS2 topic
        img_rgb = renderer.render()
        ros2_captured_image = bridge.cv2_to_imgmsg(img_rgb, encoding="passthrough")
        pub.publish(ros2_captured_image)
        frame_count += 1

def start_robotics_simulation():
    viewer = Viewer(mj_model, mj_data, step_fn=stabilize_robot)
    viewer._server.scene.configure_environment_map(
        hdri="night",
        background=True,
        background_blurriness=0.0,
        background_intensity=0.6,
        environment_intensity=2.5
    )

    # Add buttons to the Viser GUI
    viewer = add_gui_movement_buttons(viewer=viewer)

    if config.CAMERA_ACTIVATED:
        # Record video from the Robot Camera
        stream_thread = threading.Thread(target=record_camera, daemon=True)
        stream_thread.start()

    viewer.run()

if __name__ == "__main__":
    logger.info("Initializing simulation")
    start_robotics_simulation()