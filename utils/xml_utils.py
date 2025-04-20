import os
import xml.etree.ElementTree as ET
from utils.logger import logger_instance as log

def insert_xml_if_missing(xml_file, target_key, xml_block):
    """
    Inserts an XML <source> block into a specific section of an existing XML file
    (e.g., Kodi's sources.xml) if it doesn't already exist.

    Args:
        xml_file (str): Path to the XML file to modify.
        target_key (str): The key indicating the section to modify, e.g., 'sources-files' (will extract 'files').
        xml_block (str): The raw XML block to insert (must be a valid <source> element).
    """

    if not os.path.exists(xml_file):
        log.error(f"❌ XML file not found: {xml_file}")
        raise FileNotFoundError(f"XML file not found: {xml_file}")

    # Extract the section name (e.g., 'files') from 'sources-files'
    try:
        section_tag = target_key.split("-")[1]
    except IndexError:
        log.error(f"❌ Invalid target section key: {target_key}")
        raise ValueError(f"Invalid target section key: {target_key}")

    tree = ET.parse(xml_file)
    root = tree.getroot()

    target_section = root.find(section_tag)
    if target_section is None:
        target_section = ET.SubElement(root, section_tag)
        log.info(f"ℹ️ Created missing section <{section_tag}> in XML.")

    try:
        new_elem = ET.fromstring(xml_block.strip())
    except ET.ParseError as e:
        log.error(f"❌ Invalid XML block: {e}")
        raise ValueError(f"Invalid XML block: {e}")

    new_name = new_elem.findtext("name")
    new_path = new_elem.findtext("path")

    # Check if a <source> with the same name or path already exists
    for existing in target_section.findall("source"):
        existing_name = existing.findtext("name")
        existing_path = existing.findtext("path")
        if existing_name == new_name or existing_path == new_path:
            log.info(f"✅ Source '{new_name}' already exists — skipping.")
            return

    # Append new source
    target_section.append(new_elem)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    log.info(f"✅ Inserted source '{new_name}' into <{section_tag}>.")
