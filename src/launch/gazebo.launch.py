from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import TimerAction
from launch_ros.actions import Node

from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    pkg_share = get_package_share_directory("diff_lidar_robot")

    urdf_file = os.path.join(
        pkg_share,
        "urdf",
        "diff_lidar.urdf"
    )

    world_file = os.path.join(
        pkg_share,
        "worlds",
        "empty.sdf"
    )

    rviz_config = os.path.join(
        pkg_share,
        "worlds",
        "diff_lidar_config.rviz"
    )

    nav2_params = os.path.join(
        pkg_share,
        "config",
        "nav2_params.yaml",
    )

    with open(urdf_file, "r") as infp:
        robot_description = infp.read()

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("ros_gz_sim"),
                "launch",
                "gz_sim.launch.py"
            )
        ),
        launch_arguments={
            "gz_args": "-r -v 4 " + world_file
        }.items(),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=[
            "-d",
            rviz_config,
        ],
        output="screen",
        parameters=[
            {"use_sim_time": True}
        ],
    )

    teleop_keyboard = Node(
        package="teleop_twist_keyboard",
        executable="teleop_twist_keyboard",
        name="teleop_twist_keyboard",
        prefix="xterm -e",
        output="screen",
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": robot_description,
                "use_sim_time": True,
            }
        ],
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        parameters=[
            {"use_sim_time": True}
        ],
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-file",
            urdf_file,
            "-name",
            "diff_lidar",
        ],
        output="screen",
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments = [
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry@gz.msgs.Odometry",
            "/scan/points@sensor_msgs/msg/PointCloud2@gz.msgs.PointCloudPacked",
            "/camera/image@sensor_msgs/msg/Image@gz.msgs.Image",
            "/imu@sensor_msgs/msg/Imu@gz.msgs.IMU",
            "/gps@sensor_msgs/msg/NavSatFix@gz.msgs.NavSat",
        ],
        output="screen",
    )

    ekf_node = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[
            os.path.join(pkg_share, "config", "ekf.yaml")
        ],
    )

    navsat_transform = Node(
        package="robot_localization",
        executable="navsat_transform_node",
        name="navsat_transform",
        output="screen",
        parameters=[
            os.path.join(
                pkg_share,
                "config",
                "navsat.yaml",
            )
        ],
        remappings=[
            ("imu", "/imu"),
            ("gps/fix", "/gps"),
            ("odometry/filtered", "/odometry/filtered"),
        ],
    )

    controller_server = Node(
        package="nav2_controller",
        executable="controller_server",
        name="controller_server",
        output="screen",
        parameters=[nav2_params],
    )

    planner_server = Node(
        package="nav2_planner",
        executable="planner_server",
        name="planner_server",
        output="screen",
        parameters=[nav2_params],
    )

    behavior_server = Node(
        package="nav2_behaviors",
        executable="behavior_server",
        name="behavior_server",
        output="screen",
        parameters=[nav2_params],
    )

    bt_navigator = Node(
        package="nav2_bt_navigator",
        executable="bt_navigator",
        name="bt_navigator",
        output="screen",
        parameters=[nav2_params],
    )

    waypoint_follower = Node(
        package="nav2_waypoint_follower",
        executable="waypoint_follower",
        name="waypoint_follower",
        output="screen",
        parameters=[nav2_params],
    )

    lifecycle_manager = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        name="lifecycle_manager",
        output="screen",
        parameters=[nav2_params],
    )

    goal_pose_bridge = Node(
        package="diff_lidar_robot",
        executable="goal_pose_bridge",
        output="screen",
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        joint_state_publisher,
        TimerAction(
            period=3.0,
            actions=[
                spawn_robot,
            ],
        ),
        bridge,
        ekf_node,
        TimerAction(
            period=2.0,
            actions=[
                navsat_transform,
            ],
        ),
        TimerAction(
            period=6.0,
            actions=[
                planner_server,
                controller_server,
                behavior_server,
                bt_navigator,
                waypoint_follower,
                lifecycle_manager,
            ],
        ),
        goal_pose_bridge,
        rviz,
        teleop_keyboard,
    ])