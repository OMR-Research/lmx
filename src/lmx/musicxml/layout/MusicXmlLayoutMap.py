import xml.etree.ElementTree as ET
from .StaffLocation import StaffLocation
from .LayoutMapPart import LayoutMapPart


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
        parts: list[LayoutMapPart] = []
        for score_part_element in score_part_elements:
            pid = score_part_element.attrib["id"]
            part_element = root.find(f'part[@id="{pid}"]')
            assert part_element is not None, "Missing <part> with ID: {pid}"
            parts.append(LayoutMapPart.from_elements(
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
