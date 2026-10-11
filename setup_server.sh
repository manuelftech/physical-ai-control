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
export MUJOCO_GL="egl"
export __NV_PRIME_RENDER_OFFLOAD=1
export __GLX_VENDOR_LIBRARY_NAME=nvidia

# Nvidia Config for MuJoCo
export TORCH_CUDNN_V8_API_ENABLED=0
export USE_CUDNN=0
export TORCH_CUDA_ARCH_LIST="Ampere"
