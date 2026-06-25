from ....assert_xml_equals import assert_xml_equals
from lmx.musicxml.io.read_musicxml_tree_from_file \
    import read_musicxml_tree_from_file
import xml.etree.ElementTree as ET
from pathlib import Path
from lmx.musicxml.omitted_staff_header.normalize_invisible_header_clef \
    import normalize_invisible_header_clef
from lmx.musicxml.omitted_staff_header.Clef \
    import Clef, G_CLEF, F_CLEF, C_CLEF


def load_part(sample_name: str) -> ET.Element:
    musicxml_tree = read_musicxml_tree_from_file(
        Path(__file__).parent / f"{sample_name}.musicxml"
    )
    return musicxml_tree.find("part")


def normalize(given_sample: str, desired_clef: Clef, expected_sample: str):
    assert_xml_equals(
        given=normalize_invisible_header_clef(
            part_element=load_part(given_sample),
            desired_clef=desired_clef,
            when_clef_visible="raise-exception",
        ),
        expected=load_part(expected_sample)
    )


class TestClefOmissionNormalization:
    def test_plain_note_transposition(self):
        normalize("g-clef-octave", F_CLEF, "f-clef-octave")
        normalize("g-clef-octave", C_CLEF, "c-clef-octave")
        normalize("f-clef-octave", G_CLEF, "g-clef-octave")
        normalize("c-clef-octave", G_CLEF, "g-clef-octave")
        normalize("f-clef-octave", C_CLEF, "c-clef-octave")
        normalize("c-clef-octave", F_CLEF, "f-clef-octave")
    
    def test_accidental_note_transposition(self):
        normalize("g-clef-octave-sharped", F_CLEF, "f-clef-octave-sharped")
        normalize("f-clef-octave-sharped", G_CLEF, "g-clef-octave-sharped")

    def test_doubled_accidental_note_transposition(self):
        normalize(
            "g-clef-octave-sharped-and-doubled",
            F_CLEF,
            "f-clef-octave-sharped-and-doubled"
        )
        normalize(
            "f-clef-octave-sharped-and-doubled",
            G_CLEF,
            "g-clef-octave-sharped-and-doubled"
        )
    
    def test_transposition_until_clef_change(self):
        normalize(
            "g-clef-with-change",
            F_CLEF,
            "f-clef-with-change"
        )
        normalize(
            "f-clef-with-change",
            G_CLEF,
            "g-clef-with-change"
        )

    def test_piano_normalization(self):
        normalize(
            "cc-piano-octave",
            [G_CLEF, F_CLEF],
            "gf-piano-octave"
        )
        normalize(
            "gf-piano-octave",
            [C_CLEF, C_CLEF],
            "cc-piano-octave"
        )
    
    def test_piano_with_changes_normalization(self):
        normalize(
            "cc-piano-with-changes",
            [G_CLEF, F_CLEF],
            "gf-piano-with-changes"
        )
        normalize(
            "gf-piano-with-changes",
            [C_CLEF, C_CLEF],
            "cc-piano-with-changes"
        )

    # TODO: test header visibility forcing (setting)

    # TODO: test behavior with unexpected visible clefs
    # - exception
    # - normalize
    # - do nothing

    # TODO: test exception on new invisible clef
