FROM osrf/ros:humble-desktop-jammy

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-desktop-full=0.10.0-1* \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-robot-localization \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-tf2-tools \
    ros-humble-ros-gz \
    xterm \
    nano \
 && rm -rf /var/lib/apt/lists/*

RUN echo "" >> /root/.bashrc && \
    echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo '[ -f /root/od_gps_bot/install/setup.bash ] && source /root/od_gps_bot/install/setup.bash' >> /root/.bashrc
