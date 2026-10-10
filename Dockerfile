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
    git \
    cmake \
    build-essential \
    libglew-dev \
    libgtk-3-dev \
    libboost-all-dev \
    libx11-dev \
    libxmu-dev \
    libxi-dev \
    libsqlite3-dev \
    libopencv-dev \
    libeigen3-dev \
    libgoogle-glog-dev \
    libatlas-base-dev \
    libsuitesparse-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Pangolin
RUN git clone https://github.com/stevenlovegrove/Pangolin.git && cd Pangolin && git checkout v0.6 && \
    sed -i '1s/^/#include <limits>\n#include <cstdint>\n/' include/pangolin/gl/colour.h && \
    mkdir build && cd build && cmake .. -DHEADLESS=ON && make -j$(nproc) && make install && \
    ldconfig

# Install ORB-SLAM3
RUN git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git ORB_SLAM3 && cd ORB_SLAM3 && \
    # Force C++14 to resolve std::is_monotonic removal issues
    sed -i 's/set(CMAKE_CXX_STANDARD 11)/set(CMAKE_CXX_STANDARD 14)/g' CMakeLists.txt && \
    # Fix a minor structural bug inside LocalMapping.cc for Ubuntu 22.04 compilers
    sed -i 's/x3D = x3D_h.get_minor<3,1>(0,0) (1 \/ x3D_h(3));/x3D = x3D_h.get_minor<3,1>(0,0) * (1 \/ x3D_h(3));/g' src/LocalMapping.cc && \
    cd Vocabulary && tar -xf ORBvoc.txt.tar.gz && cd .. && chmod +x build.sh && \
    ./build.sh

# Environment configuration for ORB-SLAM3
ENV ORB_SLAM3_ROOT_DIR=/thirdparty/ORB_SLAM3
# Establish the runtime workspace directories inside the Ubuntu file layout
WORKDIR /ros2

# ==============================================================================
# DEPENDENCIES STAGE: Python packages isolation
# ==============================================================================
COPY . /ros2

# Install dependencies directly using pip (OpenCV headless saves CPU/RAM)
#RUN pip3 install -e /ros2/third_party/unitree_sdk2_python
RUN pip3 install --no-cache-dir -r /ros2/requirements.txt

FROM base AS development

WORKDIR /

# Build into c++ every robotics Python script
#RUN bash -c ". /opt/ros/humble/setup.bash && cd ros2/ && colcon build --packages-ignore unitree_mujoco"

# Auto-source the ROS2 environment variables inside the terminal profile
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "source /ros2/install/setup.bash" >> ~/.bashrc

# Default execution entrypoint runs the simulation and controller together
#CMD ["/bin/bash", "-c", "source /opt/ros/humble/setup.bash && source /ros2/install/setup.bash && cd /ros2/third_party/unitree_mujoco/simulate_python && python3 unitree_mujoco.py"]
CMD ["/bin/bash"]