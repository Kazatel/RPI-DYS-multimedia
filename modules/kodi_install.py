import os
import config
from utils.xml_utils import insert_xml_if_missing
from utils.apt_utils import handle_package_install, check_package_installed
from utils.logger import Logger
from utils.interaction import ask_user_choice

PACKAGE_NAME = "kodi"


def generate_kodi_source_block(name, url, pathversion="1", allowsharing=True):
    """
    Generates a Kodi XML <source> block.

    Args:
        name (str): Name of the source.
        url (str): URL or path of the source.
        pathversion (str, optional): Path version. Defaults to "1".
        allowsharing (bool, optional): Whether to allow sharing. Defaults to True.

    Returns:
        str: XML string block for the Kodi source.
    """
    allowsharing_str = "<allowsharing>true</allowsharing>" if allowsharing else ""
    return f'''
    <source>
        <name>{name}</name>
        <path pathversion="{pathversion}">{url}</path>
        {allowsharing_str}
    </source>
    '''


def configure_kodi_sources():
    """
    Inserts configured Kodi repositories into the sources XML if they are missing.
    """
    xml_file = os.path.expanduser(config.KODI_REPOSITORY_FILE_PATH)
    target_section = "sources-files"

    for repo in config.KODI_REPOSITORIES:
        name = repo.get("name")
        url = repo.get("url")
        pathversion = repo.get("pathversion", "1")
        allowsharing = repo.get("allowsharing", True)

        xml_block = generate_kodi_source_block(name, url, pathversion, allowsharing)
        insert_xml_if_missing(xml_file, target_section, xml_block)


def is_kodi_installed():
    """
    Checks if Kodi is already installed.

    Returns:
        bool: True if installed, False otherwise.
    """
    return check_package_installed(PACKAGE_NAME)


def main(log=None):
    """
    Main function to install and configure Kodi.

    Args:
        log (Logger, optional): Logger instance. If None, a new logger is created.
    """
    if log is None:
        log = Logger()

    if is_kodi_installed():
        if getattr(config, "AUTO_UPDATE_PACKAGES", False):
            log.p_info("🔁 Kodi is already installed. Updating as AUTO_UPDATE_PACKAGES is enabled...")
        else:
            choice = ask_user_choice(
                "✅ Kodi is already installed. Do you want to update it?",
                {"y": "Yes, update", "n": "No, skip"}
            )
            if choice == "n":
                log.p_info("⏩ Skipping Kodi update per user choice.")
                return

    log.p_info("\n📦 Installing Kodi...")
    log.tail_note()
    success = handle_package_install(PACKAGE_NAME, config.AUTOMATIC_VERSION_SELECTION, log=log)

    if success:
        log.p_info("⚙️  Configuring Kodi sources...")
        configure_kodi_sources()
        log.p_info("✅ Kodi installation and configuration complete.")
    else:
        log.p_error("❌ Failed to install Kodi.")


if __name__ == "__main__":
    main()
