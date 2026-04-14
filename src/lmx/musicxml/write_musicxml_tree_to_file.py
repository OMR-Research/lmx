from pathlib import Path
import xml.etree.ElementTree as ET


def write_musicxml_tree_to_file(
        file_path: Path | str,
        musicxml_tree: ET.ElementTree,
        make_parent_folder=True
):
    """Writes a MusicXML document into an uncompressed .musicxml file"""
    if make_parent_folder:
        Path(str(file_path)).parent.mkdir(exist_ok=True, parents=True)
    
    musicxml_string = str(ET.tostring(
        musicxml_tree.getroot(),
        encoding="utf-8",
        xml_declaration=True
    ), "utf-8")

    with open(file_path, "w") as file:
        file.write(musicxml_string)
