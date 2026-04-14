import xml.etree.ElementTree as ET


def parse_musicxml_tree_from_string(
        musicxml_string: str
) -> ET.ElementTree:
    """Given a MusicXML string, it parses out the ElementTree and returns it."""
    musicxml_tree = ET.ElementTree(ET.fromstring(musicxml_string))
    
    assert musicxml_tree.getroot().tag == "score-partwise", \
        "Given XML string is not MusicXML"
    
    return musicxml_tree
