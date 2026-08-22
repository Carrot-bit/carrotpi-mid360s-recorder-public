# 部署问题与解决方法（脱敏版）

## 写卡

Ubuntu 启动 U 盘不能作为 Raspberry Pi 的 x86 启动盘。写卡前物理拔下无关 U 盘和外接硬盘，只保留确认过型号、容量和序列号的 SD 卡；镜像必须来自官方 ARM64 Raspberry Pi Ubuntu 22.04 发布页并校验 SHA-256。

## 无头网络

`.local` 名称发现依赖 Avahi，可能在启动较慢或网络尚未建立时暂时不可用。应使用路由器/DHCP 客户端列表或当前 DHCP 地址，不猜测地址。雷达有线网段不能与 Wi-Fi 网段重叠。

## ROS 工具包

Ubuntu 的 ROS 相关包需要启用 `universe` 并刷新 APT 索引。`ros2 --version` 不是 Humble CLI 支持的参数；用 `printenv ROS_DISTRO`、`ros2 pkg list` 和 `colcon version-check` 验证。

## ARM64 编译

Livox SDK 和 ROS 驱动必须在 Pi 上原生编译，不能复制笔记本的 x86-64 库。低内存 Pi 编译时可临时启用交换空间，并使用低并行度；编译卡住时先确认 CPU/内存/进程状态，不要立即断电。

## 外接盘保护

`findmnt --verify` 对 `ntfs-3g` 的用户态类型名可能给出静态比较警告。只要实际挂载的 UUID 正确、文件系统为 `fuseblk`/`ntfs3`、选项为 `rw` 且存储守卫通过，就不要运行 `ntfsfix`、格式化或修复命令。

## 录包

录包服务拒绝并发、错误磁盘、错误驱动、无消息、频率越界和空间不足。异常会保留原目录并写 `FAILED` 与证据，不覆盖、删除或续录已有目录。正式使用前应完成短测、稳定性测试和完整压力测试。
