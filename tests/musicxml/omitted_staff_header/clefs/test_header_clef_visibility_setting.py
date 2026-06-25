from lmx.musicxml.omitted_staff_header.set_header_clef_visibility \
    import set_header_clef_visibility
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


class TestHeaderClefVisibilitySetting:
    def test_header_clefs_can_be_set_to_visible(self):
        # solo staff
        my_part = load_part("f-clef-octave")
        set_header_clef_visibility(
            part_element=my_part,
            set_visibility="visible"
        )
        assert_xml_equals(
            given=my_part,
            expected=load_part("f-clef-octave-visible")
        )

        # grandstaff
        my_part = load_part("gf-piano-octave")
        set_header_clef_visibility(
            part_element=my_part,
            set_visibility="visible"
        )
        assert_xml_equals(
            given=my_part,
            expected=load_part("gf-piano-octave-visible-both")
        )

        # grandstaff second
        my_part = load_part("gf-piano-octave-visible-g")
        set_header_clef_visibility(
            part_element=my_part,
            set_visibility="visible"
        )
        assert_xml_equals(
            given=my_part,
            expected=load_part("gf-piano-octave-visible-both")
        )
    
    def test_header_clefs_can_be_set_to_invisible(self):
        # solo staff
        my_part = load_part("f-clef-octave-visible")
        set_header_clef_visibility(
            part_element=my_part,
            set_visibility="invisible"
        )
        assert_xml_equals(
            given=my_part,
            expected=load_part("f-clef-octave")
        )

        # grandstaff
        my_part = load_part("gf-piano-octave-visible-both")
        set_header_clef_visibility(
            part_element=my_part,
            set_visibility="invisible"
        )
        assert_xml_equals(
            given=my_part,
            expected=load_part("gf-piano-octave")
        )

        # grandstaff second
        my_part = load_part("gf-piano-octave-visible-g")
        set_header_clef_visibility(
            part_element=my_part,
            set_visibility="invisible"
        )
        assert_xml_equals(
            given=my_part,
            expected=load_part("gf-piano-octave")
        )
