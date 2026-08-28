
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
docker build . -t ros2-robotics

# Run the local ros2-robotics docker container
docker run -it \
  --network ros2-robotics-network \
  -v "$(pwd)/src:/ros2_ws/src" \
  -e DB_HOST=postgres-ros2-robotics \
  -e DB_NAME=robotics-internal-db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=123456 \
  ros2-robotics:latest
