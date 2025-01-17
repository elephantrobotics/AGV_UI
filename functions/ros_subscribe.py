#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import queue
import threading
import typing as T
import rospy
from actionlib_msgs.msg import GoalStatusArray, GoalStatus

from PyQt5.QtCore import QThread, pyqtSignal

"""
GoalStatus
PENDING: 目标已被接受，但尚未开始执行。
ACTIVE: 目标正在执行中。
PREEMPTED: 目标已被抢占。
SUCCEEDED: 目标执行成功。
ABORTED: 目标执行失败。
REJECTED: 目标被拒绝。
LOST: 目标状态丢失
"""


class MoveBaseStatusSubscriber(QThread):
    """docstring for MoveBaseStatusSubscriber"""
    goal_status_changed = pyqtSignal(int, GoalStatus)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        rospy.init_node('move_base', anonymous=True)
        self._subscriber = rospy.Subscriber("/move_base/status", GoalStatusArray, self.on_ros_topic_callback)
        self._rate = rospy.Rate(1)
        self._queue = queue.Queue()
        self._listening = False
        self._move_status_table: T.Dict[str, list] = {}

    def on_ros_topic_callback(self, data):
        if len(data.status_list) < 0:
            return

        for status in data.status_list:

            if status.goal_id.id not in self._move_status_table:
                self._move_status_table[status.goal_id.id] = []

            accept_status_list = self._move_status_table.get(status.goal_id.id, [])
            if status.status in accept_status_list:
                continue

            self._move_status_table[status.goal_id.id].append(status.status)
            print(f"@StatusCODE => {status.status} @GoalID => {status.goal_id.id} ThreadID=> {threading.get_ident()}")
            # self._queue.put(status)
            self.goal_status_changed.emit(len(self._move_status_table.keys()), status)

    def unregister(self):
        self._listening = False
        self._subscriber.unregister()

    def run(self):
        print(f"LOOP ThreadID=> {threading.get_ident()}")
        self._listening = True
        while not rospy.is_shutdown() and self._listening:
            self._rate.sleep()
