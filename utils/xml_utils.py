import os
import xml.etree.ElementTree as ET

def insert_xml_if_missing(xml_file, target_section, xml_block):
    if not os.path.exists(xml_file):
        raise FileNotFoundError(f"❌ XML file not found: {xml_file}")

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Find the correct section (e.g., <files>)
    target = root.find(target_section)
    if target is None:
        target = ET.SubElement(root, target_section)

    # Convert xml_block (str) to Element
    try:
        new_elem = ET.fromstring(xml_block.strip())
    except ET.ParseError as e:
        raise ValueError(f"❌ Invalid XML block: {e}")

    # Check if this block already exists (based on name or URL)
    new_name = new_elem.findtext("name")
    new_path = new_elem.findtext("path")

    for existing in target.findall("source"):
        existing_name = existing.findtext("name")
        existing_path = existing.findtext("path")
        if existing_name == new_name or existing_path == new_path:
            print(f"✅ Source '{new_name}' already exists — skipping.")
            return

    # Append if not found
    target.append(new_elem)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ Inserted source '{new_name}' into <{target_section}>.")
