from lmx.musicxml.omitted_staff_header.set_header_key_visibility \
    import set_header_key_visibility
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


def test_header_key_can_be_set_to_visible():
    # solo staff
    my_part = load_part("key-7-octave")
    set_header_key_visibility(
        part_element=my_part,
        set_visibility="visible"
    )
    assert_xml_equals(
        given=my_part,
        expected=load_part("key-7-octave-visible")
    )

    # grandstaff
    my_part = load_part("piano-7-octave")
    set_header_key_visibility(
        part_element=my_part,
        set_visibility="visible"
    )
    assert_xml_equals(
        given=my_part,
        expected=load_part("piano-7-octave-visible")
    )


def test_header_key_can_be_set_to_invisible():
    # solo staff
    my_part = load_part("key-7-octave-visible")
    set_header_key_visibility(
        part_element=my_part,
        set_visibility="invisible"
    )
    assert_xml_equals(
        given=my_part,
        expected=load_part("key-7-octave")
    )

    # grandstaff
    my_part = load_part("piano-7-octave-visible")
    set_header_key_visibility(
        part_element=my_part,
        set_visibility="invisible"
    )
    assert_xml_equals(
        given=my_part,
        expected=load_part("piano-7-octave")
    )


def test_setting_null_key_to_either_does_nothing():
    # setting invisible (it already is in a way...)
    my_part = load_part("key-0-octave")
    set_header_key_visibility(
        part_element=my_part,
        set_visibility="invisible"
    )
    assert_xml_equals(
        given=my_part,
        expected=load_part("key-0-octave")
    )

    # setting visible (it already is in a way...)
    my_part = load_part("key-0-octave")
    set_header_key_visibility(
        part_element=my_part,
        set_visibility="visible"
    )
    assert_xml_equals(
        given=my_part,
        expected=load_part("key-0-octave")
    )
