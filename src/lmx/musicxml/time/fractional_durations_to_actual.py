import xml.etree.ElementTree as ET
from fractions import Fraction
import math
from ..attributes.get_head_attributes import get_head_attributes
from ..attributes.sort_attributes import sort_attributes


# TODO: refactor to use the new value objects (Duration, MeasureOnset)


def fractional_durations_to_actual(part_element: ET.Element):
    """
    Accepts a `<part>` element with no `<divisions>` element
    and all `<duration>` elements set to Python Fraction values,
    such as `1/2` for eighth notes (half a beat). This method
    creates the `<divisions>` element and changes all
    `<duration>` values to appropriate integers according to the
    MusicXML specification.
    """

    assert part_element.tag == "part"
    
    if len(part_element) == 0:
        return

    # make sure there are no divisions
    divisions_elements = part_element.findall("measure/attributes/divisions")
    assert len(divisions_elements) == 0, \
        "Fractional <part> should contain no <divisions> elements"

    # get all duration values
    duration_values = set(
        Fraction(e.text)
        for e in part_element.iter("duration")
        if e.text is not None # should not happen, but calms down mypy
    )

    # compute divisions
    denominators = [v.denominator for v in duration_values]
    
    # LCM magic algorithm (lowest common denominator)
    if len(denominators) > 0:
        lcm = denominators[0]
        for denominator in denominators[1:]:
            lcm = lcm // math.gcd(lcm, denominator) * denominator
        divisions: int = lcm
    else: # there are only measure rests in the score (no durations)
        divisions: int = 1

    # write divisions element
    first_measure_element = part_element[0]
    attributes_element = get_head_attributes(
        first_measure_element,
        create_if_missing=True
    )
    divisions_element = ET.Element("divisions")
    divisions_element.text = str(divisions)
    attributes_element.append(divisions_element)
    sort_attributes(attributes_element)

    # update all duration elements
    for duration_element in part_element.iter("duration"):
        assert duration_element.text is not None
        duration_value = Fraction(duration_element.text) * divisions
        assert duration_value.denominator == 1
        duration_element.text = str(duration_value.numerator)
