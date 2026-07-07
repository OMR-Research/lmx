from ....assert_xml_equals import assert_xml_equals
from lmx.musicxml.io.read_musicxml_tree_from_file \
    import read_musicxml_tree_from_file
import xml.etree.ElementTree as ET
from pathlib import Path
from lmx.musicxml.omitted_staff_header.normalize_invisible_key_signature \
    import normalize_invisible_key_signature
from typing import Literal
import pytest


def load_part(sample_name: str) -> ET.Element:
    musicxml_tree = read_musicxml_tree_from_file(
        Path(__file__).parent / f"{sample_name}.musicxml"
    )
    return musicxml_tree.find("part")


def normalize(
        given_sample: str,
        desired_key: int,
        expected_sample: str,
        when_key_visible: Literal[
            "dont-normalize", "raise-exception"
        ] = "raise-exception",
):
    assert_xml_equals(
        given=normalize_invisible_key_signature(
            part_element=load_part(given_sample),
            desired_key=desired_key,
            when_key_visible=when_key_visible,
        ),
        expected=load_part(expected_sample)
    )


######################
# Ordinary behaviour #
######################

def test_plain_note_transposition():
    normalize("key-3-octave", 7, "key-7-octave")
    normalize("key-3-octave", -7, "key-b7-octave")
    normalize("key-3-octave", 0, "key-0-octave")
    normalize("key-7-octave", 0, "key-0-octave")
    normalize("key-b7-octave", 0, "key-0-octave")


def test_accidental_note_transposition():
    normalize("key-7-accidentals", 0, "key-0-accidentals")
    normalize("key-0-accidentals", 7, "key-7-accidentals")


def test_transposition_until_key_change():
    normalize("key-7-octave-with-change", 0, "key-0-octave-with-change")
    normalize("key-0-octave-with-change", 7, "key-7-octave-with-change")


def test_piano_normalization():
    normalize("piano-7-octave", 0, "piano-0-octave")
    normalize("piano-0-octave", 7, "piano-7-octave")


def test_piano_with_change_normalization():
    normalize("piano-7-octave-with-change", 0, "piano-0-octave-with-change")
    normalize("piano-0-octave-with-change", 7, "piano-7-octave-with-change")


##############################
# Unexpected input behaviour #
##############################


def test_normalizing_visible_key_should_not_normalize():
    normalize(
        "piano-7-octave-visible",
        0,
        "piano-7-octave-visible",
        when_key_visible="dont-normalize"
    )


def test_normalizing_visible_key_should_raise():
    with pytest.raises(ValueError, match="this function expects header key to be invisible"):
        normalize(
            "piano-7-octave-visible",
            0,
            "piano-7-octave-visible",
            when_key_visible="raise-exception"
        )


def test_normalization_raises_on_invisible_key_change():
    with pytest.raises(ValueError, match="Invisible keys are only allowed at onset 0"):
        normalize_invisible_key_signature(
            load_part("piano-7-octave-with-invisible-change"),
            0,
            when_key_visible="raise-exception",
        )
