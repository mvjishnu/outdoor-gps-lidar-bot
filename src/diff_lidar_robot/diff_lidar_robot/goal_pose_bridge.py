#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from action_msgs.msg import GoalStatus


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

        if not msg.header.frame_id:
            self.get_logger().error(
                "Ignoring goal with an empty frame_id; set the RViz Fixed Frame "
                "to odom or another frame connected to odom."
            )
            return

        if not self.client.wait_for_server(timeout_sec=2.0):
            self.get_logger().error(
                "Nav2 /navigate_to_pose action server is unavailable; goal was not sent."
            )
            return

        goal = NavigateToPose.Goal()
        goal.pose = msg

        future = self.client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)
        self.get_logger().info(
            f"Sending goal in frame '{msg.header.frame_id}' at "
            f"({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})."
        )

    def goal_response_callback(self, future):
        try:
            goal_handle = future.result()
        except Exception as exc:  # Report action transport failures in the ROS log.
            self.get_logger().error(f"Could not send navigation goal: {exc}")
            return

        if not goal_handle.accepted:
            self.get_logger().error("Nav2 rejected the navigation goal.")
            return

        self.get_logger().info("Nav2 accepted the goal; planning and navigation started.")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        try:
            result = future.result()
        except Exception as exc:
            self.get_logger().error(f"Navigation action failed: {exc}")
            return

        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Navigation goal succeeded.")
        elif result.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().warning("Navigation goal was canceled.")
        else:
            self.get_logger().error(
                f"Navigation goal ended with action status {result.status}; "
                "check Nav2 planner/controller logs for the failure reason."
            )


def main(args=None):

    rclpy.init(args=args)

    node = GoalPoseBridge()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
