# Livox ROS Driver 2 source baseline template

The public repository intentionally does not include a measured source
manifest or hardware-specific checksums. Build Livox-SDK2 and
`livox_ros_driver2` natively on the target ARM64 Pi, then generate a local
manifest and set the verifier variables before acquisition.

From the `carrot_ws/src` directory, verify the locally supplied source snapshot with:

```bash
sha256sum -c /usr/local/share/carrot-recorder/livox_ros_driver2.files.sha256
```
