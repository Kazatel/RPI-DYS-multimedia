import os
import xml.etree.ElementTree as ET

def insert_xml_if_missing(xml_file, target_section, xml_block):
    if not os.path.exists(xml_file):
        raise FileNotFoundError(f"❌ XML file not found: {xml_file}")

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Traverse or create nested section path
    section_path = target_section.split("-")
    current = root
    for section in section_path:
        next_elem = current.find(section)
        if next_elem is None:
            next_elem = ET.SubElement(current, section)
        current = next_elem

    # Convert the provided xml_block string to an Element
    try:
        new_elem = ET.fromstring(xml_block.strip())
    except ET.ParseError as e:
        raise ValueError(f"❌ Invalid XML block provided: {e}")

    # Compare with existing children
    for child in current.findall(new_elem.tag):
        if ET.tostring(child, encoding="unicode").strip() == ET.tostring(new_elem, encoding="unicode").strip():
            print(f"✅ XML block already exists in section <{'-'.join(section_path)}> — Skipping insertion.")
            return

    # Insert the new XML block
    current.append(new_elem)
    tree.write(xml_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ Inserted XML block into section <{'-'.join(section_path)}>.")
