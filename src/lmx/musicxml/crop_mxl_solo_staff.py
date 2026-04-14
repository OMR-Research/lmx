from .MusicXmlLayoutMap import MusicXmlLayoutMap, StaffLocation
import xml.etree.ElementTree as ET
from .get_part_system_from_mxl_document import get_part_system_from_mxl_document
from .split_piano_part_staves import split_piano_part_staves
import copy


def crop_mxl_solo_staff(
        layout_map: MusicXmlLayoutMap,
        staff_location: StaffLocation
) -> ET.ElementTree:
    """Crops a solo staff out of a MusicXML document given its location"""

    # get the part and slice
    source_part = layout_map.parts[staff_location.part_index]
    source_slice = get_part_system_from_mxl_document(
        layout_map=layout_map,
        part_index=staff_location.part_index,
        page_index=staff_location.page_index,
        page_system_index=staff_location.page_system_index
    )

    # === separate one staff out of piano parts ===

    assert source_part.staff_count in [1, 2], \
        "Target part has unsupported number of staves"
    
    if source_part.staff_count == 1:
        output_part_element = source_slice
    elif source_part.staff_count == 2:
        upper_slice, lower_slice = split_piano_part_staves(
            source_slice,
            upper_part_id=source_part.id,
            lower_part_id=source_part.id,
            force_split=False
        )
        if staff_location.part_staff_index == 0:
            output_part_element = upper_slice
        elif staff_location.part_staff_index == 1:
            output_part_element = lower_slice
        else:
            raise Exception("This should not happen")
    else:
        raise Exception("This should not happen")

    # === render output musicxml file ===

    # extract important elements from the input file
    root = layout_map.musicxml_tree.getroot()
    identification_element = root.find("identification")
    defaults_element = root.find("defaults")
    assert identification_element is not None
    assert defaults_element is not None

    # build the output mxl tree
    root = ET.Element("score-partwise", {"version": "3.1"})
    root.append(copy.deepcopy(identification_element))
    root.append(copy.deepcopy(defaults_element))

    # part-list
    part_list_element = ET.Element("part-list")
    root.append(part_list_element)
    part_list_element.append(copy.deepcopy(source_part.score_part_element))

    # the part itself
    root.append(output_part_element)

    return ET.ElementTree(root)
