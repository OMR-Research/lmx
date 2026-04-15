from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
import copy
from .attributes.sort_attributes import sort_attributes
from .attributes.get_head_attributes import get_head_attributes


def slice_part_to_systems(
    part_element: ET.Element,
    emit_attributes_header=True,
    attributes_to_emit=["divisions", "key", "staves", "clef"],
    remove_page_and_system_breaks=True
) -> list["PageSlice"]:
    """
    Slices a MusicXML `<part>` element up into multiple `<part>` elements by
    system breaks and page breaks. It returns a list of pages, each
    containing a list of systems.

    part_element: Element
        The input `<part>` XML element
    
    emit_attributes_header: bool
        When true, the `<attributes>` element is added to the
        start of each system after splitting to make the resulting
        measures a valid MusicXML part.
    
    emit_attributes: list
        What `<attributes>` children to re-emit with each new system.
        The default contains clefs and key signature, which is typically
        present on each system in the music notation. It also contains
        divisions and staves, which is metadata useful for MusicXML completeness.
    
    remove_page_and_system_breaks: bool
        When true, the page and system breaks on the measures are removed.
    """
    assert part_element.tag == "part"
    part_id = part_element.get("id", None)

    pages: list[PageSlice] = [PageSlice()]
    page = pages[0]

    system = SystemSlice(part_id)
    page.append_system(system)

    tracked_attributes = TrackedAttributes()
    
    for original_measure_element in part_element:
        # make a copy so that we dont't modify the original
        measure_element = copy.deepcopy(original_measure_element)

        # detect page and system breaks
        new_system_measure = False
        print_element = measure_element.find("print")
        if print_element is not None:
            if print_element.get("new-system") == "yes":
                if remove_page_and_system_breaks:
                    del print_element.attrib["new-system"]
                system = SystemSlice(part_id)
                page.append_system(system)
                new_system_measure = True
            elif print_element.get("new-page") == "yes":
                if remove_page_and_system_breaks:
                    del print_element.attrib["new-page"]
                page = PageSlice()
                pages.append(page)
                system = SystemSlice(part_id)
                page.append_system(system)
                new_system_measure = True
        
        # remove an empty print element
        if remove_page_and_system_breaks and print_element is not None:
            if len(print_element) == 0 and len(print_element.attrib) == 0:
                measure_element.remove(print_element)
        
        # emit the head attributes element
        head_attributes = get_head_attributes(
            measure_element,
            create_if_missing=False
        )
        if head_attributes is not None:
            tracked_attributes.update_with(head_attributes)
        if emit_attributes_header and new_system_measure \
                and not tracked_attributes.is_empty():
            head_attributes = get_head_attributes(
                measure_element,
                create_if_missing=True
            )
            _emit_header(
                tracked_attributes=tracked_attributes,
                attributes=head_attributes,
                attributes_to_emit=attributes_to_emit
            )
        for attributes_element in measure_element.iterfind("attributes"):
            tracked_attributes.update_with(attributes_element)

        # the measure is processed
        system.append_measure(measure_element)

    return pages


class SystemSlice:
    """Represents one system of a `<part>` that was sliced up into systems"""
    def __init__(self, part_id: str | None):
        self.part = ET.Element("part")
        if part_id is not None:
            self.part.attrib["id"] = part_id
    
    def append_measure(self, measure: ET.Element):
        assert measure.tag == "measure"
        self.part.append(measure)


class PageSlice:
    """Represents one page of a `<part>` that was sliced up into systems"""
    def __init__(self) -> None:
        self.systems: list[SystemSlice] = []
    
    def append_system(self, system: SystemSlice):
        self.systems.append(system)


@dataclass
class TrackedAttributes:
    """
    Tracked context of `<attributes>` that are re-emitted
    for each slice, when slicing a `<part>` into
    individual systems
    """
    divisions: ET.Element | None = None
    key: ET.Element | None = None
    time: ET.Element | None = None
    staves: ET.Element | None = None
    clef: dict[int, ET.Element] = field(default_factory=dict)

    def update_with(self, attributes_element: ET.Element):
        """
        Updates tracked `<attributes>` based on the just
        encountered `<attributes>` element
        """
        # divisions
        divisions_element = attributes_element.find("divisions")
        if divisions_element is not None:
            self.divisions = divisions_element
        
        # key
        key_element = attributes_element.find("key")
        if key_element is not None:
            self.key = key_element
        
        # time
        time_element = attributes_element.find("time")
        if time_element is not None:
            self.time = time_element
        
        # staves
        staves_element = attributes_element.find("staves")
        if staves_element is not None:
            staves = int(staves_element.text or "1")
            assert staves > 0
            self.staves = staves_element
            clefs_to_clear = [
                s for s in self.clef.keys()
                if s > staves
            ]
            for s in clefs_to_clear:
                del self.clef[s]

        # clef
        for clef_element in attributes_element.findall("clef"):
            staff = int(clef_element.get("number", 1))
            assert staff > 0
            self.clef[staff] = clef_element
    
    def is_empty(self) -> bool:
        """Returns true if nothing is tracked so far"""
        if self.divisions is not None:
            return False
        if self.key is not None:
            return False
        if self.time is not None:
            return False
        if self.staves is not None:
            return False
        if len(self.clef) > 0:
            return False
        return True


def _emit_header(
        tracked_attributes: TrackedAttributes,
        attributes: ET.Element,
        attributes_to_emit: list[str]
):
    # divisions
    if "divisions" in attributes_to_emit:
        divisions_element = attributes.find("divisions")
        if divisions_element is None and tracked_attributes.divisions is not None:
            attributes.append(
                copy.deepcopy(tracked_attributes.divisions)
            )
    
    # key
    if "key" in attributes_to_emit:
        key_element = attributes.find("key")
        if key_element is None and tracked_attributes.key is not None:
            attributes.append(
                copy.deepcopy(tracked_attributes.key)
            )
    
    # time
    if "time" in attributes_to_emit:
        time_element = attributes.find("time")
        if time_element is None and tracked_attributes.time is not None:
            attributes.append(
                copy.deepcopy(tracked_attributes.time)
            )
    
    # staves
    if "staves" in attributes_to_emit:
        staves_element = attributes.find("staves")
        if staves_element is None and tracked_attributes.staves is not None:
            attributes.append(
                copy.deepcopy(tracked_attributes.staves)
            )
    
    # clef
    if "clef" in attributes_to_emit:
        for number in sorted(tracked_attributes.clef.keys()):
            try:
                _ = next(
                    e for e in attributes.iterfind("clef")
                    if e.get("number", "1") == str(number)
                )
            except StopIteration:
                # the clef element is not present, add it
                attributes.append(
                    copy.deepcopy(tracked_attributes.clef[number])
                )
    
    sort_attributes(attributes)
