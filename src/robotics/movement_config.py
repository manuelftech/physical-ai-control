import mujoco
import structlog
logger = structlog.get_logger()

# Actuator IDs
WHEEL_ACTUATORS = [12, 13, 14, 15]

# Control Settings
STIFFNESS_SPRING_FORCE = 100.0
DAMPING_SHOCK_ABSORBER = 1.0
WHEEL_BRAKE_FORCE = 50.0
UNION_BODY_LEGS_SIDEWAYS_TARGET = 0.0
UNION_BODY_LEGS_FORWARD_TARGET = 0.67
KNEES_TARGET = -1.3

# LEG: LEFT-UP
UNION_BODY_LEG_SIDEWAYS_LEFT_UP = 3
UNION_BODY_LEG_FORWARD_LEFT_UP = 4
KNEE_LEFT_UP = 5

# LEG: RIGHT-UP
UNION_BODY_LEG_SIDEWAYS_RIGHT_UP = 0
UNION_BODY_LEG_FORWARD_RIGHT_UP = 1
KNEE_RIGHT_UP = 2

# LEG: RIGHT-DOWN
UNION_BODY_LEG_SIDEWAYS_RIGHT_DOWN = 6
UNION_BODY_LEG_FORWARD_RIGHT_DOWN = 7
KNEE_RIGHT_DOWN = 8

# LEG: LEFT-DOWN
UNION_BODY_LEG_SIDEWAYS_LEFT_DOWN = 9
UNION_BODY_LEG_FORWARD_LEFT_DOWN = 10
KNEE_LEFT_DOWN = 11

# GUI BUTTON: MOVE-FORWARD
FORWARD_SPEED = 2.5

# GUI BUTTON: MOVE-LEFT
FRONT_RIGHT_WHEEL = 12
FRONT_LEFT_WHEEL = 13
REAR_RIGHT_WHEEL = 14
REAR_LEFT_WHEEL = 15
TURNING_STRENTH = 0.01
target_speed_left = 0.0
target_speed_right = 0.0

def stabilize_robot(model, data):
    # Apply independent side speeds to make steering possible
    data.ctrl[FRONT_RIGHT_WHEEL] = target_speed_right
    data.ctrl[REAR_RIGHT_WHEEL] = target_speed_right
    data.ctrl[FRONT_LEFT_WHEEL] = target_speed_left
    data.ctrl[REAR_LEFT_WHEEL] = target_speed_left
    # Front-Left Leg Actuator Control via PD Loops
    data.ctrl[UNION_BODY_LEG_SIDEWAYS_LEFT_UP] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEGS_SIDEWAYS_TARGET - data.actuator_length[UNION_BODY_LEG_SIDEWAYS_LEFT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_SIDEWAYS_LEFT_UP]
    data.ctrl[UNION_BODY_LEG_FORWARD_LEFT_UP] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEGS_FORWARD_TARGET - data.actuator_length[UNION_BODY_LEG_FORWARD_LEFT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_FORWARD_LEFT_UP]
    data.ctrl[KNEE_LEFT_UP] = STIFFNESS_SPRING_FORCE * (KNEES_TARGET - data.actuator_length[KNEE_LEFT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[KNEE_LEFT_UP]
    # Front-Right Leg Actuator Control via PD Loops
    data.ctrl[UNION_BODY_LEG_SIDEWAYS_RIGHT_UP] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEGS_SIDEWAYS_TARGET - data.actuator_length[UNION_BODY_LEG_SIDEWAYS_RIGHT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_SIDEWAYS_RIGHT_UP]
    data.ctrl[UNION_BODY_LEG_FORWARD_RIGHT_UP] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEGS_FORWARD_TARGET - data.actuator_length[UNION_BODY_LEG_FORWARD_RIGHT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_FORWARD_RIGHT_UP]
    data.ctrl[KNEE_RIGHT_UP] = STIFFNESS_SPRING_FORCE * (KNEES_TARGET - data.actuator_length[KNEE_RIGHT_UP]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[KNEE_RIGHT_UP]
    # Rear-Right Leg Actuator Control via PD Loops
    data.ctrl[UNION_BODY_LEG_SIDEWAYS_RIGHT_DOWN] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEGS_SIDEWAYS_TARGET - data.actuator_length[UNION_BODY_LEG_SIDEWAYS_RIGHT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_SIDEWAYS_RIGHT_DOWN]
    data.ctrl[UNION_BODY_LEG_FORWARD_RIGHT_DOWN] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEGS_FORWARD_TARGET - data.actuator_length[UNION_BODY_LEG_FORWARD_RIGHT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_FORWARD_RIGHT_DOWN]
    data.ctrl[KNEE_RIGHT_DOWN] = STIFFNESS_SPRING_FORCE * (KNEES_TARGET - data.actuator_length[KNEE_RIGHT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[KNEE_RIGHT_DOWN]
    # Rear-Left Leg Actuator Control via PD Loops
    data.ctrl[UNION_BODY_LEG_SIDEWAYS_LEFT_DOWN] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEGS_SIDEWAYS_TARGET - data.actuator_length[UNION_BODY_LEG_SIDEWAYS_LEFT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_SIDEWAYS_LEFT_DOWN]
    data.ctrl[UNION_BODY_LEG_FORWARD_LEFT_DOWN] = STIFFNESS_SPRING_FORCE * (UNION_BODY_LEGS_FORWARD_TARGET - data.actuator_length[UNION_BODY_LEG_FORWARD_LEFT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[UNION_BODY_LEG_FORWARD_LEFT_DOWN]
    data.ctrl[KNEE_LEFT_DOWN] = STIFFNESS_SPRING_FORCE * (KNEES_TARGET - data.actuator_length[KNEE_LEFT_DOWN]) - DAMPING_SHOCK_ABSORBER * data.actuator_velocity[KNEE_LEFT_DOWN]

    # Advance the simulator physics matrix by one tick frame
    mujoco.mj_step(model, data)

def move_forward(event):
    global target_speed_left, target_speed_right
    target_speed_left = FORWARD_SPEED - 1
    target_speed_right = FORWARD_SPEED - 1
    logger.info("Moving forward")

def move_backwards(event):
    global target_speed_left, target_speed_right
    target_speed_left = FORWARD_SPEED * -0.5
    target_speed_right = FORWARD_SPEED * -0.5
    logger.info("Moving backwards")

def move_right_up(event):
    global target_speed_left, target_speed_right
    target_speed_left = FORWARD_SPEED + 0.4
    target_speed_right = FORWARD_SPEED * TURNING_STRENTH
    logger.info("Moving right up")

def move_right_down(event):
    global target_speed_left, target_speed_right
    target_speed_left = (FORWARD_SPEED * -1) - 0.4
    target_speed_right = FORWARD_SPEED * TURNING_STRENTH
    logger.info("Moving right down")

def move_left_up(event):
    global target_speed_left, target_speed_right
    target_speed_left = FORWARD_SPEED * TURNING_STRENTH
    target_speed_right = FORWARD_SPEED + 0.4
    logger.info("Moving left up")

def move_left_down(event):
    global target_speed_left, target_speed_right
    target_speed_left = FORWARD_SPEED * TURNING_STRENTH
    target_speed_right = (FORWARD_SPEED * -1) - 0.4
    logger.info("Moving left down")

def stop_movement(event):
    global target_speed_left, target_speed_right
    target_speed_left = 0.0
    target_speed_right = 0.0
    logger.info("Stopping movement")