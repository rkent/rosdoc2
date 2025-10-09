# Copyright 2022 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This file is used to test documentation generation."""

# Adapted from:
# https://docs.ros.org/en/rolling/Tutorials/Beginner-Client-Libraries/
# Writing-A-Simple-Py-Publisher-And-Subscriber.html

import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
from std_msgs.msg import String

# Simple talker demo that published std_msgs/Strings messages
# to the 'chatter' topic


class MinimalSubscriber(Node):
    """Node that subscribes to a topic and prints the messages."""

    def __init__(self):
        """Create a MinimalSubscriber node."""
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            String,
            'topic',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        """Process received messages.

        :param msg: The received message
        :type msg: std_msgs.msg.String
        """
        self.get_logger().info('I heard: "%s"' % msg.data)


def main(args=None):
    """Entry point for the minimal_subscriber node."""
    try:
        with rclpy.init(args=args):
            minimal_subscriber = MinimalSubscriber()

            rclpy.spin(minimal_subscriber)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass


if __name__ == '__main__':
    main()
