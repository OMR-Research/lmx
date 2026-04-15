from .MusicXmlLayoutMap import MusicXmlLayoutMap
import xml.etree.ElementTree as ET
from .extract_part_system import extract_part_system
import copy


def extract_system(
        layout_map: MusicXmlLayoutMap,
        page_index: int,
        page_system_index: int
) -> ET.ElementTree:
    """
    Extracts a system (with all parts) out of
    a MusicXML document given the system's location
    """
    
    # === separate out the part-system for each part ===

    part_systems = [
        extract_part_system(
            layout_map=layout_map,
            part_index=part_index,
            page_index=page_index,
            page_system_index=page_system_index
        )
        for part_index in range(len(layout_map.parts))
    ]
    
    # === render output musicxml file ===

    # extract important elements from the input file
    root = layout_map.musicxml_tree.getroot()
    identification_element = root.find("identification")
    defaults_element = root.find("defaults")
    part_list_element = root.find("part-list")
    assert identification_element is not None
    assert defaults_element is not None

    # build the output mxl tree
    root = ET.Element("score-partwise", {"version": "3.1"})
    root.append(copy.deepcopy(identification_element))
    root.append(copy.deepcopy(defaults_element))

    # part-list
    part_list_element = ET.Element("part-list")
    root.append(part_list_element)
    for part in layout_map.parts:
        part_list_element.append(copy.deepcopy(part.score_part_element))

    # parts
    for output_part_element in part_systems:
        root.append(output_part_element)

    return ET.ElementTree(root)
