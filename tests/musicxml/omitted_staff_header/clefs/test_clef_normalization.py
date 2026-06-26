from ....assert_xml_equals import assert_xml_equals
from lmx.musicxml.io.read_musicxml_tree_from_file \
    import read_musicxml_tree_from_file
import xml.etree.ElementTree as ET
from pathlib import Path
from lmx.musicxml.omitted_staff_header.normalize_invisible_header_clef \
    import normalize_invisible_header_clef
from lmx.musicxml.omitted_staff_header.Clef \
    import Clef, G_CLEF, F_CLEF, C_CLEF
from typing import Literal
import pytest


def load_part(sample_name: str) -> ET.Element:
    musicxml_tree = read_musicxml_tree_from_file(
        Path(__file__).parent / f"{sample_name}.musicxml"
    )
    return musicxml_tree.find("part")


def normalize(
        given_sample: str,
        desired_clef: Clef,
        expected_sample: str,
        when_clef_visible: Literal[
            "dont-normalize", "normalize-keep-visible",
            "normalize-set-invisible", "raise-exception"
        ] = "raise-exception",
):
    assert_xml_equals(
        given=normalize_invisible_header_clef(
            part_element=load_part(given_sample),
            desired_clef=desired_clef,
            when_clef_visible=when_clef_visible,
        ),
        expected=load_part(expected_sample)
    )


######################
# Ordinary behaviour #
######################

def test_plain_note_transposition():
    normalize("g-clef-octave", F_CLEF, "f-clef-octave")
    normalize("g-clef-octave", C_CLEF, "c-clef-octave")
    normalize("f-clef-octave", G_CLEF, "g-clef-octave")
    normalize("c-clef-octave", G_CLEF, "g-clef-octave")
    normalize("f-clef-octave", C_CLEF, "c-clef-octave")
    normalize("c-clef-octave", F_CLEF, "f-clef-octave")

def test_accidental_note_transposition():
    normalize("g-clef-octave-sharped", F_CLEF, "f-clef-octave-sharped")
    normalize("f-clef-octave-sharped", G_CLEF, "g-clef-octave-sharped")

def test_doubled_accidental_note_transposition():
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

def test_transposition_until_clef_change():
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

def test_piano_normalization():
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

def test_piano_with_changes_normalization():
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

def test_normalization_for_complex_onset():
    # onset calculation is complicated for chords
    # and may throw off transposed span to a clef change
    normalize(
        "f-clef-complex-onset",
        G_CLEF,
        "g-clef-complex-onset"
    )
    normalize(
        "g-clef-complex-onset",
        F_CLEF,
        "f-clef-complex-onset"
    )

##############################
# Unexpected input behaviour #
##############################

def test_normalizing_visible_clef_should_not_normalize():
    normalize(
        "g-clef-octave-visible",
        F_CLEF,
        "g-clef-octave-visible",
        when_clef_visible="dont-normalize"
    )
    normalize(
        "cf-piano-octave-visible-c",
        [G_CLEF, F_CLEF],
        "cf-piano-octave-visible-c",
        when_clef_visible="dont-normalize"
    )

def test_normalizing_visible_clef_should_keep_visible():
    normalize(
        "g-clef-octave-visible",
        F_CLEF,
        "f-clef-octave-visible",
        when_clef_visible="normalize-keep-visible"
    )
    normalize(
        "cf-piano-octave-visible-c",
        [G_CLEF, F_CLEF],
        "gf-piano-octave-visible-g",
        when_clef_visible="normalize-keep-visible"
    )

def test_normalizing_visible_clef_should_set_invisible():
    normalize(
        "g-clef-octave-visible",
        F_CLEF,
        "f-clef-octave",
        when_clef_visible="normalize-set-invisible"
    )
    normalize(
        "cf-piano-octave-visible-c",
        [G_CLEF, F_CLEF],
        "gf-piano-octave",
        when_clef_visible="normalize-set-invisible"
    )

def test_normalizing_visible_clef_should_raise():
    with pytest.raises(ValueError, match="this method expects header clefs to be invisible"):
        normalize_invisible_header_clef(
            part_element=load_part("g-clef-octave-visible"),
            desired_clef=F_CLEF,
            when_clef_visible="raise-exception",
        )
    
    with pytest.raises(ValueError, match="this method expects header clefs to be invisible"):
        normalize_invisible_header_clef(
            part_element=load_part("cf-piano-octave-visible-c"),
            desired_clef=[G_CLEF, F_CLEF],
            when_clef_visible="raise-exception",
        )

def test_normalization_raises_on_invisible_clef_change():
    with pytest.raises(ValueError, match="Invisible clefs are only allowed at onset 0"):
        normalize_invisible_header_clef(
            part_element=load_part("g-clef-with-invisible-change"),
            desired_clef=F_CLEF,
            when_clef_visible="raise-exception",
        )
