from .MusicXmlLayoutMap import MusicXmlLayoutMap
import xml.etree.ElementTree as ET
from ..split_part_to_systems import split_part_to_systems, \
    Page, System


def extract_part_system(
        layout_map: MusicXmlLayoutMap,
        part_index: int,
        page_index: int,
        page_system_index: int
) -> ET.Element:
    """
    Extracts out one part-system out of a given `<part>`
    of a MusicXML document and returns it as a new `<part>`.
    """
    source_part = layout_map.parts[part_index]

    # split the source part into pages and systems
    # and get the slice we're interested in
    pages: list[Page] = split_part_to_systems(
        part=source_part.part_element,
        emit_attributes_header=True,
        attributes_to_emit=["divisions", "key", "staves", "clef"],
        remove_page_and_system_breaks=True
    )
    assert len(pages) == layout_map.page_count

    page = pages[page_index]
    assert len(page.systems) == layout_map.system_count_on_page(
        page_index
    )

    system: System = page.systems[page_system_index]
    return system.part
