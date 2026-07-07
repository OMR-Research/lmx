from ....assert_xml_equals import assert_xml_equals
from lmx.musicxml.io.read_musicxml_tree_from_file \
    import read_musicxml_tree_from_file
import xml.etree.ElementTree as ET
from pathlib import Path
from lmx.musicxml.omitted_staff_header.normalize_invisible_time_signature \
    import normalize_invisible_time_signature
from typing import Literal
import pytest


TIME_44 = ET.fromstring(
    "<time><beats>4</beats><beat-type>4</beat-type></time>"
)
TIME_34 = ET.fromstring(
    "<time><beats>3</beats><beat-type>4</beat-type></time>"
)
TIME_68 = ET.fromstring(
    "<time><beats>6</beats><beat-type>8</beat-type></time>"
)


def load_part(sample_name: str) -> ET.Element:
    musicxml_tree = read_musicxml_tree_from_file(
        Path(__file__).parent / f"{sample_name}.musicxml"
    )
    return musicxml_tree.find("part")


def normalize(
        given_sample: str,
        desired_time: ET.Element | None,
        expected_sample: str,
        when_time_visible: Literal[
            "dont-normalize", "raise-exception"
        ] = "raise-exception",
):
    assert_xml_equals(
        given=normalize_invisible_time_signature(
            part_element=load_part(given_sample),
            desired_time=desired_time,
            when_time_visible=when_time_visible,
        ),
        expected=load_part(expected_sample)
    )


######################
# Ordinary behaviour #
######################

def test_plain_time_replacement():
    normalize("time-44-octave-4", None, "time-none-octave-4")
    normalize("time-34-octave-3", None, "time-none-octave-3")
    normalize("time-68-octave-3", None, "time-none-octave-3")
    
    normalize("time-none-octave-4", TIME_44, "time-44-octave-4")
    normalize("time-none-octave-3", TIME_34, "time-34-octave-3")
    normalize("time-none-octave-3", TIME_68, "time-68-octave-3")

    normalize("time-34-octave-3", TIME_68, "time-68-octave-3")
    normalize("time-68-octave-3", TIME_34, "time-34-octave-3")


def test_piano_time_replacement():
    normalize("piano-34-octave-3", None, "piano-none-octave-3")
    normalize("piano-68-octave-3", None, "piano-none-octave-3")
    
    normalize("piano-none-octave-3", TIME_34, "piano-34-octave-3")
    normalize("piano-none-octave-3", TIME_68, "piano-68-octave-3")

    normalize("piano-34-octave-3", TIME_68, "piano-68-octave-3")
    normalize("piano-68-octave-3", TIME_34, "piano-34-octave-3")


##############################
# Unexpected input behaviour #
##############################


def test_normalizing_visible_time_should_not_normalize():
    normalize(
        "time-44-octave-4-visible",
        None,
        "time-44-octave-4-visible",
        when_time_visible="dont-normalize"
    )


def test_normalizing_visible_time_should_raise():
    with pytest.raises(ValueError, match="this function expects header time to be invisible"):
        normalize(
            "time-44-octave-4-visible",
            None,
            "time-44-octave-4-visible",
            when_time_visible="raise-exception"
        )


def test_normalization_raises_on_invisible_time_change():
    with pytest.raises(ValueError, match="Invisible time signatures are only allowed at onset 0"):
        normalize_invisible_time_signature(
            load_part("time-44-octave-4-with-invisible-change"),
            None,
            when_time_visible="raise-exception",
        )
