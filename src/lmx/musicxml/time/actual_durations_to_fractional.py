import xml.etree.ElementTree as ET
from fractions import Fraction


# TODO: refactor to use the new value objects (Duration, MeasureOnset)


def actual_durations_to_fractional(part_element: ET.Element):
    """
    Goes over the given `<part>` element's contents and replaces
    all `<duration>` elements values with Python Fraction
    values, such as `1/2` for eighth notes (half a beat).
    It also removes all `<divisions>` elements in the process.
    This is useful to de-contextualize duration values for
    further processing.
    """

    assert part_element.tag == "part"
    
    if len(part_element) == 0:
        return
    
    # tracked context
    current_divisions: int | None = None
    
    ############
    # Visitors #
    ############

    def _visit_duration(duration_element: ET.Element):
        nonlocal current_divisions
        if duration_element is None:
            return
        
        assert current_divisions is not None
        assert duration_element.text is not None

        duration_value = Fraction(duration_element.text)
        duration_value = duration_value / current_divisions
        duration_element.text = str(duration_value)
        duration_element.attrib["fractional"] = "yes"
    
    def _visit_notelike(notelike_element: ET.Element):
        duration_element = notelike_element.find("duration")
        assert duration_element is not None, \
            f"The {notelike_element.tag} element should have <duration> child"
        _visit_duration(duration_element)

    def _visit_attributes(attributes_element: ET.Element):
        nonlocal current_divisions
        divisions_element = attributes_element.find("divisions")
        if divisions_element is None:
            return
        assert divisions_element.text is not None
        current_divisions = int(divisions_element.text)
        attributes_element.remove(divisions_element)

    ##########################
    # Iteration over content #
    ##########################

    for measure_element in part_element:
        for element in measure_element:
            if element.tag in {"note", "forward", "backup"}:
                _visit_notelike(element)
            elif element.tag == "attributes":
                _visit_attributes(element)
