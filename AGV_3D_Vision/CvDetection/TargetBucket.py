from typing import *
import math
import time


class TargetCircle(TypedDict):
    """
    检测到的目标点
    """

    x: int
    y: int
    radius: int
    count: int
    last_check: float


class TargetBucket:
    """
    目标点平滑桶
    """

    def __init__(self, adj_tolerance=15, use_thresh=10, expire_time=0.1, max_bucket=10):
        self.bucket = []
        self.bucket: List[TargetCircle]
        self.adj_tolerance = adj_tolerance
        self.use_thresh = use_thresh
        self.expire_time = expire_time
        self.max_bucket = max_bucket

    @staticmethod
    def distance(target_a: TargetCircle, target_b: TargetCircle):
        x1, y1 = target_a["x"], target_a["y"]
        x2, y2 = target_b["x"], target_b["y"]
        return math.sqrt(math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))

    def add(self, x, y, radius):
        tmp_point = TargetCircle(
            x=x, y=y, radius=radius, count=0, last_check=time.time()
        )
        if len(self.bucket) == 0:
            self.bucket.append(tmp_point)
            return

        # if there exist adjacent point
        for t in self.bucket:
            if TargetBucket.distance(t, tmp_point) < self.adj_tolerance:
                t["x"] = int((t["x"] + tmp_point["x"]) / 2)
                t["y"] = int((t["y"] + tmp_point["y"]) / 2)
                t["radius"] = int((t["radius"] + tmp_point["radius"]) / 2)
                t["count"] += 1
                t["last_check"] = time.time()
                return

        # no adjacent point
        self.bucket.append(tmp_point)

    def add_all(self, target_list):
        for target in target_list:
            x, y, radius = target
            self.add(x, y, radius)

    def update(self):
        self.bucket = list(
            filter(
                lambda x: time.time() -
                x["last_check"] < self.expire_time, self.bucket
            )
        )
        if len(self.bucket) > self.max_bucket:
            self.bucket.sort(key=lambda x: x["count"], reverse=True)
            self.bucket = self.bucket[: self.max_bucket]

    def fetch(self):
        target_list = list(
            filter(lambda x: x["count"] >= self.use_thresh, self.bucket))
        if len(target_list) > 0:
            return target_list[0]
        else:
            return None

    def fetch_all(self):
        target_list = list(
            filter(lambda x: x["count"] >= self.use_thresh, self.bucket))
        if len(target_list) > 0:
            return target_list
        else:
            return None
