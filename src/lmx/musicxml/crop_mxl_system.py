from .MusicXmlLayoutMap import MusicXmlLayoutMap
import xml.etree.ElementTree as ET
from .get_part_system_from_mxl_document import get_part_system_from_mxl_document
import copy


def crop_mxl_system(
        layout_map: MusicXmlLayoutMap,
        page_index: int,
        page_system_index: int
) -> ET.ElementTree:
    """Crops a system out of a MusicXML document given its location"""
    
    # === separate out the part-system for each part ===

    part_systems = [
        get_part_system_from_mxl_document(
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
