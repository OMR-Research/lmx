import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class Part:
    """Represents one part in a MusicXML document"""

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
    ) -> "Part":
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

        return Part(
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


@dataclass
class StaffLocation:
    """Represents a location of a staff in all various coordinate systems"""
    
    page_index: int
    """What page is this staff part of"""

    global_system_index: int
    """What system is this staff part of (out of all systems in the document)"""

    page_system_index: int
    """What system is this staff part of (out of systems on the page)"""

    part_index: int
    """What part is this staff part of (out of parts in the document)"""

    page_staff_index: int
    """What staff is this within its page"""

    system_staff_index: int
    """What staff is this within its system"""

    part_staff_index: int
    """What staff is this within its part (0 or 1, rarely more)"""




class MusicXmlLayoutMap:
    """
    This is an index that can be built on top of a MusicXML document
    and it provides information about the layout of the music on pages.
    It counts staves, parts, measures, systems and pages as they are
    defined in the MusicXML document. Plus it validates correct number
    of measures per system per part, etc. Treat it as a read-only structure,
    do not modify its fields.
    """

    def __init__(
            self,
            musicxml_tree: ET.ElementTree,
            verify_system_break_support=True,
            verify_page_break_support=True
    ):
        """
        Builds the layout map description and performs heavy validation.

        :param musicxml_tree: The parsed XML tree of the MusicXML document.
        :param verify_system_break_support: Check that the MusicXML document
            specifies that it contains explicit system breaks.
        :param verify_page_break_support: Check that the MusicXML document
            specifies that it contains explicit page breaks.
        """
        
        # === verify given musicxml ===
        
        root = musicxml_tree.getroot()
        
        assert root.tag == "score-partwise", \
            "This code works with <score-partwise> MusicXML documents"

        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/examples/supports-element/
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/supports/
        if verify_system_break_support:
            # NOTE: if you know that your document has explicit system breaks,
            # but the metadata does not state that, you can disable this check
            # by setting verify_system_break_support=False in the constructor
            supports_element = root.find('identification/encoding/supports[@element="print"][@attribute="new-system"][@value="yes"]')
            assert supports_element is not None, "The document does not state whether system breaks are present or not"
            assert supports_element.attrib.get("type") == "yes", "The document does not contain explicit system breaks"
        
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/examples/supports-element/
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/supports/
        if verify_page_break_support:
            # NOTE: if you know that your document has explicit page breaks,
            # but the metadata does not state that, you can disable this check
            # by setting verify_page_break_support=False in the constructor
            supports_element = root.find('identification/encoding/supports[@element="print"][@attribute="new-page"][@value="yes"]')
            assert supports_element is not None, "The document does not state whether page breaks are present or not"
            assert supports_element.attrib.get("type") == "yes", "The document does not contain explicit page breaks"

        # === parse parts ===

        # get <score-part> in document reading order, which
        # is the same order as the parts should are drawn on page.
        score_part_elements = root.findall("part-list/score-part")
        parts: list[Part] = []
        for score_part_element in score_part_elements:
            pid = score_part_element.attrib["id"]
            part_element = root.find(f'part[@id="{pid}"]')
            assert part_element is not None, "Missing <part> with ID: {pid}"
            parts.append(Part.from_elements(
                score_part_element=score_part_element,
                part_element=part_element,
            ))
        
        # === verify cross-part invariants ===

        assert len(parts) > 0, "The document must have at least one <part>"

        first_part = parts[0]
        for part in parts:
            # same counts of things
            assert part.measure_count == first_part.measure_count
            assert part.new_systems_at == first_part.new_systems_at
            assert part.new_pages_at == first_part.new_pages_at
            assert part.system_count == first_part.system_count
            assert part.page_count == first_part.page_count

            # same measures for each system and at least some
            # and they add up to total
            total_measures = 0
            for system_index in range(part.system_count):
                system_measures = len(part.measure_range_for_system(system_index))
                assert system_measures > 0
                assert system_measures == len(first_part.measure_range_for_system(system_index))
                total_measures += system_measures
            assert total_measures == part.measure_count

            # same measures for each page and at least some
            # and they add up to total
            total_measures = 0
            for page_index in range(part.page_count):
                page_measures = len(part.measure_range_for_page(page_index))
                assert page_measures > 0
                assert page_measures == len(first_part.measure_range_for_page(page_index))
                total_measures += page_measures
            assert total_measures == part.measure_count
            
            # systems over pages must add up to total systems
            total_systems = 0
            for page_index in range(part.page_count):
                page_systems = part.system_count_on_page(page_index)
                assert page_systems > 0
                total_systems += page_systems
            assert total_systems == part.system_count
            
        # === populate fields ===
        
        self.musicxml_tree = musicxml_tree
        """The whole MusicXML document"""

        self.parts = parts
        """
        Metadata about individual parts `<part>` and `<score-part>` elements.
        Parts are ordered in the same way they are present on the page top-down.
        """

        self.part_count = len(parts)
        """Number of parts in the document. One part is one instrument,
        but it may be multiple staves (e.g. for piano)."""

        self.measure_count = first_part.measure_count
        """Number of measures in the whole XML document across all pages"""

        self.system_count = first_part.system_count
        """Number of systems in the whole XML document, across all pages"""

        self.page_count = first_part.page_count
        """Number of pages in the document. Determined by the presence
        of explicit new-page instructions: `<print new-page="yes">`"""

        self.staff_count_per_system = sum(
            part.staff_count for part in self.parts
        )
        """Number of staves in a single system"""

    def system_count_on_page(self, page_index: int) -> int:
        """How many systems there are on a given page"""
        return self.parts[0].system_count_on_page(page_index)
    
    def staff_count_on_page(self, page_index: int) -> int:
        """How many staves there are on a given page, across all of its systems"""
        return self.staff_count_per_system \
            * self.system_count_on_page(page_index)

    def locate_staff_from_page_staff_index(
            self,
            page_index: int,
            page_staff_index: int
    ) -> StaffLocation:
        """
        Given a staff on a page, it returns the complete location
        description for the staff.

        :param page_index: Index of the page we're looking at, 0-based.
        :param page_staff_index: Index of the staff out of all staves
            on the page, 0-based.
        """
        # verify the given numbers make sense
        staff_count_on_page = self.staff_count_on_page(page_index)
        assert page_index >= 0 and page_index < staff_count_on_page

        # count systems on previous pages
        systems_before_this_page = 0
        for pi in range(0, page_index):
            systems_before_this_page += self.system_count_on_page(pi)
    
        # locate the system context
        page_system_index = page_staff_index // self.staff_count_per_system
        system_staff_index = page_staff_index % self.staff_count_per_system

        # locate the part context
        def locate_part_context() -> tuple[int, int]:
            _tracked_system_staff_index = -1
            for pi in range(self.part_count):
                for si in range(self.parts[pi].staff_count):
                    _tracked_system_staff_index += 1
                    if _tracked_system_staff_index == system_staff_index:
                        return pi, si
            raise Exception("We should return if invariants hold properly.")
        
        part_index, part_staff_index = locate_part_context()

        return StaffLocation(
            page_index=page_index,
            global_system_index=systems_before_this_page + page_system_index,
            page_system_index=page_system_index,
            part_index=part_index,
            page_staff_index=page_staff_index,
            system_staff_index=system_staff_index,
            part_staff_index=part_staff_index
        )
