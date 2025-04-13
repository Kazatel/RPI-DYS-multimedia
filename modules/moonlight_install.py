import subprocess
from utils.apt_utils import handle_package_install

PACKAGE_NAME = "moonlight-qt"
REQUIRED_DEPS = ["git", "lsb-release"]


def install_moonlight():
    print("\n➡️  Installing dependencies for Moonlight...")
    for dep in REQUIRED_DEPS:
        handle_package_install(dep, auto_select_version=True)

    print("\n➡️  Setting up Moonlight repository...")
    try:
        subprocess.check_call(
            [
                "bash", "-c",
                "curl -1sLf 'https://dl.cloudsmith.io/public/moonlight-game-streaming/moonlight-qt/setup.deb.sh' | "
                "distro=raspbian codename=$(lsb_release -cs) sudo -E bash"
            ]
        )
    except subprocess.CalledProcessError as e:
        print("❌ Failed to set up Moonlight repository:", e)
        return False

    print("\n➡️  Installing Moonlight...")
    success = handle_package_install(PACKAGE_NAME, auto_select_version=True)
    return success


def main():
    if install_moonlight():
        print("\n✅ Moonlight installed successfully!")
    else:
        print("\n❌ Moonlight installation failed.")


if __name__ == "__main__":
    main()