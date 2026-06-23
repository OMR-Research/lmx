import xml.etree.ElementTree as ET
from lmx.musicxml.part_to_score import part_to_score


def wrap_part_in_score(part_element: ET.Element) -> ET.ElementTree:
    """Wraps an LMX decoded `<part>` in a `<score-partwise>`
    to make it comparable to ground truth MusicXML files.
    
    This method is intended to be only used in tests,
    as it defines the specific shape of testing musicxml files.
    """
    return part_to_score(
        part=part_element,
        part_id="P1",
        part_name="Piano",
        musicxml_version="4.0",
    )
