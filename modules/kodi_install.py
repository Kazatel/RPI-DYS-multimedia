import os
import subprocess
from utils.xml_utils import insert_xml_if_missing
import config


def generate_kodi_source_block(name, url, pathversion="1", allowsharing=True):
    allowsharing_str = "<allowsharing>true</allowsharing>" if allowsharing else ""
    return f'''
    <source>
        <name>{name}</name>
        <path pathversion="{pathversion}">{url}</path>
        {allowsharing_str}
    </source>
    '''


def is_kodi_installed():
    try:
        output = subprocess.check_output(["kodi", "--version"], stderr=subprocess.STDOUT)
        version_line = output.decode().strip().split("\n")[0]
        return True, version_line
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, None


def get_latest_kodi_version():
    try:
        output = subprocess.check_output(["apt-cache", "policy", "kodi"]).decode()
        for line in output.split("\n"):
            if "Candidate:" in line:
                return line.strip().split()[1]
    except subprocess.CalledProcessError:
        pass
    return None


def install_kodi():
    print("📦 Installing Kodi...")
    subprocess.run(["sudo", "apt", "update"])
    subprocess.run(["sudo", "apt", "install", "-y", "kodi"])


def upgrade_kodi():
    print("⬆️  Upgrading Kodi to the latest version...")
    subprocess.run(["sudo", "apt", "install", "--only-upgrade", "-y", "kodi"])


def configure_kodi_sources():
    xml_file = os.path.expanduser(config.KODI_REPOSITORY_FILE_PATH)
    target_section = "sources-files"

    for repo in config.KODI_REPOSITORIES:
        name = repo.get("name")
        url = repo.get("url")
        pathversion = repo.get("pathversion", "1")
        allowsharing = repo.get("allowsharing", True)

        xml_block = generate_kodi_source_block(name, url, pathversion, allowsharing)
        insert_xml_if_missing(xml_file, target_section, xml_block)


def main():
    installed, installed_version = is_kodi_installed()
    latest_version = get_latest_kodi_version()

    if installed:
        print(f"✅ Kodi is already installed: {installed_version}")
        if installed_version and latest_version and installed_version < latest_version:
            if config.AUTOMATIC_VERSION_SELECTION:
                print(f"🔄 Newer version available ({latest_version}). Upgrading automatically...")
                upgrade_kodi()
            else:
                answer = input(f"❓ Kodi version {latest_version} available. Do you want to upgrade? (yes/no): ").strip().lower()
                if answer == "yes":
                    upgrade_kodi()
    else:
        install_kodi()

    # Post-install configuration
    configure_kodi_sources()


if __name__ == "__main__":
    main()

