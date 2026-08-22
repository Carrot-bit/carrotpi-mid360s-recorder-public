#!/usr/bin/env bash
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo 'run with sudo' >&2; exit 2; }
root=$(cd "$(dirname "$0")" && pwd)
install -d -m 0755 /usr/local/lib/carrot-recorder /usr/local/share/carrot-recorder /usr/local/bin /etc/carrot-net
install -m 0755 "$root/bin/carrot-bag" /usr/local/bin/carrot-bag
install -m 0755 "$root/bin/carrot-storage-guard" /usr/local/bin/carrot-storage-guard
install -m 0755 "$root/bin/carrot-driver-launch" /usr/local/bin/carrot-driver-launch
install -m 0755 "$root/bin/carrot-net" /usr/local/bin/carrot-net
install -m 0755 "$root/bin/carrot-net-auto-priority" /usr/local/lib/carrot-recorder/carrot-net-auto-priority
install -m 0755 "$root/bin/carrot-livox-verify" /usr/local/bin/carrot-livox-verify
install -m 0755 "$root/bin/topic_watchdog.py" /usr/local/lib/carrot-recorder/topic_watchdog.py
install -m 0755 "$root/bin/verify_bag.py" /usr/local/lib/carrot-recorder/verify_bag.py
if [[ -f "$root/livox/livox_ros_driver2.files.sha256" ]]; then
  install -m 0644 "$root/livox/livox_ros_driver2.files.sha256" /usr/local/share/carrot-recorder/livox_ros_driver2.files.sha256
else
  printf '%s\n' 'Public template: add your locally generated Livox source manifest before installation.' >&2
fi
install -m 0644 "$root/systemd/carrot-driver.service" /etc/systemd/user/carrot-driver.service
install -m 0644 "$root/systemd/carrot-bag@.service" /etc/systemd/user/carrot-bag@.service
install -m 0644 "$root/systemd/carrot-net-auto-priority.service" /etc/systemd/system/carrot-net-auto-priority.service
[[ -e /etc/carrot-net/home.yaml ]] || install -m 0600 "$root/netplan/home.yaml" /etc/carrot-net/home.yaml
[[ -e /etc/carrot-net/field.yaml ]] || install -m 0600 "$root/netplan/field.yaml" /etc/carrot-net/field.yaml
[[ -e /etc/carrot-net/rescue.yaml ]] || install -m 0600 "$root/netplan/rescue.yaml" /etc/carrot-net/rescue.yaml
install -d -m 0755 /etc/netplan
rm -f /etc/netplan/50-cloud-init.yaml
install -d -m 0755 /etc/cloud/cloud.cfg.d
printf 'network: {config: disabled}\n' > /etc/cloud/cloud.cfg.d/99-carrot-disable-network-config.cfg
# NoCloud has completed before this post-first-boot installer runs. Disabling
# further cloud-init probing avoids a recurring 30-second boot delay.
: > /etc/cloud/cloud-init.disabled
target_user=${SUDO_USER:-carrotuser}
target_uid=$(id -u "$target_user")
usermod -a -G adm,video "$target_user"
loginctl enable-linger "$target_user"
systemctl daemon-reload
systemctl enable carrot-net-auto-priority.service
# All shipped profiles use NetworkManager. The networkd waiter otherwise adds
# a fixed two-minute delay before headless Wi-Fi and SSH become available.
systemctl mask systemd-networkd-wait-online.service
runuser -u "$target_user" -- env XDG_RUNTIME_DIR="/run/user/$target_uid" \
  systemctl --user daemon-reload
printf 'Installed. Configure /etc/carrot-net templates and /etc/fstab, then reboot.\n'
