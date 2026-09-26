from movement_config import stabilize_robot
from interface_config import add_gui_movement_buttons
from mjviser import Viewer
from PIL import Image
import time
import mujoco
import threading
import config
import shutil
import os

locker = threading.Lock()
mj_model = mujoco.MjModel.from_xml_path(config.ROBOT_SCENE)
mj_data = mujoco.MjData(mj_model)
mj_model.opt.timestep = config.SIMULATE_DT
num_motor_ = mj_model.nu
dim_motor_sensor_ = 3 * num_motor_
time.sleep(0.2)

def record_camera():
    XML_CAMERA_NAME = "go2w_camera"
    CAMERA_FOLDER = "recording"
    WIDTH, HEIGHT = 640, 480
    renderer = mujoco.Renderer(mj_model, width=WIDTH, height=HEIGHT)

    if os.path.exists(CAMERA_FOLDER):
        shutil.rmtree(CAMERA_FOLDER)
    os.makedirs(CAMERA_FOLDER, exist_ok=True)

    frame_count = 0
    while True:
        # Configure amount of images captured per second
        time.sleep(0.5)

        with locker:
            # Synchronize model data state into the renderer instance
            renderer.update_scene(mj_data, camera=XML_CAMERA_NAME)

        # Draw and capture raw RGB array pixel buffers, Parse and immediately dump arrays straight into JPG formats
        Image.fromarray(renderer.render()).save("{}/{:04d}.jpg".format(CAMERA_FOLDER, frame_count))
        frame_count += 1

def initialize_robot():
    viewer = Viewer(mj_model, mj_data, step_fn=stabilize_robot)

    # Add buttons to the Viser GUI
    viewer = add_gui_movement_buttons(viewer=viewer)

    # Record video from the Robot Camera
    stream_thread = threading.Thread(target=record_camera, daemon=True)
    stream_thread.start()

    viewer.run()

if __name__ == "__main__":
    initialize_robot()
