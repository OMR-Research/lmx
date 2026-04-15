from dataclasses import dataclass
import xml.etree.ElementTree as ET


@dataclass
class LayoutMapPart:
    """
    Represents one part in a MusicXML document.
    Used by the MusicXmlLayoutMap to represent parts.
    """

    id: str
    """The XML id attribute value; ID of the part"""

    score_part_element: ET.Element
    """The `<score-part>` element - contains part metadata"""

    part_element: ET.Element
    """The `<part>` element - contains musical content"""

    measure_elements: list[ET.Element]
    """All `<measure>` elements in this part"""

    staff_count: int
    """
    How many staves does this part have (always, across all systems),
    usually 1 or 2, where 2 is for piano parts.
    """

    measure_count: int
    """
    Total number of measures across all pages and systems.
    Should be the same number for all parts. Simply the count
    of `<measure>` elements within the `<part>` element.
    """

    new_systems_at: list[int]
    """
    Measure indexes (0-based) where a new system begins. The first measure
    is not included. The list is extracted directly from the
    `<print new-system="yes">` tags from the XML. A new-page tag is
    also understood as a new-system, even if the new-system attribute
    is not present. New page necessarily starts a new system. This means that
    the new_pages_at list is a subset of new_systems_at list.
    This list should be identical for all parts.
    """

    new_pages_at: list[int]
    """
    Measure indexes (0-based) where a new page begins. The first measure
    is not included. The list is extracted directly from the
    `<print new-page="yes">` tags from the XML.
    This list should be identical for all parts.
    """

    page_count: int
    """
    How many pages does the part have, based on its page breaks.
    This should be the same value for all parts.
    """

    system_count: int
    """
    How many systems does the part have, based on its system breaks.
    This should be the same value for all parts.
    """

    def __post_init__(self):
        assert len(self.id) > 0, "ID may not be empty"
        assert self.score_part_element.tag == "score-part", "Score part element must be a <score-part> element"
        assert self.id == self.score_part_element.attrib["id"]
        assert self.part_element.tag == "part", "Part element must be a <part> element"
        assert self.id == self.part_element.attrib["id"]
        assert all(m.tag == "measure" for m in self.measure_elements)
        assert len(self.measure_elements) == self.measure_count
        assert self.staff_count > 0
        assert self.measure_count > 0
        assert set(self.new_pages_at).issubset(set(self.new_systems_at)), "Parsing error, page breaks should be a subset of system breaks"
        assert self.page_count == len(self.new_pages_at) + 1
        assert self.system_count == len(self.new_systems_at) + 1

    @staticmethod
    def from_elements(
        score_part_element: ET.Element,
        part_element: ET.Element
    ) -> "LayoutMapPart":
        """
        Builds the Part description object from the
        `<score-part>` and `<part>` XML elements
        """
        assert score_part_element.tag == "score-part"
        assert part_element.tag == "part"
        assert score_part_element.attrib["id"] == part_element.attrib["id"]

        # parse out staff count
        staves_elements = part_element.findall("measure/attributes/staves")
        assert len(staves_elements) <= 1, \
            "The part has more than one <staves> element which is not supported"
        staff_count = 1
        if len(staves_elements) > 0:
            staff_count = int(staves_elements[0].text or "0")
        
        # count measures
        measure_elements = part_element.findall("measure")
        measure_count = len(measure_elements)

        # get system and page breaks
        new_systems_at: list[int] = []
        new_pages_at: list[int] = []
        for i, measure_element in enumerate(measure_elements):
            print_element = measure_element.find("print")
            if print_element is None:
                continue

            # page break is also a system break
            if print_element.attrib.get("new-page") == "yes":
                new_pages_at.append(i)
                new_systems_at.append(i)
            elif print_element.attrib.get("new-system") == "yes":
                new_systems_at.append(i)

        return LayoutMapPart(
            id=part_element.attrib["id"],
            score_part_element=score_part_element,
            part_element=part_element,
            measure_elements=measure_elements,
            staff_count=staff_count,
            measure_count=measure_count,
            new_systems_at=new_systems_at,
            new_pages_at=new_pages_at,
            page_count=len(new_pages_at) + 1,
            system_count=len(new_systems_at) + 1,
        )

    def measure_range_for_page(self, page_index: int) -> range:
        """Returns a range of 0-based measure indices
        that are present on a given page, page index is 0-based"""
        assert page_index >= 0 and page_index < self.page_count
        
        # single page only
        if len(self.new_pages_at) == 0:
            return range(0, self.measure_count)
        
        # first page
        if page_index == 0:
            return range(0, self.new_pages_at[0])
        
        # last page
        if page_index == self.page_count - 1:
            return range(self.new_pages_at[-1], self.measure_count)
        
        # middle page
        return range(
            self.new_pages_at[page_index - 1],
            self.new_pages_at[page_index]
        )
    
    def measure_range_for_system(self, global_system_index: int) -> range:
        """Returns a range of 0-based measure indices
        that are present on a given system, system index is 0-based
        and global to the whole document - across all pages"""
        assert global_system_index >= 0 \
            and global_system_index < self.system_count
        
        # single system only
        if len(self.new_systems_at) == 0:
            return range(0, self.measure_count)
        
        # first system
        if global_system_index == 0:
            return range(0, self.new_systems_at[0])
        
        # last system
        if global_system_index == self.system_count - 1:
            return range(self.new_systems_at[-1], self.measure_count)

        # middle system
        return range(
            self.new_systems_at[global_system_index - 1],
            self.new_systems_at[global_system_index]
        )
    
    def system_count_on_page(self, page_index: int) -> int:
        """How many systems there are on a given page"""
        system_count = 1
        for measure_index in self.measure_range_for_page(page_index):
            if measure_index in self.new_systems_at:
                system_count += 1
        return system_count
