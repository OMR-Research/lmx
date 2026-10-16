import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from lmx.musicxml.grandstaff.unzip_grandstaff import (
    ContainsTruePianoformMusicException,
    unzip_grandstaff,
)
from lmx.musicxml.grandstaff.zip_grandstaff import zip_grandstaff
from lmx.musicxml.io.read_musicxml_tree_from_file import read_musicxml_tree_from_file

from ...assert_xml_equals import assert_xml_equals


def load_part(sample_name: str) -> ET.Element:
    musicxml_tree = read_musicxml_tree_from_file(
        Path(__file__).parent / f"{sample_name}.musicxml"
    )
    return musicxml_tree.find("part")


def zipg(given_sample: str, strict=True):
    assert_xml_equals(
        given=zip_grandstaff(
            upper_part=load_part(given_sample + "-a"),
            lower_part=load_part(given_sample + "-b"),
            output_part_id="P1",
            strict=strict
        ),
        expected=load_part(given_sample)
    )


def unzipg(given_sample: str, force_split=False, strict=True):
    upper_part, lower_part = unzip_grandstaff(
        piano_part=load_part(given_sample),
        upper_part_id="P1",
        lower_part_id="P1",
        force_split=force_split,
        strict=strict
    )
    assert_xml_equals(
        given=upper_part,
        expected=load_part(given_sample + "-a")
    )
    assert_xml_equals(
        given=lower_part,
        expected=load_part(given_sample + "-b")
    )


######################
# Ordinary behaviour #
######################

def test_simple_music():
    zipg("simple-music")
    unzipg("simple-music")

def test_complex_music():
    # also tests different divisions for each staff
    zipg("complex-music")
    unzipg("complex-music")

def test_multiple_systems():
    zipg("multiple-systems")
    unzipg("multiple-systems")

def test_clef_change():
    zipg("clef-change")
    unzipg("clef-change")


##############################
# Unexpected input behaviour #
##############################

def test_true_pianoform_raises():
    with pytest.raises(ContainsTruePianoformMusicException):
        unzipg("true-pianoform")
