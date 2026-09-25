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
DAMPING_SHOCK_ABSORBER = 5.0
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
TURN_SPEED_REDUCTION = 0.3 # Slows down inside wheels to cause a turn
# Tracking variable to pass the button state safely down into the physics clock
target_speed_left = 0.0
target_speed_right = 0.0
is_braking = False

def physics_callback(model, data):
    # # Constantly assign our button's target speed directly to all four wheels

    if is_braking:
        # Actively counter any external forces / rolling velocity by applying high inverse damping torque
        data.ctrl[FRONT_RIGHT_WHEEL] = -WHEEL_BRAKE_FORCE * data.actuator_velocity[FRONT_RIGHT_WHEEL]
        data.ctrl[REAR_RIGHT_WHEEL] = -WHEEL_BRAKE_FORCE * data.actuator_velocity[REAR_RIGHT_WHEEL]
        data.ctrl[FRONT_LEFT_WHEEL] = -WHEEL_BRAKE_FORCE * data.actuator_velocity[FRONT_LEFT_WHEEL]
        data.ctrl[REAR_LEFT_WHEEL] = -WHEEL_BRAKE_FORCE * data.actuator_velocity[REAR_LEFT_WHEEL]
    else:
        # Standard driving conditions
        data.ctrl[FRONT_RIGHT_WHEEL] = target_speed_right
        data.ctrl[REAR_RIGHT_WHEEL] = target_speed_right
        data.ctrl[FRONT_LEFT_WHEEL] = target_speed_left
        data.ctrl[REAR_LEFT_WHEEL] = target_speed_left

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

# ==============================================================================
# Attaching the Frontend Click Event Listener Function
# ==============================================================================
def handle_drive_forward(event):
    global target_speed_left, target_speed_right, is_braking
    is_braking = False
    target_speed_left = FORWARD_SPEED
    target_speed_right = FORWARD_SPEED
    print("Driving forward!")

def handle_turn_right(event):
    global target_speed_left, target_speed_right, is_braking
    is_braking = False   
    # Drop the speed of the right wheels while keeping left wheels moving forward
    target_speed_left = FORWARD_SPEED
    target_speed_right = FORWARD_SPEED * TURN_SPEED_REDUCTION
    print("Turning right forward!")

def handle_turn_left(event):
    global target_speed_left, target_speed_right, is_braking
    is_braking = False
    # Drop the speed of the left wheels while keeping right wheels moving forward
    target_speed_left = FORWARD_SPEED * TURN_SPEED_REDUCTION
    target_speed_right = FORWARD_SPEED
    print("Turning left forward!")

def handle_stop_robot(event):
    global target_speed_left, target_speed_right, is_braking
    is_braking = True
    target_speed_left = 0.0
    target_speed_right = 0.0
    print("Stopping robot movement!")

if __name__ == "__main__":
    # Run the Viser web interface via the step loop callback
    viewer = Viewer(mj_model, mj_data, step_fn=physics_callback)

    ###### ADD GUI Buttons ######
    forward_button = viewer._server.gui.add_button("Drive Forward")
    # Direct Viser to run our function every single time the DOM element is clicked
    forward_button.on_click(handle_drive_forward)
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