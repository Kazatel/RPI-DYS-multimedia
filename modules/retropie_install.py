import os
import shutil
import subprocess
import hashlib
from utils.apt_utils import handle_package_install
from utils.logger import Logger
import config


def install_prerequisites(log):
    log.info("🔧 Installing prerequisites...")
    for pkg in ["git", "lsb-release"]:
        handle_package_install(pkg, auto_update_packages=True, log=log)


def clone_retropie(log):
    log.info("📥 Cloning RetroPie setup script...")
    if not os.path.exists("RetroPie-Setup"):
        try:
            log_file_path = log.get_log_file_path()
            with open(log_file_path, "a") as logfile:
                subprocess.run([
                    "git", "clone", "--depth=1", "https://github.com/RetroPie/RetroPie-Setup.git"
                ], check=True, stdout=logfile, stderr=subprocess.STDOUT)
            log.info("✅ Successfully cloned RetroPie-Setup repository.")
        except subprocess.CalledProcessError:
            log.error("❌ Failed to clone RetroPie-Setup repository. See log for details.")
    else:
        log.info("✅ RetroPie-Setup folder already exists. Skipping clone.")


def run_setup_script(log):
    log.info("🚀 Running RetroPie installation script...")
    os.chdir("RetroPie-Setup")
    subprocess.run(["chmod", "+x", "retropie_setup.sh", "retropie_packages.sh"])
    log_file_path = log.get_log_file_path()
    log.tail_note()

    try:
        with open(log_file_path, "a") as logfile:
            process = subprocess.Popen(
                ["sudo", "./retropie_packages.sh", "setup", "basic_install"],
                stdout=logfile,
                stderr=subprocess.STDOUT,
                bufsize=1,
                universal_newlines=True
            )
            returncode = process.wait()
            if returncode != 0:
                log.error("❌ RetroPie installation failed. Check the log.")
            else:
                log.info("✅ RetroPie installation completed successfully.")
    except Exception as e:
        log.error(f"❌ Error during RetroPie installation: {e}")


def is_retropie_installed():
    return os.path.exists("/opt/retropie/configs")


def get_retropie_version():
    version_file = "/opt/retropie/VERSION"
    if os.path.exists(version_file):
        try:
            result = subprocess.run(["cat", version_file], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Version file exists, but could not be read."
    return None


def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None


def files_different(file1, file2):
    if not os.path.exists(file2):
        return True
    return calculate_sha256(file1) != calculate_sha256(file2)


def handle_missing_folders(rel_dir, log):
    src = os.path.join(config.RETROPIE_SOURCE_PATH, rel_dir)
    dst = os.path.join(config.RETROPIE_LOCAL_PATH, rel_dir)

    if not os.path.isdir(src) or not os.path.isdir(dst) or os.path.islink(dst):
        return

    source_subdirs = [d for d in os.listdir(src) if os.path.isdir(os.path.join(src, d))]
    local_subdirs = [d for d in os.listdir(dst) if os.path.isdir(os.path.join(dst, d))]
    missing = set(source_subdirs) - set(local_subdirs)

    for subdir in missing:
        src_path = os.path.join(src, subdir)
        dst_path = os.path.join(dst, subdir)
        log.info(f"🔗 Creating missing symlink: {dst_path} → {src_path}")
        os.symlink(src_path, dst_path)


def sync_directory(rel_dir, log):
    src = os.path.join(config.RETROPIE_SOURCE_PATH, rel_dir)
    dst = os.path.join(config.RETROPIE_LOCAL_PATH, rel_dir)

    log.info(f"📂 Processing: {rel_dir}")

    if not os.path.isdir(src):
        log.warn(f"⚠️ Source directory {src} doesn't exist. Skipping...")
        return

    if os.path.isdir(dst) and not os.path.islink(dst):
        handle_missing_folders(rel_dir, log)
        for root, _, files in os.walk(dst):
            rel_path = os.path.relpath(root, dst)
            target_dir = os.path.join(src, rel_path)
            os.makedirs(target_dir, exist_ok=True)
            for file in files:
                local_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)
                if files_different(local_file, target_file):
                    log.info(f"  🔄 Copying: {local_file} → {target_file}")
                    shutil.copy2(local_file, target_file)

        log.info(f"  🔁 Replacing folder with symlink: {dst} → {src}")
        shutil.rmtree(dst)
        os.symlink(src, dst)

    elif not os.path.exists(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        log.info(f"  🔗 Creating symlink: {dst} → {src}")
        os.symlink(src, dst)

    elif os.path.islink(dst):
        log.info(f"  ✅ Already symlinked: {dst}")
    else:
        log.warn(f"⚠️ Unexpected state at {dst}. Skipping...")


def sync_retropie_directories(log):
    if not config.RETROPIE_SOURCE_PATH:
        log.warn("⚠️ RETROPIE_SOURCE_PATH is not set in config. Skipping symlink setup.")
        return

    if not os.path.isdir(config.RETROPIE_SOURCE_PATH):
        log.warn(f"⚠️ Source path {config.RETROPIE_SOURCE_PATH} does not exist or is not mounted.")
        return

    log.info("🔁 Syncing RetroPie directories...")
    for folder in ["BIOS", "retropiemenu", "roms", "splashscreens"]:
        sync_directory(folder, log)
    log.info("✅ Sync complete.")


def main_install(log=None):
    if log is None:
        log = Logger()

    if is_retropie_installed():
        version = get_retropie_version()
        if version:
            log.info(f"✅ RetroPie already installed. Version: {version}")
        else:
            log.info("✅ RetroPie already installed.")
        return

    install_prerequisites(log)
    clone_retropie(log)
    run_setup_script(log)
    sync_retropie_directories(log)


if __name__ == "__main__":
    main_install()
