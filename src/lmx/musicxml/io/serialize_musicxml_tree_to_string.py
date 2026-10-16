import xml.dom.minidom
import xml.etree.ElementTree as ET


def serialize_musicxml_tree_to_string(
        musicxml_tree: ET.ElementTree,
        pretty=False,
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

    # pretty-print
    if pretty:
        dom = xml.dom.minidom.parseString(musicxml_string)
        musicxml_string = str(dom.toprettyxml(indent="  ", encoding="utf-8"), "utf-8")

    return musicxml_string
