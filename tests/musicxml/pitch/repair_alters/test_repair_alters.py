from ....assert_xml_equals import assert_xml_equals
from lmx.musicxml.io.read_musicxml_tree_from_file \
    import read_musicxml_tree_from_file
from lmx.musicxml.pitch.repair_alters import repair_alters
import xml.etree.ElementTree as ET
from pathlib import Path
import copy


def load_part(sample_name: str) -> ET.Element:
    musicxml_tree = read_musicxml_tree_from_file(
        Path(__file__).parent / f"{sample_name}.musicxml"
    )
    return musicxml_tree.find("part")


def strip_and_repair(sample_name: str):
    gold_part = load_part(sample_name)

    stripped_part = copy.deepcopy(gold_part)
    for pitch_element in stripped_part.findall(".//pitch"):
        alter_element = pitch_element.find("alter")
        if alter_element is not None:
            pitch_element.remove(alter_element)
    # TODO: implement cautionaries
    # for accidental_element in stripped_part.findall(".//accidental"):
    #     accidental_element.attrib.pop("cautionary", None)
    #     accidental_element.attrib.pop("parentheses", None)

    # run the repair
    repair_alters(stripped_part)

    assert_xml_equals(
        given=stripped_part, # (stripped and repaired)
        expected=gold_part,
    )


##################
# Test functions #
##################


def test_no_changes_to_nothing():
    strip_and_repair("nothing")


def test_accidentals_produce_alters():
    strip_and_repair("accidentals")


def test_accidentals_are_carried():
    strip_and_repair("doubled-accidentals")


def test_accidentals_are_reset_by_barline():
    strip_and_repair("accidental-reset-by-barline")


def test_accidentals_are_carried_by_ties_across_barlines():
    strip_and_repair("tie-across-barline")


def test_key_signature_produces_alters():
    strip_and_repair("key-signature")


def test_key_signature_produces_cautionaries():
    strip_and_repair("key-signature-with-cautionaries")


def test_repair_works_for_piano_part():
    # in MuseScore, part only has one active key signature for all staves
    # (despite MusicXML allowing different for each; we copy MuseScore)
    strip_and_repair("piano")
