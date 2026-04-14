from pathlib import Path
import xml.etree.ElementTree as ET
from .read_musicxml_string_from_file import read_musicxml_string_from_file
from .parse_musicxml_tree_from_string import parse_musicxml_tree_from_string


def read_musicxml_tree_from_file(
        file_path: Path | str
) -> ET.ElementTree:
    """
    Reads the given .musicxml, .xml, or .mxl file and returns
    the ElementTree representation of its content.
    """
    musicxml_string = read_musicxml_string_from_file(
        file_path=file_path
    )
    musicxml_tree = parse_musicxml_tree_from_string(
        musicxml_string=musicxml_string
    )
    return musicxml_tree
