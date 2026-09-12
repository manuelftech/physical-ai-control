
## Build up

# set up the Docker network shared by all containers
docker network create robotics-network

# Set up PostgreSQL locally
docker run -d \
  --name postgres-ros2-robotics \
  --network robotics-network \
  -e POSTGRES_DB=robotics-internal-db \
  -e POSTGRES_PASSWORD=123456 \
  -p 5432:5432 \
  -v db_data:/var/lib/postgresql/data \
  postgres:15-alpine

# Set up the local Docker image
docker build . -t physical-ai-control

# Run the local ros2-robotics docker container
docker run -it \
  --network host \
  -v "$(pwd)/src:/ros2_ws/src" \
  -e DB_HOST=localhost \
  -e DB_NAME=robotics-internal-db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=123456 \
  physical-ai-control:latest

# Inside the running container setp up the ROS2 skeleton
cd src

# Create the skeleton package for the quadruped inspector node (go2_auditor):
ros2 pkg create --build-type ament_python unitre-go2 --dependencies rclpy std_msgs sensor_msgs

# Create the skeleton package for the humanoid handler node (g1_handler):
ros2 pkg create --build-type ament_python unitree-g1-hands --dependencies rclpy std_msgs

## Build the scripts
python -m colcon build

## Execution

# Command to initialize Mujoco with the robot

mjpython /Users/$(whoami)/unitree_mujoco/simulate_python/unitree_mujoco.py

