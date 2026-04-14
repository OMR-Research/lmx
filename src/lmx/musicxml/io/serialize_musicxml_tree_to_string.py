import xml.etree.ElementTree as ET


def serialize_musicxml_tree_to_string(
        musicxml_tree: ET.ElementTree
) -> str:
    """Serializes a given MusicXML ElementTree to a string"""
    assert musicxml_tree.getroot().tag == "score-partwise", \
        "Given XML ElementTree is not MusicXML"
    
    musicxml_stream = ET.tostring(
        musicxml_tree.getroot(),
        encoding="utf-8",
        xml_declaration=True
    )
    
    musicxml_string = str(musicxml_stream, "utf-8")

    return musicxml_string
