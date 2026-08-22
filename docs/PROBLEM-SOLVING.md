# Deployment troubleshooting

## Writing the SD card

The Raspberry Pi requires a 64-bit ARM image. A normal x86/amd64 Ubuntu USB
drive boots a laptop and is not a Raspberry Pi boot medium. Before writing,
disconnect unrelated USB storage and identify the target SD whole-disk device
by model, serial and capacity. Verify the official image checksum before
writing it.

## Headless networking

`.local` discovery is provided by Avahi and may be unavailable while the network
is still starting. The router/DHCP client list and `ip -br addr` provide the
authoritative address. The radar Ethernet subnet must differ from every Wi-Fi
subnet. `eth0` carries radar UDP traffic; `wlan0` carries SSH and the default
route.

## ROS package installation

Ubuntu 22.04 requires the `universe` component for several development tools.
After enabling it, refresh APT and install the ROS 2 Humble packages listed in
[`SOFTWARE_STACK.md`](SOFTWARE_STACK.md). `ros2 --version` is not a supported
Humble CLI invocation; use `printenv ROS_DISTRO`, `ros2 pkg list` and
`colcon version-check` for validation.

## ARM64 compilation

Livox SDK and ROS driver binaries are architecture-specific. Build both on the
Pi with the ARM64 compiler. Low-memory boards can use a temporary swap file and
low parallelism (`-j2`). During a slow build, inspect `free -h`, `ps` and CPU
activity before interrupting the compiler.

## NTFS data storage

`findmnt --verify` can report a type-name warning for the `ntfs-3g` userspace
driver. The runtime checks are the mounted UUID, actual filesystem type
(`fuseblk` or `ntfs3`), read/write state, write probe and free-space result.
The storage guard rejects a missing, read-only or mismatched disk. Volume repair
tools are outside this deployment workflow.

## Recording validation

Run the following sequence after the driver and disk are configured:

```bash
carrot-storage-guard
carrot-bag start smoke 1
carrot-bag status
carrot-bag stop
```

Inspect `metadata.yaml`, the `.db3` file, `bag_files.sha256`, `bag_info.txt` and
the `COMPLETE`/`FAILED` marker. The recorder rejects concurrent sessions,
incorrect topic types, missing messages, out-of-range frequencies, low disk
space and health failures. Abnormal sessions retain their original directory
and evidence; existing sessions are never overwritten or resumed.

## Common service checks

```bash
systemctl --user is-active carrot-driver.service
journalctl --user -u carrot-driver.service -n 50
carrot-bag logs <label>
vcgencmd get_throttled
df -h /mnt/carrot_disk
```
