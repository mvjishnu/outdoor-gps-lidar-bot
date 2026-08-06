#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


class GoalPoseBridge(Node):

    def __init__(self):
        super().__init__("goal_pose_bridge")

        self.client = ActionClient(
            self,
            NavigateToPose,
            "/navigate_to_pose"
        )

        self.subscription = self.create_subscription(
            PoseStamped,
            "/goal_pose",
            self.goal_callback,
            10
        )

        self.get_logger().info("Waiting for /goal_pose...")

    def goal_callback(self, msg):

        goal = NavigateToPose.Goal()
        goal.pose = msg

        self.client.wait_for_server()

        self.client.send_goal_async(goal)

        self.get_logger().info("Goal sent to BT Navigator")


def main(args=None):

    rclpy.init(args=args)

    node = GoalPoseBridge()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()