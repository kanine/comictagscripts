import sys
import os
import re
import zipfile
from xml.etree import ElementTree as ET

def extract_volume_from_folder(path):
    folder = os.path.dirname(path)
    match = re.search(r"\((\d{4})\)", folder)
    if match:
        return int(match.group(1))
    return None

def update_volume_tag(cbz_path):
    volume_tag_updated = False
    xml_filename = "ComicInfo.xml"

    target_volume = extract_volume_from_folder(cbz_path)
    if target_volume is None:
        print(f"⚠️  Could not find volume in folder name for {cbz_path}. Skipping.")
        return

    with zipfile.ZipFile(cbz_path, "r") as zip_read:
        namelist = zip_read.namelist()
        if xml_filename not in namelist:
            print(f"❌ No ComicInfo.xml found in {cbz_path}. Skipping.")
            return

        # Read existing ComicInfo.xml
        xml_data = zip_read.read(xml_filename).decode("utf-8")

    root = ET.fromstring(xml_data)

    volume_elem = root.find("Volume")
    if volume_elem is None:
        volume_elem = ET.SubElement(root, "Volume")
        volume_elem.text = str(target_volume)
        volume_tag_updated = True
        print(f"✅ Added volume {target_volume} to {cbz_path}")
    elif volume_elem.text != str(target_volume):
        print(f"🔁 Updating volume in {cbz_path} from {volume_elem.text} to {target_volume}")
        volume_elem.text = str(target_volume)
        volume_tag_updated = True
    else:
        print(f"✅ Volume already correct in {cbz_path} ({volume_elem.text}). Skipping.")

    if volume_tag_updated:
        new_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

        temp_path = cbz_path + ".tmp"
        with zipfile.ZipFile(cbz_path, "r") as zin, zipfile.ZipFile(temp_path, "w") as zout:
            for item in zin.infolist():
                if item.filename != xml_filename:
                    zout.writestr(item, zin.read(item.filename))
            zout.writestr(xml_filename, new_xml)

        os.replace(temp_path, cbz_path)

def process_folder(folder_path):
    if not os.path.isdir(folder_path):
        print(f"❌ Not a valid folder: {folder_path}")
        return

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".cbz"):
                cbz_path = os.path.join(root, file)
                update_volume_tag(cbz_path)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        folder = sys.argv[1]
    else:
        folder = input("Enter path to a folder containing .cbz files: ").strip()

    process_folder(folder)
