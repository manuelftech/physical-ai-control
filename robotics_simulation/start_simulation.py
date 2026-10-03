from movement_config import stabilize_robot
from interface_config import add_gui_movement_buttons
from vision_detection import identify_element
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
    renderer = mujoco.Renderer(mj_model, width=config.CAMERA_WIDTH, height=config.CAMERA_HEIGHT)

    if os.path.exists(config.CAMERA_FOLDER):
        shutil.rmtree(config.CAMERA_FOLDER)
    os.makedirs(config.CAMERA_FOLDER, exist_ok=True)

    frame_count = 0
    while True:
        # Configure amount of images captured per second
        time.sleep(0.3)

        with locker:
            # Synchronize model data state into the renderer instance
            renderer.update_scene(mj_data, camera=config.XML_CAMERA_NAME)

        # Draw and capture raw RGB array pixel buffers, Parse and immediately dump arrays straight into JPG formats
        img_filename = "{}/{:04d}.jpg".format(config.CAMERA_FOLDER, frame_count)
        Image.fromarray(renderer.render()).save(img_filename)
        identify_element(img_filename=img_filename)
        frame_count += 1

def initialize_robot():
    viewer = Viewer(mj_model, mj_data, step_fn=stabilize_robot)

    viewer._server.scene.configure_environment_map(
        hdri="night",                # Switches background texture to night sky
        background=True,             # Ensures the sky map is visible
        background_blurriness=0.0,   # Keep it as sharp as possible
        background_intensity=0.6,    # Lowers the sky brightness so it feels dark
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
    initialize_robot()
