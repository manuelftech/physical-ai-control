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

# Actuator IDs mapping specifically to the four rolling hub motors
WHEEL_ACTUATORS = [12, 13, 14, 15]

# Controller Settings Renamed for Clarity
STIFFNESS_SPRING_FORCE = 100.0
DAMPING_SHOCK_ABSORBER = 1.0
WHEEL_BRAKE_FORCE = 50.0  # High damping value to completely seize wheel rotation

################# LEG: LEFT-UP #################
# Front-Left Leg Actuator Numerical Positions
UNION_BODY_LEG_SIDEWAYS_LEFT_UP = 3
UNION_BODY_LEG_FORWARD_LEFT_UP = 4
KNEE_LEFT_UP = 5
# Target positions for Front-Left physical unions
UNION_BODY_LEG_SIDEWAYS_LEFT_UP_TARGET = 0.0
UNION_BODY_LEG_FORWARD_LEFT_UP_TARGET = 0.67
KNEE_LEFT_UP_TARGET = -1.3

################# LEG: RIGHT-UP #################
# Front-Right Leg Actuator Numerical Positions
UNION_BODY_LEG_SIDEWAYS_RIGHT_UP = 0
UNION_BODY_LEG_FORWARD_RIGHT_UP = 1
KNEE_RIGHT_UP = 2
# Target positions for Front-Right physical unions
UNION_BODY_LEG_SIDEWAYS_RIGHT_UP_TARGET = 0.0
UNION_BODY_LEG_FORWARD_RIGHT_UP_TARGET = 0.67
KNEE_RIGHT_UP_TARGET = -1.3

################# LEG: RIGHT-DOWN #################
# Rear-Right Leg Actuator Numerical Positions
UNION_BODY_LEG_SIDEWAYS_RIGHT_DOWN = 6
UNION_BODY_LEG_FORWARD_RIGHT_DOWN = 7
KNEE_RIGHT_DOWN = 8
# Target positions for Rear-Right physical unions
UNION_BODY_LEG_SIDEWAYS_RIGHT_DOWN_TARGET = 0.0
UNION_BODY_LEG_FORWARD_RIGHT_DOWN_TARGET = 0.67
KNEE_RIGHT_DOWN_TARGET = -1.3

################# LEG: LEFT-DOWN #################
# Rear-Left Leg Actuator Numerical Positions
UNION_BODY_LEG_SIDEWAYS_LEFT_DOWN = 9
UNION_BODY_LEG_FORWARD_LEFT_DOWN = 10
KNEE_LEFT_DOWN = 11
# Target positions for Rear-Left physical unions
UNION_BODY_LEG_SIDEWAYS_LEFT_DOWN_TARGET = 0.0
UNION_BODY_LEG_FORWARD_LEFT_DOWN_TARGET = 0.67
KNEE_LEFT_DOWN_TARGET = -1.3

################# GUI BUTTON: MOVE-FORWARD #################
FORWARD_SPEED = 2.5 # Adjust this value (rad/s velocity command) to alter speed

################# GUI BUTTON: MOVE-LEFT #################
FRONT_RIGHT_WHEEL = 12
FRONT_LEFT_WHEEL = 13
REAR_RIGHT_WHEEL = 14
REAR_LEFT_WHEEL = 15
TURN_SPEED_REDUCTION = 0.1 # Slows down inside wheels to cause a turn
# Tracking variable to pass the button state safely down into the physics clock
target_speed_left = 0.0
target_speed_right = 0.0

