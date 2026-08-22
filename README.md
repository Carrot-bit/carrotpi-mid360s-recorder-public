# Raspberry Pi Mid-360S ROS 2 Bag Recorder

这是一个完全脱敏的 Raspberry Pi 4B + Ubuntu Server 22.04 ARM64 + ROS 2 Humble 录包模板。
树莓派只运行 Livox 驱动和 `rosbag2`，不运行 FAST-LIO、RViz 或压缩算法。

## 功能

- 外接 NTFS 磁盘保护：按 UUID、挂载状态、读写能力和剩余空间拒绝错误录制；不回退写 SD 卡。
- 受管 Livox 驱动生命周期：录包时自动启动，停止录包后保持运行。
- `systemd --user` 录包服务，SSH 断开不会中断录制。
- LiDAR/IMU 话题类型、实时频率、磁盘、温度、电源和网卡健康检查。
- 单个 SQLite3 bag、完成/失败标记、相对 SHA-256 清单和诊断证据。
- 家用 Wi-Fi、手机热点和雷达有线链路的网络模板。

## 使用前必须配置

公开版本故意没有任何真实 IP、磁盘 UUID、源码哈希、用户名或网络密码。部署前必须填写：

1. `pi_deployment/netplan/*.yaml` 中的 SSID、密码和雷达网段；
2. `pi_deployment/bin/carrot-storage-guard` 的磁盘 UUID；
3. `pi_deployment/bin/carrot-livox-verify` 的源码清单、配置和启动文件哈希；
4. `pi_deployment/bin/carrot-bag`、`carrot-driver-launch` 和 `install.sh` 中的 Pi 用户及工作空间路径；
5. 与你的 Mid-360S 配置匹配的 Livox 源码、配置文件和 ARM64 SDK。

不要把真实 Wi-Fi 密码、SSH 私钥或访问令牌提交到 Git。

## 常用命令

```bash
carrot-bag start experiment01     # 默认 60 分钟
carrot-bag watch experiment01    # 可选监控
carrot-bag status
carrot-bag stop
carrot-bag logs experiment01
carrot-bag driver-stop
carrot-net status
```

输出目录格式为：

```text
/mnt/carrot_disk/carrot_rosbags/<label>_<timestamp>/
```

完整部署说明见 [`树莓派录包部署环境.md`](树莓派录包部署环境.md)。问题排查和验收建议见 `docs/`。

## 镜像

不要把 SD 卡原始镜像或 bag 文件提交到 Git 历史。建议在 GitHub Release、对象存储或实验室备份中保存镜像，并在发布说明中记录来源、制作日期、压缩格式和 SHA-256。
