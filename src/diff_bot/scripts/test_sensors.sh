#!/bin/bash

source /opt/ros/humble/setup.bash
source ~/robot_description_ws/install/setup.bash

echo "    LiDAR    "
ros2 topic hz /scan

echo "    Camera    "
ros2 topic hz /camera/image

echo "    IMU    "
ros2 topic hz /imu/out