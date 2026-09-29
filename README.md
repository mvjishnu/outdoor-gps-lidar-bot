# 🤖 Outdoor GPS + LiDAR Autonomous Navigation Robot

<p align="center">

  <img src="https://img.shields.io/badge/ROS%202-Humble-22314E?style=for-the-badge&logo=ros" alt="ROS 2 Humble"/>
  <img src="https://img.shields.io/badge/Gazebo-Simulation-orange?style=for-the-badge" alt="Gazebo"/>
  <img src="https://img.shields.io/badge/Nav2-Autonomous%20Navigation-blue?style=for-the-badge" alt="Nav2"/>
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker" alt="Docker"/>
  <img src="https://img.shields.io/badge/Python-3-3776AB?style=for-the-badge&logo=python" alt="Python"/>

</p>

<p align="center">
  <b>A ROS 2 Humble simulation platform for autonomous robot navigation using LiDAR, GPS, IMU, sensor fusion and Nav2.</b>
</p>

---

## ✨ Overview

**Outdoor GPS + LiDAR Autonomous Navigation Robot** is a ROS 2 based mobile-robot simulation designed to explore autonomous navigation using multiple sources of localization and perception.

The robot is simulated in **Gazebo** and visualized through **RViz2**. It combines:

- 📡 GPS-based positioning
- 🧭 IMU orientation data
- 📏 LiDAR-based obstacle detection
- 🔄 Wheel odometry
- 🧮 EKF sensor fusion
- 🗺️ Nav2 path planning and control
- 🎯 RViz 2D Goal Pose navigation
- 🎮 Keyboard teleoperation
- 🌉 ROS 2 ↔ Gazebo communication through `ros_gz_bridge`
- 🐳 Docker-based development environment

The project is designed as a **foundation for experimenting with autonomous mobile robots**, particularly robots that may eventually operate in outdoor environments.

---

# 🎯 What Does This Project Do?

At a high level, the system follows this pipeline:

```text
                    ┌──────────────────┐
                    │     Gazebo       │
                    │    Simulation    │
                    └────────┬─────────┘
                             │
             ┌───────────────┼────────────────┐
             │               │                │
             ▼               ▼                ▼
          📡 GPS           🧭 IMU          📏 LiDAR
             │               │                │
             └───────────────┼────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ Robot Localiz.  │
                    │      EKF        │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Localization  │
                    │   /odometry     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │      Nav2       │
                    │ Planner + Ctrl. │
                    └────────┬────────┘
                             │
                             ▼
                       🎯 Goal Pose
                             │
                             ▼
                    ┌─────────────────┐
                    │     /cmd_vel    │
                    └────────┬────────┘
                             │
                             ▼
                       🤖 Mobile Robot
