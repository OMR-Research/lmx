from lmx.musicxml.io.read_musicxml_tree_from_file \
    import read_musicxml_tree_from_file
from lmx.musicxml.time.OnsetVisitor import OnsetVisitor
from lmx.musicxml.time.PartOnset import PartOnset
from lmx.musicxml.time.MeasureOnset import MeasureOnset
from lmx.musicxml.time.ActualDuration import ActualDuration
from lmx.musicxml.time.find_divisions import find_divisions
import xml.etree.ElementTree as ET
from pathlib import Path
import pytest


def load_part(sample_name: str) -> ET.Element:
    musicxml_tree = read_musicxml_tree_from_file(
        Path(__file__).parent / f"{sample_name}.musicxml"
    )
    return musicxml_tree.find("part")


def test_onset_recording():
    # load input sample
    part_element = load_part("basic-sample")
    divisions = find_divisions(part_element)
    assert divisions is not None
    
    # run the visitor
    visitor = OnsetVisitor(record_onsets=True)
    visitor.run(part_element)

    # locate key landmarks
    clef_change_attributes = part_element.find(
        "measure/attributes[2]" # second attributes
    )
    first_half_note = part_element.find(
        "measure/note[type='half']"
    )

    # assert ladmark onsets
    assert visitor.onset_of(clef_change_attributes) == PartOnset(
        measure_index=0,
        measure_onset=MeasureOnset(ActualDuration(3, divisions))
    )
    assert visitor.onset_of(first_half_note) == PartOnset(
        measure_index=1,
        measure_onset=MeasureOnset(ActualDuration(0, divisions))
    )

    # unknown element is not recorded and raises when queried
    with pytest.raises(KeyError):
        visitor.onset_of(ET.Element("note"))


def test_custom_visitor():
    # Goal: count notes past a given onset
    
    # load input sample
    part_element = load_part("basic-sample")
    divisions = find_divisions(part_element)
    assert divisions is not None

    # define threshold (middle of the second measure)
    onset_threshold = PartOnset(
        measure_index=1,
        measure_onset=MeasureOnset(ActualDuration(2, divisions)),
    )

    # define custom visitor
    class MyVisitor(OnsetVisitor):
        def __init__(self):
            super().__init__(record_onsets=False)
            
            self.notes_past_threshold = 0 # custom state (counter)
        
        def visit_note(self, note_element: ET.Element):
            nonlocal onset_threshold
            if self.part_onset >= onset_threshold:
                self.notes_past_threshold += 1 # increment

    # run the visitor
    visitor = MyVisitor()
    visitor.run(part_element)

    # assert results
    assert visitor.notes_past_threshold == 5
