from movement_config import stabilize_robot
from interface_config import add_gui_movement_buttons
from mjviser import Viewer
import os
from PIL import Image
import time
import mujoco
import threading
import config
import shutil

locker = threading.Lock()
mj_model = mujoco.MjModel.from_xml_path(config.ROBOT_SCENE)
mj_data = mujoco.MjData(mj_model)
mj_model.opt.timestep = config.SIMULATE_DT
num_motor_ = mj_model.nu
dim_motor_sensor_ = 3 * num_motor_
time.sleep(0.2)


def initialize_simulation():
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

    viewer.run()

if __name__ == "__main__":
    print("Initializing simulation")
    initialize_simulation()
