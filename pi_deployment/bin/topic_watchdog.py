#!/usr/bin/env python3
import argparse
import signal
import time
from pathlib import Path
import rclpy
from livox_ros_driver2.msg import CustomMsg
from rclpy.executors import ExternalShutdownException
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Imu

running = True
def stop(_sig, _frame):
    global running
    running = False
def read(path):
    try: return path.read_text().strip()
    except OSError: return "-1"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--heartbeat", required=True)
    ap.add_argument("--interface", default="eth0")
    args = ap.parse_args()
    signal.signal(signal.SIGINT, stop); signal.signal(signal.SIGTERM, stop)
    out = Path(args.heartbeat); out.parent.mkdir(parents=True, exist_ok=True)
    net = Path("/sys/class/net") / args.interface
    qos = QoSProfile(history=HistoryPolicy.KEEP_LAST, depth=10,
                     reliability=ReliabilityPolicy.BEST_EFFORT,
                     durability=DurabilityPolicy.VOLATILE)
    rclpy.init(); node = rclpy.create_node("carrot_topic_watchdog")
    last = {"lidar": None, "imu": None}
    node.create_subscription(CustomMsg, "/livox/lidar", lambda _: last.__setitem__("lidar", time.monotonic_ns()), qos)
    node.create_subscription(Imu, "/livox/imu", lambda _: last.__setitem__("imu", time.monotonic_ns()), qos)
    with out.open("a", buffering=1) as f:
        if out.stat().st_size == 0: f.write("epoch_ms lidar_age_ms imu_age_ms carrier rx_packets rx_bytes rx_dropped rx_errors\n")
        next_report = time.monotonic()
        while running and rclpy.ok():
            try: rclpy.spin_once(node, timeout_sec=0.1)
            except ExternalShutdownException: break
            now = time.monotonic()
            if now < next_report: continue
            now_ns = time.monotonic_ns()
            age = lambda key: -1 if last[key] is None else (now_ns - last[key]) // 1_000_000
            stat = lambda name: read(net / "statistics" / name)
            f.write(" ".join([str(time.time_ns() // 1_000_000), str(age("lidar")), str(age("imu")), read(net / "carrier"), stat("rx_packets"), stat("rx_bytes"), stat("rx_dropped"), stat("rx_errors")]) + "\n")
            next_report = max(next_report + 1.0, now + 1.0)
    node.destroy_node()
    if rclpy.ok(): rclpy.shutdown()
    return 0
if __name__ == "__main__": raise SystemExit(main())
