import os
import xml.etree.ElementTree as ET

def insert_xml_if_missing(xml_file, target_key, xml_block):
    if not os.path.exists(xml_file):
        raise FileNotFoundError(f"❌ XML file not found: {xml_file}")

    # Extract actual section tag (like 'files') from 'sources-files'
    try:
        section_tag = target_key.split("-")[1]
    except IndexError:
        raise ValueError(f"❌ Invalid target section key: {target_key}")

    tree = ET.parse(xml_file)
    root = tree.getroot()

    target_section = root.find(section_tag)
    if target_section is None:
        target_section = ET.SubElement(root, section_tag)

    try:
        new_elem = ET.fromstring(xml_block.strip())
    except ET.ParseError as e:
        raise ValueError(f"❌ Invalid XML block: {e}")

    new_name = new_elem.findtext("name")
    new_path = new_elem.findtext("path")

    # Check for duplicates
    for existing in target_section.findall("source"):
        existing_name = existing.findtext("name")
        existing_path = existing.findtext("path")
        if existing_name == new_name or existing_path == new_path:
            print(f"✅ Source '{new_name}' already exists — skipping.")
            return

    target_section.append(new_elem)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ Inserted source '{new_name}' into <{section_tag}>.")
