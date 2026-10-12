# Install dependencies
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
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
    && sudo rm -rf /var/lib/apt/lists/*

# Install Pangolin
git clone https://github.com/stevenlovegrove/Pangolin.git && cd Pangolin && git checkout master && \
    mkdir build && cd build && cmake .. -DHEADLESS=ON && \
    make -j$(nproc) && sudo make install && \
    sudo ldconfig

# Install ORB-SLAM3
git clone https://github.com/zang09/ORB-SLAM3-STEREO-FIXED.git ORB_SLAM3 && cd ORB_SLAM3/Vocabulary && \
    tar -xf ORBvoc.txt.tar.gz && cd .. && chmod +x build.sh && \
    ./build.sh \ 
    ls -lh ~/ORB_SLAM3/lib/libORB_SLAM3.so

# MuJoCo configuration
# 1. Force MuJoCo to render headless frames straight to VRAM using EGL
echo "export MUJOCO_GL='egl'" >> ~/.bashrc

# 2. Force the driver layers to route calls through your NVIDIA hardware
echo "export __NV_PRIME_RENDER_OFFLOAD=1" >> ~/.bashrc
echo "export __GLX_VENDOR_LIBRARY_NAME=nvidia" >> ~/.bashrc

# 3. Reload your profile instantly
source ~/.bashrc

sudo apt update && sudo apt upgrade -y
sudo apt install -y ubuntu-desktop gdm3
sudo apt update && sudo apt install epiphany-browser -y

sudo apt update && sudo apt install ros-$ROS_DISTRO-cv-bridge ros-$ROS_DISTRO-sensor-msgs ros-$ROS_DISTRO-image-transport
