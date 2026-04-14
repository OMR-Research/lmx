from .MusicXmlLayoutMap import MusicXmlLayoutMap, StaffLocation
import xml.etree.ElementTree as ET
from .get_part_system_from_mxl_document import get_part_system_from_mxl_document
from .merge_piano_part_staves import merge_piano_part_staves
from .split_piano_part_staves import split_piano_part_staves
import copy


def crop_mxl_piano_staff(
        layout_map: MusicXmlLayoutMap,
        upper_staff_location: StaffLocation,
        lower_staff_location: StaffLocation
) -> ET.ElementTree:
    """Crops a piano staff out of a MusicXML document given its location"""

    # get the source parts and slices
    upper_part = layout_map.parts[upper_staff_location.part_index]
    lower_part = layout_map.parts[lower_staff_location.part_index]
    upper_slice = get_part_system_from_mxl_document(
        layout_map=layout_map,
        part_index=upper_staff_location.part_index,
        page_index=upper_staff_location.page_index,
        page_system_index=upper_staff_location.page_system_index
    )
    lower_slice = get_part_system_from_mxl_document(
        layout_map=layout_map,
        part_index=lower_staff_location.part_index,
        page_index=lower_staff_location.page_index,
        page_system_index=lower_staff_location.page_system_index
    )

    # === merge two parts to form a piano part if needed ===

    # if the two parts are the same 2-staff part, then both slices
    # are identical and they are our output
    if upper_part is lower_part and upper_part.staff_count == 2:
        output_part_element = upper_slice
    else:
        # else we're merging two solo parts
        assert upper_part.staff_count in [1, 2]
        assert lower_part.staff_count in [1, 2]

        # if the two parts are actually pianos, split them first
        if upper_part.staff_count == 2:
            _, upper_slice = split_piano_part_staves(
                piano_part=upper_slice,
                upper_part_id="Ignored",
                lower_part_id=upper_part.id,
                force_split=False
            )
        if lower_part.staff_count == 2:
            lower_slice, _ = split_piano_part_staves(
                piano_part=lower_slice,
                upper_part_id=lower_part.id,
                lower_part_id="Ignored",
                force_split=False
            )

        # merge the two solo slices
        output_part_element = merge_piano_part_staves(
            upper_part=upper_slice,
            lower_part=lower_slice,
            output_part_id=upper_part.id
        )

    # === render output musicxml file ===

    # extract important elements from the input file
    root = layout_map.musicxml_tree.getroot()
    assert root is not None
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
    part_list_element.append(copy.deepcopy(upper_part.score_part_element))

    # the part itself
    root.append(output_part_element)

    return ET.ElementTree(root)
