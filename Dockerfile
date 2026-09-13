# ==============================================================================
# BASE STAGE: Official Open Source Robotics Foundation Ubuntu Image
# ==============================================================================
FROM ros:humble-ros-base-jammy AS base

# Prevent interactive prompts during installation steps
ENV DEBIAN_FRONTEND=noninteractive

# Set system environment variables for optimal headless operation
ENV PYTHONUNBUFFERED=1
ENV ROS_DOMAIN_ID=42

# Install minimal OS dependencies for Python development, OpenCV, and PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Establish the runtime workspace directories inside the Ubuntu file layout
WORKDIR /ros2

# ==============================================================================
# DEPENDENCIES STAGE: Python packages isolation
# ==============================================================================
COPY . /ros2

# Install dependencies directly using pip (OpenCV headless saves CPU/RAM)
RUN pip3 install -e /ros2/third_party/unitree_sdk2_python
RUN pip3 install --no-cache-dir -r /ros2/requirements.txt

# ==============================================================================
# DEVELOPMENT STAGE: Setup local workspace configuration
# ==============================================================================
FROM base AS development

WORKDIR /

# Build into c++ every robotics Python script
RUN bash -c ". /opt/ros/humble/setup.bash && cd ros2/ && colcon build --packages-ignore unitree_mujoco"

# Auto-source the ROS2 environment variables inside the terminal profile
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "source /ros2/install/setup.bash" >> ~/.bashrc

# Default execution entrypoint sets up the runtime context shell
CMD ["/bin/bash"]