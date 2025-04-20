import os
import config
from utils.xml_utils import insert_xml_if_missing
from utils.apt_utils import handle_package_install, check_package_installed
from utils.logger import logger_instance as log
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


import os
from xml.etree import ElementTree as ET

def configure_kodi_sources():
    """
    Ensures the Kodi sources.xml file exists with a base structure,
    then inserts configured repositories if they are missing.
    """
    xml_file = os.path.expanduser(config.KODI_REPOSITORY_FILE_PATH)
    target_section = "sources-files"

    if not os.path.exists(xml_file):
        os.makedirs(os.path.dirname(xml_file), exist_ok=True)
        with open(xml_file, "w", encoding="utf-8") as f:
            f.write("""<sources>
    <programs>
        <default pathversion="1"></default>
    </programs>
    <video>
        <default pathversion="1"></default>
    </video>
    <music>
        <default pathversion="1"></default>
    </music>
    <pictures>
        <default pathversion="1"></default>
    </pictures>
    <files>
        <default pathversion="1"></default>
    </files>
    <games>
        <default pathversion="1"></default>
    </games>
</sources>""")

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

def launch_and_kill_kodi():
    try:
        command = "(kodi & sleep 10 && killall kodi.bin)"
        return_code = run_command(
            command,
            run_as_user=config.USER,
            log_live=True,
            use_bash_wrapper=True
        )
        log.info(f"✅ Kodi launched and killed successfully (exit code: {return_code})")
    except Exception as e:
        log.error("❌ Failed to launch and kill Kodi.")
        log.debug(f"Error: {e}")

def main_install():


    if is_kodi_installed():
        if getattr(config, "AUTO_UPDATE_PACKAGES", False):
            log.info("🔁 Kodi is already installed. Updating because AUTO_UPDATE_PACKAGES is enabled...")
        else:
            choice = ask_user_choice(
                "✅ Kodi is already installed. Do you want to update it?",
                {"y": "Yes, update", "n": "No, skip"}
            )
            if choice == "n":
                log.info("⏩ Skipping Kodi update per user choice.")
                return

    log.info("\n📦 Installing Kodi...")
    log.tail_note()
    success = handle_package_install(PACKAGE_NAME, config.AUTO_UPDATE_PACKAGES)

    if not success:
        log.error("❌ Failed to install Kodi.")


def main_configure():
    log.info("🚀 Launching Kodi to initialize configuration folders...")
    launch_and_kill_kodi()
    log.info("⚙️  Configuring Kodi sources...")
    configure_kodi_sources()
    log.info("✅ Kodi configuration complete.")

if __name__ == "__main__":
    main_install()
    main_configure()
