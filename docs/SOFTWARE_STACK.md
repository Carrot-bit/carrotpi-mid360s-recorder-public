# Verified software stack

The recorder target is a Raspberry Pi 4 Model B running a 64-bit ARM server
system.

| Component | Required baseline | Official source |
|---|---|---|
| Board | Raspberry Pi 4 Model B | <https://www.raspberrypi.com/products/raspberry-pi-4-model-b/> |
| Operating system | Ubuntu Server 22.04.5 LTS, ARM64 (`aarch64`) | <https://cdimage.ubuntu.com/releases/jammy/release/> |
| ROS 2 | Humble Hawksbill on Ubuntu 22.04 | <https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html> |
| Livox SDK | Livox-SDK2, ARM64 native build | <https://github.com/Livox-SDK/Livox-SDK2> |
| ROS driver | `livox_ros_driver2` 1.2.5, ARM64 native build | <https://github.com/Livox-SDK/livox_ros_driver2> |
| Bag storage | `rosbag2` SQLite3, one file per session | <https://github.com/ros2/rosbag2> |

## Install the operating system

The official preinstalled Raspberry Pi image can be downloaded and verified as
follows. Replace the output filename if a newer 22.04 ARM64 Pi image is used.

```bash
curl -LO https://cdimage.ubuntu.com/releases/jammy/release/ubuntu-22.04.5-preinstalled-server-arm64+raspi.img.xz
curl -LO https://cdimage.ubuntu.com/releases/jammy/release/SHA256SUMS
grep 'ubuntu-22.04.5-preinstalled-server-arm64+raspi.img.xz' SHA256SUMS | sha256sum -c -
```

Write the verified image to the confirmed SD whole-disk device. Device names are
system-dependent; identify the device with `lsblk` before writing.

```bash
unxz ubuntu-22.04.5-preinstalled-server-arm64+raspi.img.xz
sudo dd if=ubuntu-22.04.5-preinstalled-server-arm64+raspi.img \
  of=/dev/<confirmed-sd-device> bs=4M status=progress conv=fsync
sync
```

## Install ROS 2 and build tools

Follow the official ROS 2 Humble deb instructions, then install the recorder
dependencies:

```bash
sudo apt update
sudo apt install -y \
  ros-humble-ros-base ros-humble-rosbag2 \
  ros-humble-rosbag2-storage-default-plugins ros-humble-rclpy \
  ros-humble-sensor-msgs python3-colcon-common-extensions \
  python3-rosdep build-essential cmake git pkg-config
source /opt/ros/humble/setup.bash
printenv ROS_DISTRO
uname -m
```

Expected values are `humble` and `aarch64`.

## Build Livox components on the Pi

Clone the SDK and driver sources on the Pi and build them locally. The source
revision and measured file manifest used by a particular deployment belong in
that deployment's private records.

```bash
git clone https://github.com/Livox-SDK/Livox-SDK2.git
cd Livox-SDK2
# Pin a reviewed commit before building.
git checkout <reviewed-sdk2-commit>
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j2
sudo cmake --install build
sudo ldconfig

mkdir -p ~/carrot_ws/src
git clone https://github.com/Livox-SDK/livox_ros_driver2.git \
  ~/carrot_ws/src/livox_ros_driver2
cd ~/carrot_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install --event-handlers console_direct+ \
  --cmake-args -DHUMBLE_ROS=humble -DCMAKE_BUILD_TYPE=Release
source install/setup.bash
```

The Mid-360S launch configuration must publish:

```text
/livox/lidar  livox_ros_driver2/msg/CustomMsg  8–12 Hz
/livox/imu    sensor_msgs/msg/Imu                 160–240 Hz
```
