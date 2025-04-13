import os
import config
from utils.xml_utils import insert_xml_if_missing
from utils.apt_utils import handle_package_install
from utils.os_utils import is_command_available


def generate_kodi_source_block(name, url, pathversion="1", allowsharing=True):
    allowsharing_str = "<allowsharing>true</allowsharing>" if allowsharing else ""
    return f'''
    <source>
        <name>{name}</name>
        <path pathversion="{pathversion}">{url}</path>
        {allowsharing_str}
    </source>
    '''


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
    print("📦 Checking/installing Kodi...")
    success = handle_package_install("kodi", config.AUTOMATIC_VERSION_SELECTION)

    if success:
        print("⚙️  Configuring Kodi sources...")
        configure_kodi_sources()
    else:
        print("❌ Failed to install Kodi.")


if __name__ == "__main__":
    main()
