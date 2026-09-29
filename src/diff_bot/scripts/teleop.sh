#!/bin/bash

source /opt/ros/humble/setup.bash
source ~/robot_description_ws/install/setup.bash

ros2 run key_teleop key_teleop \
  --ros-args \
  -r /key_vel:=/diff_controller/cmd_vel_unstamped