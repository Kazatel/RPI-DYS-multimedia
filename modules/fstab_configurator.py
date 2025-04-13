import os
import re
import subprocess
from datetime import datetime
import config
from utils import apt_utils

FSTAB_PATH = "/etc/fstab"
FSTAB_MARKER_PREFIX = "# added by script"
FSTAB_MARKER_RE = re.compile(rf"^{re.escape(FSTAB_MARKER_PREFIX)}.*$")

def get_blkid_data():
    try:
        blkid_output = subprocess.check_output(["blkid"], text=True)
        return blkid_output.strip().splitlines()
    except subprocess.CalledProcessError:
        return []

def parse_blkid_output(lines):
    disks_info = {}
    for line in lines:
        match = re.match(r'^(/dev/\S+): (.+)$', line)
        if not match:
            continue
        device, attrs_str = match.groups()
        attrs = dict(re.findall(r'(\w+)="([^"]+)"', attrs_str))
        label = attrs.get("LABEL")
        if label:
            disks_info[label] = {
                "device": device,
                "uuid": attrs.get("UUID"),
                "type": attrs.get("TYPE"),
            }
    return disks_info

def update_fstab_with_disks(auto_select_version=True):
    print("⚙️ Preparing to update /etc/fstab with external disks...")
    blkid_lines = get_blkid_data()
    disks_by_label = parse_blkid_output(blkid_lines)

    new_lines = []
    ntfs_needed = False

    for disk in config.DISKS:
        label = disk.get("name")
        mount_point = disk.get("mountpoint")

        if label not in disks_by_label:
            print(f"⚠️ Disk with label '{label}' not found — skipping.")
            continue

        disk_info = disks_by_label[label]
        uuid = disk_info["uuid"]
        fs_type = disk_info["type"]

        if fs_type == "ntfs":
            ntfs_needed = True
            fs_type = "ntfs-3g"
            options = "defaults,auto,nofail,x-systemd.device-timeout=30,uid=1000,gid=1000"
        else:
            options = "defaults"

        new_lines.append(
            f"UUID={uuid}\t{mount_point}\t{fs_type}\t{options}\t0\t2"
        )

    # Install ntfs-3g if needed
    if ntfs_needed:
        print("ℹ️ NTFS filesystem detected — checking ntfs-3g...")
        apt_utils.handle_package_install("ntfs-3g", auto_select_version)

    # Load existing fstab and remove old entries
    if not os.path.exists(FSTAB_PATH):
        print(f"❌ {FSTAB_PATH} not found.")
        return

    with open(FSTAB_PATH, "r") as f:
        lines = f.readlines()

    updated_lines = []
    marker_found = False
    for line in lines:
        if marker_found:
            continue
        if FSTAB_MARKER_RE.match(line.strip()):
            marker_found = True
            continue
        updated_lines.append(line.rstrip())

    # Add marker with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated_lines.append(f"{FSTAB_MARKER_PREFIX} {timestamp}")
    updated_lines.extend(new_lines)

    # Write back to fstab
    try:
        with open(FSTAB_PATH, "w") as f:
            f.write("\n".join(updated_lines) + "\n")
        print("✅ /etc/fstab updated successfully.")
    except Exception as e:
        print(f"❌ Failed to update {FSTAB_PATH}: {e}")
