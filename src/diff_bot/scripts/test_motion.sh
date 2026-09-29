#!/bin/bash

source /opt/ros/humble/setup.bash
source ~/mobile_ws/install/setup.bash

TOPIC=/diff_controller/cmd_vel_unstamped

echo "Forward..."
timeout 5 ros2 topic pub -r 10 $TOPIC geometry_msgs/msg/Twist \
"{linear: {x: 0.05}, angular: {z: 0.0}}"

echo "Stop..."
ros2 topic pub --once $TOPIC geometry_msgs/msg/Twist \
"{linear: {x: 0.0}, angular: {z: 0.0}}"

sleep 1

echo "Rotate..."
timeout 5 ros2 topic pub -r 10 $TOPIC geometry_msgs/msg/Twist \
"{linear: {x: 0.0}, angular: {z: 0.5}}"

echo "Stop..."
ros2 topic pub --once $TOPIC geometry_msgs/msg/Twist \
"{linear: {x: 0.0}, angular: {z: 0.0}}"