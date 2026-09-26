from movement_control import stabilize_robot
from user_interface import add_gui_movement_buttons
import time
import mujoco
import threading
import config
from mjviser import Viewer
locker = threading.Lock()
mj_model = mujoco.MjModel.from_xml_path(config.ROBOT_SCENE)
mj_data = mujoco.MjData(mj_model)
mj_model.opt.timestep = config.SIMULATE_DT
num_motor_ = mj_model.nu
dim_motor_sensor_ = 3 * num_motor_
time.sleep(0.2)

def initialize_simulation():
    viewer = Viewer(mj_model, mj_data, step_fn=stabilize_robot)
    viewer = add_gui_movement_buttons(viewer=viewer)
    viewer.run()

if __name__ == "__main__":
    initialize_simulation()
