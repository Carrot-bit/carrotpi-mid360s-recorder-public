# SD image workflow

Full SD images are stored as release artifacts or in object storage rather than
Git history. A published image record contains the OS version, architecture,
creation date, compression format, byte size and SHA-256 checksum.

## Create an image

Stop the recorder, stop the driver, unmount the data disk, and identify the SD
whole-disk device with `lsblk`. The source device is read only during this
operation; the destination must be a different filesystem with sufficient free
space.

```bash
sudo sync
sudo umount /mnt/carrot_disk
lsblk -o NAME,MODEL,SERIAL,SIZE,FSTYPE,LABEL,MOUNTPOINTS
sudo dd if=/dev/<confirmed-sd-device> of=/path/to/carrotpi-ubuntu-22.04.5.img \
  bs=4M status=progress iflag=fullblock
sync
xz -T0 -z /path/to/carrotpi-ubuntu-22.04.5.img
sha256sum /path/to/carrotpi-ubuntu-22.04.5.img.xz
```

The image includes the device's local machine identity, SSH host keys and any
local network configuration present at capture time. Release metadata states
whether those values were removed or regenerated.

## Restore an image

Identify the target SD whole-disk device by model, serial and capacity, then
write the verified image:

```bash
sha256sum -c image.sha256
xz -dc carrotpi-ubuntu-22.04.5.img.xz | \
  sudo dd of=/dev/<confirmed-sd-device> bs=4M status=progress conv=fsync
sync
```

Partition names and device paths are system-dependent; the examples use
placeholders intentionally.
