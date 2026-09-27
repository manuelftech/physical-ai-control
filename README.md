## Building steps using Docker:

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
  -p 8080:8080 \
  --network host \
  -v "$(pwd)/src:/ros2/src" \
  -e DB_HOST=postgres-db \
  -e DB_NAME=robotics-internal-db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=123456 \
  physical-ai-control:latest

# ROS2 Execution inside the Docker Container

ros2 run unitree_go2w test_movement

# Yolo Version

YOLO26n (Nano)

@misc{downs2022scannedobjects,
    url = {https://arxiv.org/abs/2204.11918},
    author = {Downs, Laura and Francis, Anthony and Koenig, Nate and Kinman, Brandon and Hickman, Ryan and Reymann, Krista and McHugh, Thomas B. and Vanhoucke, Vincent},
    keywords = {Robotics (cs.RO), Graphics (cs.GR), FOS: Computer and information sciences, FOS: Computer and information sciences},
    title = {Google Scanned Objects: A High-Quality Dataset of 3D Scanned Household Items},
    publisher = {arXiv},
    year = {2022},
}