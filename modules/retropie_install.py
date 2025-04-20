import os
import shutil
import hashlib
from utils.apt_utils import handle_package_install
from utils.logger import get_logger as log
import config
from utils.os_utils import get_home_directory, run_command

HOME_DIR = get_home_directory()
RETROPIE_CLONE_DIR = os.path.join(HOME_DIR, "RetroPie-Setup")


def install_prerequisites():
    log.info("🔧 Installing prerequisites...")
    for pkg in ["git", "lsb-release"]:
        handle_package_install(pkg, auto_update_packages=True, log=log)


def clone_retropie():
    log.info("📥 Cloning RetroPie setup script...")
    if not os.path.exists(RETROPIE_CLONE_DIR):
        try:
            run_command(
                ["git", "clone", "--depth=1", "https://github.com/RetroPie/RetroPie-Setup.git", RETROPIE_CLONE_DIR],
                log_path=log.get_log_file_path(),
                run_as_user=config.APPLICATIONS["retropie"]["user"]
            )
            log.info("✅ Successfully cloned RetroPie-Setup repository.")
        except Exception:
            log.error("❌ Failed to clone RetroPie-Setup repository. See log for details.")
    else:
        log.info("✅ RetroPie-Setup folder already exists. Skipping clone.")


def run_setup_script():
    log.info("🚀 Running RetroPie installation script...")
    user = config.APPLICATIONS["retropie"]["user"]

    script_path = os.path.join(RETROPIE_CLONE_DIR, "retropie_packages.sh")
    setup_path = os.path.join(RETROPIE_CLONE_DIR, "retropie_setup.sh")

    run_command(["chmod", "+x", setup_path, script_path])

    log.tail_note()

    try:
        run_command(
            f"cd '{RETROPIE_CLONE_DIR}' && ./retropie_packages.sh setup basic_install",
            log_path=log.get_log_file_path(),
            run_as_user=user,
            use_bash_wrapper=True
        )
        log.info("✅ RetroPie installation completed successfully.")
    except Exception as e:
        log.error(f"❌ RetroPie installation failed: {e}")


def is_retropie_installed():
    return os.path.exists("/opt/retropie/configs")


def get_retropie_version():
    version_file = "/opt/retropie/VERSION"
    if os.path.exists(version_file):
        try:
            result = run_command(["cat", version_file], capture_output=True)
            return result.stdout.strip()
        except Exception:
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


def handle_missing_folders(rel_dir):
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


def sync_directory(rel_dir):
    src = os.path.join(config.RETROPIE_SOURCE_PATH, rel_dir)
    dst = os.path.join(config.RETROPIE_LOCAL_PATH, rel_dir)

    log.info(f"📂 Processing: {rel_dir}")

    if not os.path.isdir(src):
        log.warn(f"⚠️ Source directory {src} doesn't exist. Skipping...")
        return

    if os.path.isdir(dst) and not os.path.islink(dst):
        handle_missing_folders(rel_dir)
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


def sync_retropie_directories():
    if not config.RETROPIE_SOURCE_PATH:
        log.warn("⚠️ RETROPIE_SOURCE_PATH is not set in config. Skipping symlink setup.")
        return

    if not os.path.isdir(config.RETROPIE_SOURCE_PATH):
        log.warn(f"⚠️ Source path {config.RETROPIE_SOURCE_PATH} does not exist or is not mounted.")
        return

    log.info("🔁 Syncing RetroPie directories...")
    for folder in ["BIOS", "retropiemenu", "roms", "splashscreens"]:
        sync_directory(folder)
    log.info("✅ Sync complete.")


def main_install(force=False):
    if is_retropie_installed() and not force:
        version = get_retropie_version()
        if version:
            log.info(f"✅ RetroPie already installed. Version: {version}")
        else:
            log.info("✅ RetroPie already installed.")
        return

    install_prerequisites()
    clone_retropie()
    run_setup_script()


def main_configure():
    sync_retropie_directories()


if __name__ == "__main__":
    main_install(force=True)
    main_configure()
