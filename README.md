# 🤖 Outdoor GPS + LiDAR Autonomous Navigation Robot

<p align="center">

  <img src="https://img.shields.io/badge/ROS%202-Humble-22314E?style=for-the-badge&logo=ros" />
  <img src="https://img.shields.io/badge/Gazebo-Simulation-orange?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Nav2-Autonomous%20Navigation-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker" />
  <img src="https://img.shields.io/badge/Python-3-3776AB?style=for-the-badge&logo=python" />

</p>

<p align="center">
  <b>A ROS 2 Humble mobile robot simulation for GPS-assisted localization, LiDAR-based obstacle detection, sensor fusion and autonomous navigation.</b>
</p>

---

## 📌 Contents

- [🌍 Overview](#-overview)
- [🧠 How It Works](#-how-it-works)
- [💻 Requirements](#-requirements)
- [🚀 Installation & Setup](#-installation--setup)
- [🎮 How to Use](#-how-to-use)
- [⚠️ Limitations](#-limitations)

---

# 🌍 Overview

**Outdoor GPS + LiDAR Autonomous Navigation Robot** is a ROS 2 Humble simulation that demonstrates a complete mobile-robot navigation pipeline using:

- 📡 GPS
- 🧭 IMU
- 📏 LiDAR
- ⚙️ Wheel odometry
- 🔄 EKF sensor fusion
- 🧠 Nav2
- 🎯 RViz2
- 🎮 Keyboard teleoperation
- 🐳 Docker

The robot is simulated in **Gazebo** and visualized in **RViz2**.

> **Goal:** provide a simulation foundation for developing and testing autonomous navigation before moving toward physical hardware.

---

# 🧠 How It Works

The main system pipeline is:

```text
              ┌──────────────────────┐
              │       Gazebo         │
              │   Simulated Robot    │
              └──────────┬───────────┘
                         │
          ┌──────────────┼──────────────┬──────────────┐
          ▼              ▼              ▼              ▼
       📡 LiDAR         🧭 IMU         🌎 GPS         ⚙️ Odom
          │              │              │              │
          │              └──────┬───────┴──────────────┘             
          │                     │                      
          │                     ▼                      
          │                    EKF 
          │                     │
          │                     ▼
          │              Localization
          │                     │
          └──────────────►     Nav2
                               │
                         ┌─────┴─────┐
                         ▼           ▼
                      Planner    Controller
                         │           │
                         └─────┬─────┘
                               ▼
                           /cmd_vel
                               │
                               ▼
                          🤖 Robot
```

### 🎯 Autonomous Navigation

In RViz2:

```text
2D Goal Pose
     ↓
Select Destination
     ↓
/goal_pose
     ↓
Goal Pose Bridge
     ↓
/navigate_to_pose
     ↓
Nav2
     ↓
Plan + Avoid Obstacles + Control
     ↓
🤖 Robot Reaches Goal
```

### 🔄 Localization

`robot_localization` combines:

```text
/odom
/imu
/odometry/gps
     │
     ▼
    EKF
     │
     ▼
/odometry/filtered
```

LiDAR data is used by Nav2 costmaps for obstacle-aware navigation.

---

# 💻 Requirements

The current workflow is intended for a **Linux desktop** with graphical support.

Recommended:

```text
Linux
Docker
X11 / XWayland
```

The Docker setup uses graphical display forwarding for Gazebo, RViz2 and the teleoperation terminal.

---

# 🚀 Installation & Setup

Follow these steps for the **first-time setup**.

## 1. Install Docker

If Docker is already installed, **skip this step**.

Check:

```bash
docker --version
```

If it is not installed, install Docker using the instructions for your Linux distribution.

For example, on Arch-based systems:

```bash
sudo pacman -S docker
sudo systemctl enable --now docker
```

Verify:

```bash
docker --version
```

---

## 2. Clone the Repository

```bash
git clone https://github.com/mvjishnu/outdoor-gps-lidar-bot.git
```

Inside you will see:

```text
docker and src
```
---

## 3. Build the Docker Environment

Go to the Docker directory:

```bash
cd ~/od_gps_bot/docker
```

Make the scripts executable:

```bash
chmod +x build.sh run.sh shell.sh stop.sh
```

Build:

```bash
./build.sh
```

### ⏳ First Build

The first build may take approximately **6–8 minutes**.

> **Do not interrupt the build while the ROS 2 environment is being installed.**

---

## 4. Start the Container

Still inside:

```text
~/od_gps_bot/docker
```

run:

```bash
./run.sh
```

The main Docker container is:

```text
humble_container
```

The ROS 2 workspace inside the container is:

```text
/root/od_gps_bot
```

---

## 5. Build the ROS 2 Workspace

Once inside the container:

```bash
cd ~/od_gps_bot
```

Build:

```bash
colcon build
```

Then source:

```bash
source install/setup.bash
```

---

# 🎮 How to Use

After the initial setup, the normal workflow is very short.

## 1. Start the Container

From the host:

```bash
cd ~/od_gps_bot/docker
./run.sh
```

## 2. Build & Source

Inside the container:

```bash
cd ~/od_gps_bot
colcon build
source install/setup.bash
```

> If you have not changed the source code, rebuilding is usually unnecessary.

## 3. Launch the Simulation

```bash
ros2 launch diff_lidar_robot gazebo.launch.py
```

The launch file starts the main simulation and navigation components.

You should get:

```text
┌─────────────────────────────────────┐
│              GAZEBO                 │
│        🤖 Simulated Robot           │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│              RVIZ2                  │
│     Robot + Sensors + Navigation    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│       KEYBOARD TELEOPERATION        │
│       Manual robot control          │
└─────────────────────────────────────┘
```

---

# 🎯 Autonomous Navigation

This is the main way to use the project.

### 1. Open RViz2

Wait for the robot, sensors and navigation visualization to appear.

### 2. Select `2D Goal Pose`

In the RViz2 toolbar, choose:

```text
2D Goal Pose
```

### 3. Select the Destination

Click on the location where you want the robot to go.

### 4. Set Orientation

Hold the mouse button and drag to set the robot's desired direction.

```text
             🎯
             ↑
             │
             │
             🤖
```

### 5. Release

RViz2 sends the goal to Nav2.

Nav2 then:

```text
Receive Goal
     ↓
Plan Path
     ↓
Check Obstacles
     ↓
Control Robot
     ↓
🎯 Reach Goal
```

> **Choose the destination in RViz2 and Nav2 handles the navigation.**

---

# 🎮 Keyboard Teleoperation

A teleoperation terminal is launched automatically.

Use it to manually drive the robot.

Velocity commands are published through:

```text
/cmd_vel
```

This is useful for checking that the simulation and robot control pipeline are working.

---

# ⚠️ Limitations

This repository is currently a **simulation and navigation development platform**.

The following are simulated:

- GPS
- LiDAR
- IMU
- Wheel motion
- Robot environment

It does not currently provide:

- Physical motor control
- Real-world sensor hardware
- SLAM maps
- Physical robot deployment
- Real outdoor GPS accuracy

Therefore, successful Gazebo navigation should not be treated as proof of equivalent real-world performance.

---
