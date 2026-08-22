#!/usr/bin/env python3
import sys

import yaml

EXPECTED = {
    "/livox/lidar": ("livox_ros_driver2/msg/CustomMsg", 8.0, 12.0),
    "/livox/imu": ("sensor_msgs/msg/Imu", 160.0, 240.0),
}


def fail(message):
    print(f"verify-bag: {message}", file=sys.stderr)
    raise SystemExit(1)


if len(sys.argv) != 2:
    fail("usage: verify_bag.py BAG_INFO_YAML")

with open(sys.argv[1], encoding="utf-8") as stream:
    document = yaml.safe_load(stream)
info = document.get("rosbag2_bagfile_information", document) if isinstance(document, dict) else None
if not isinstance(info, dict):
    fail("invalid ros2 bag info YAML")

duration_ns = info.get("duration", {}).get("nanoseconds", 0)
try:
    duration_s = int(duration_ns) / 1_000_000_000
except (TypeError, ValueError):
    fail("missing bag duration")
if duration_s <= 0:
    fail("bag has no positive duration")

topics = {}
for item in info.get("topics_with_message_count", []):
    metadata = item.get("topic_metadata", {})
    name = metadata.get("name")
    try:
        count = int(item.get("message_count", 0))
    except (TypeError, ValueError):
        count = 0
    if name:
        if name in topics:
            fail(f"duplicate topic metadata for {name}")
        topics[name] = (metadata.get("type"), count)

if set(topics) != set(EXPECTED):
    fail(f"unexpected topic set: {', '.join(sorted(topics)) or 'none'}")

for name, (expected_type, low, high) in EXPECTED.items():
    actual_type, count = topics[name]
    if actual_type != expected_type:
        fail(f"{name} type {actual_type!r} does not match {expected_type!r}")
    rate = count / duration_s
    if count <= 0:
        fail(f"{name} has no messages")
    if not low <= rate <= high:
        fail(f"{name} rate {rate:.3f} Hz is outside {low:g}..{high:g} Hz")
    print(f"{name}: count={count} rate_hz={rate:.3f}")
print(f"duration_s={duration_s:.3f}")
