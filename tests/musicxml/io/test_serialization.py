import xml.etree.ElementTree as ET

from lmx.musicxml.io.serialize_musicxml_tree_to_string import serialize_musicxml_tree_to_string


def generate_musicxml_tree() -> ET.ElementTree:
    score = ET.Element("score-partwise", {"version": "4.0"})
    
    score.append(part := ET.Element("part", {"id": "P1"}))

    part.append(measure := ET.Element("measure", {"number": "1"}))

    measure.append(note := ET.Element("note"))
    
    note.append(duration := ET.Element("duration"))
    duration.text = "4"

    note.append(type := ET.Element("type"))
    type.text = "whole"

    return ET.ElementTree(score)

def test_plain_serialization():
    musicxml_tree = generate_musicxml_tree()
    xml_string = serialize_musicxml_tree_to_string(musicxml_tree)
    assert xml_string == (
        "<?xml version='1.0' encoding='utf-8'?>\n" +
        '<score-partwise version="4.0">' +
        '<part id="P1">' +
        '<measure number="1">' +
        '<note>' +
        '<duration>4</duration>' +
        '<type>whole</type>' +
        '</note>' +
        '</measure>' +
        '</part>' +
        '</score-partwise>'
    )

def test_pretty_serialization():
    musicxml_tree = generate_musicxml_tree()
    xml_string = serialize_musicxml_tree_to_string(musicxml_tree, pretty=True)
    assert xml_string == (
        '<?xml version="1.0" encoding="utf-8"?>\n' +
        '<score-partwise version="4.0">\n' +
        '  <part id="P1">\n' +
        '    <measure number="1">\n' +
        '      <note>\n' +
        '        <duration>4</duration>\n' +
        '        <type>whole</type>\n' +
        '      </note>\n' +
        '    </measure>\n' +
        '  </part>\n' +
        '</score-partwise>\n'
    )