def physics_callback(model, data):
    ################# MOVEMENT #################
    # Apply independent side speeds to make steering possible
    data.ctrl[FRONT_RIGHT_WHEEL] = target_speed_right
    data.ctrl[REAR_RIGHT_WHEEL] = target_speed_right
    data.ctrl[FRONT_LEFT_WHEEL] = target_speed_left
    data.ctrl[REAR_LEFT_WHEEL] = target_speed_left
    # Front-Left Leg Actuator Control via PD Loops
    data.ctrl[UNION_BODY_LEG_SIDEWAYS_LEFT_UP] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEG_SIDEWAYS_LEFT_UP_TARGET - data.actuator_length[UNION_BODY_LEG_SIDEWAYS_LEFT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_SIDEWAYS_LEFT_UP]
    data.ctrl[UNION_BODY_LEG_FORWARD_LEFT_UP] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEG_FORWARD_LEFT_UP_TARGET - data.actuator_length[UNION_BODY_LEG_FORWARD_LEFT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_FORWARD_LEFT_UP]
    data.ctrl[KNEE_LEFT_UP] = STIFFNESS_SPRING_FORCE * (KNEE_LEFT_UP_TARGET - data.actuator_length[KNEE_LEFT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[KNEE_LEFT_UP]
    # Front-Right Leg Actuator Control via PD Loops
    data.ctrl[UNION_BODY_LEG_SIDEWAYS_RIGHT_UP] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEG_SIDEWAYS_RIGHT_UP_TARGET - data.actuator_length[UNION_BODY_LEG_SIDEWAYS_RIGHT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_SIDEWAYS_RIGHT_UP]
    data.ctrl[UNION_BODY_LEG_FORWARD_RIGHT_UP] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEG_FORWARD_RIGHT_UP_TARGET - data.actuator_length[UNION_BODY_LEG_FORWARD_RIGHT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_FORWARD_RIGHT_UP]
    data.ctrl[KNEE_RIGHT_UP] = STIFFNESS_SPRING_FORCE * (KNEE_RIGHT_UP_TARGET - data.actuator_length[KNEE_RIGHT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[KNEE_RIGHT_UP]
    # Rear-Right Leg Actuator Control via PD Loops
    data.ctrl[UNION_BODY_LEG_SIDEWAYS_RIGHT_DOWN] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEG_SIDEWAYS_RIGHT_DOWN_TARGET - data.actuator_length[UNION_BODY_LEG_SIDEWAYS_RIGHT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_SIDEWAYS_RIGHT_DOWN]
    data.ctrl[UNION_BODY_LEG_FORWARD_RIGHT_DOWN] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEG_FORWARD_RIGHT_DOWN_TARGET - data.actuator_length[UNION_BODY_LEG_FORWARD_RIGHT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_FORWARD_RIGHT_DOWN]
    data.ctrl[KNEE_RIGHT_DOWN] = STIFFNESS_SPRING_FORCE * (KNEE_RIGHT_DOWN_TARGET - data.actuator_length[KNEE_RIGHT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[KNEE_RIGHT_DOWN]
    # Rear-Left Leg Actuator Control via PD Loops
    data.ctrl[UNION_BODY_LEG_SIDEWAYS_LEFT_DOWN] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEG_SIDEWAYS_LEFT_DOWN_TARGET - data.actuator_length[UNION_BODY_LEG_SIDEWAYS_LEFT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_SIDEWAYS_LEFT_DOWN]
    data.ctrl[UNION_BODY_LEG_FORWARD_LEFT_DOWN] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEG_FORWARD_LEFT_DOWN_TARGET - data.actuator_length[UNION_BODY_LEG_FORWARD_LEFT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_FORWARD_LEFT_DOWN]
    data.ctrl[KNEE_LEFT_DOWN] = STIFFNESS_SPRING_FORCE * (KNEE_LEFT_DOWN_TARGET - data.actuator_length[KNEE_LEFT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[KNEE_LEFT_DOWN]

    # Advance the simulator physics matrix by one tick frame
    mujoco.mj_step(model, data)

def handle_drive_forward(event):
    global target_speed_left, target_speed_right
    target_speed_left = FORWARD_SPEED
    target_speed_right = FORWARD_SPEED

def handle_drive_backwards(event):
    global target_speed_left, target_speed_right
    target_speed_left = FORWARD_SPEED * -0.5
    target_speed_right = FORWARD_SPEED * -0.5

def handle_turn_right(event):
    global target_speed_left, target_speed_right
    # Drop the speed of the right wheels while keeping left wheels moving forward
    target_speed_left = FORWARD_SPEED
    target_speed_right = FORWARD_SPEED * TURN_SPEED_REDUCTION

def handle_turn_left(event):
    global target_speed_left, target_speed_right
    # Drop the speed of the left wheels while keeping right wheels moving forward
    target_speed_left = FORWARD_SPEED * TURN_SPEED_REDUCTION
    target_speed_right = FORWARD_SPEED

def handle_stop_robot(event):
    global target_speed_left, target_speed_right
    target_speed_left = 0.0
    target_speed_right = 0.0

if __name__ == "__main__":
    # Run the Viser web interface via the step loop callback
    viewer = Viewer(mj_model, mj_data, step_fn=physics_callback)

    ###### ADD GUI Buttons ######
    forward_button = viewer._server.gui.add_button("Drive Forward")
    forward_button.on_click(handle_drive_forward)

    forward_button = viewer._server.gui.add_button("Drive Backwards")
    forward_button.on_click(handle_drive_backwards)

    # Spawn and hook up the Turn Left DOM button
    left_button = viewer._server.gui.add_button("Turn Left")
    left_button.on_click(handle_turn_left)

    # Spawn and hook up the Turn Right DOM button
    right_button = viewer._server.gui.add_button("Turn Right")
    right_button.on_click(handle_turn_right)

    # Spawn and hook up the Stop DOM button
    stop_button = viewer._server.gui.add_button("Stop")
    stop_button.on_click(handle_stop_robot)

    viewer.run()
