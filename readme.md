# Important Instructions To Read !!! 

## How To Start Up The Arm
1) Open the gripper to the full extent 
2) Power on the arm 
3) Run reset.py to calibrate the arm 

# Visionc_

# Packages and their functions
## Paramiko 
Paramiko package is used to establish SSH connections to remote devices. In this case, the robotic arm. 
## Pymycobot (3.6.1 DO NOT UPDATE)
Pymycobot is designed to control MyCobot robotic arms developed by Elephant Robotics. It controls the movement of joints and grippers. 
## ikpy 
ikpy is used to implement inverse kinematics and compute all joint angles at once.
## pyrealsense2 
pyrealsense2 is used to interact with D435i 3D camera through python scripts.
## ultralytics
ultratyics is used to access YOLO (you only look once) models. 
## cv2
cv2 is used to control the camera.

## COPY N PASTE 
cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
      -D ENABLE_NEON=ON \
      -D WITH_CUDA=ON \
      -D WITH_CUDNN=ON \
      -D CUDA_ARCH_BIN=5.3 \
      -D OPENCV_DNN_CUDA=ON \
      -D WITH_GSTREAMER=ON \
      -D WITH_LIBV4L=ON \
      -D BUILD_opencv_python3=ON \
      -D BUILD_opencv_python2=OFF \
      -D BUILD_TESTS=OFF \
      -D BUILD_PERF_TESTS=OFF \
      -D BUILD_EXAMPLES=OFF ..
    