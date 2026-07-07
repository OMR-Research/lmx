from lmx.musicxml.omitted_staff_header.set_header_time_visibility \
    import set_header_time_visibility
from ....assert_xml_equals import assert_xml_equals
import xml.etree.ElementTree as ET
from pathlib import Path
from lmx.musicxml.io.read_musicxml_tree_from_file \
    import read_musicxml_tree_from_file


def load_part(sample_name: str) -> ET.Element:
    musicxml_tree = read_musicxml_tree_from_file(
        Path(__file__).parent / f"{sample_name}.musicxml"
    )
    return musicxml_tree.find("part")


def test_header_time_can_be_set_to_visible():
    # solo staff
    my_part = load_part("time-44-octave-4")
    set_header_time_visibility(
        part_element=my_part,
        set_visibility="visible"
    )
    assert_xml_equals(
        given=my_part,
        expected=load_part("time-44-octave-4-visible")
    )

    # grandstaff
    my_part = load_part("piano-34-octave-3")
    set_header_time_visibility(
        part_element=my_part,
        set_visibility="visible"
    )
    assert_xml_equals(
        given=my_part,
        expected=load_part("piano-34-octave-3-visible")
    )


def test_header_time_can_be_set_to_invisible():
    # solo staff
    my_part = load_part("time-44-octave-4-visible")
    set_header_time_visibility(
        part_element=my_part,
        set_visibility="invisible"
    )
    assert_xml_equals(
        given=my_part,
        expected=load_part("time-44-octave-4")
    )

    # grandstaff
    my_part = load_part("piano-34-octave-3-visible")
    set_header_time_visibility(
        part_element=my_part,
        set_visibility="invisible"
    )
    assert_xml_equals(
        given=my_part,
        expected=load_part("piano-34-octave-3")
    )
