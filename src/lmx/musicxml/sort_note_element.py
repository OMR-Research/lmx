import xml.etree.ElementTree as ET


def sort_note_element(note_element: ET.Element):
    """Sorts children in a `<note>` element"""
    assert note_element.tag == "note", \
        "The given element is not a <note> element"
    tag_order = [
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/note/
        
        # compressed head
        "grace",
        "cue",
        "chord",
        "pitch", "unpitched", "rest",
        "duration",
        "tie",

        # tail
        "instrument",
        "footnote", "level", "voice",
        "type",
        "dot",
        "accidental",
        "time-modification",
        "stem",
        "notehead",
        "notehead-text",
        "staff",
        "beam",
        "notations",
        "lyric",
        "play",
        "listen",
    ]
    note_element[:] = sorted(
        note_element,
        key=lambda e: tag_order.index(e.tag)
    )
