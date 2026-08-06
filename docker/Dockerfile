FROM osrf/ros:humble-desktop-jammy

RUN apt-get update && apt-get install -y --no-install-recommends \
	ros-humble-desktop-full=0.10.0-1* \
	ros-humble-navigation2 \
	ros-humble-nav2-bringup \
	xterm \
	ros-humble-tf2-tools \
 && rm -rf /var/lib/apt/lists/*
