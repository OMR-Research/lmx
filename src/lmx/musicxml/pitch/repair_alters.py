import xml.etree.ElementTree as ET
from .PitchAlternator import PitchAlternator


def repair_alters(
        part_element: ET.Element,
        repair_cautionaries=True,
) -> None:
    """Sets pitch `<alter>` values to match the visual `<accidental>` values,
    while respecting key signatures and other complications.
    
    MusicXML encodes both visual (`<accidental>`) and semantic
    (`<alter>`) data. In a correct document, these two layers are in sync.
    However, often times during MusicXML processing, we might get them
    out of sync. Especially in LMX where we put stress on visual appearance.
    This method takes all the visual data and repairs the semantic data
    corresponding to pitch alters and accidentals to match. This is needed,
    because while we focus on visual and ignore semantic in LMX,
    MuseScore does the opposite - parsing semantic and mostly ignoring
    visual. Therefore to make out MusicXML documents readable by MuseScore,
    we need to get these two representation layers in sync.

    This method sets `<alter>` values on all notes of a `<part>`,
    plus it sets `<accidental>` attribute `cautionary="yes"` accordingly.

    This method modifies the given `<part>` element in-place.
    If you need to preserve it, pass in a copy via copy.deepcopy(...).

    :param part_element: The `<part>` element whoose contents to repair.
    :param repair_cautionaries: Whether the fuction should repair
        the accidental cautionary attribute as well.
    """

    if part_element.tag != "part":
        raise ValueError("The given MusicXML element is not a <part>")

    pa = PitchAlternator()
    for measure_element in part_element:
        pa.process_measure(measure_element)
