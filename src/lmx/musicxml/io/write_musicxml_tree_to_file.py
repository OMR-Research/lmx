from pathlib import Path
import xml.etree.ElementTree as ET
from .serialize_musicxml_tree_to_string import serialize_musicxml_tree_to_string


def write_musicxml_tree_to_file(
        file_path: Path | str,
        musicxml_tree: ET.ElementTree,
        make_parent_folder=True
):
    """Writes a MusicXML document into an uncompressed .musicxml file"""
    if make_parent_folder:
        Path(str(file_path)).parent.mkdir(exist_ok=True, parents=True)
    
    musicxml_string = serialize_musicxml_tree_to_string(musicxml_tree)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(musicxml_string)
