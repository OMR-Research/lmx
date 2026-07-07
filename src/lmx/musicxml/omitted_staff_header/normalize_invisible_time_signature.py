import copy
from typing import Literal
import xml.etree.ElementTree as ET
from ..time.OnsetVisitor import OnsetVisitor
from ..attributes.sort_attributes import sort_attributes


def normalize_invisible_time_signature(
        part_element: ET.Element,
        desired_time: ET.Element | None,
        when_time_visible: Literal[
            "dont-normalize",
            "raise-exception",
        ],
) -> ET.Element:
    """
    Takes in a `<part>` element with invisible header time signature
    and changes that signature to the desired time signature.
    Missing time signature is ok and is represented by None.
    While MusicXML supports per-staff times, MuseScore does not
    and we primarily target MuseScore. If the <part> contains
    invisible time signature anywhere other than the head (onset zero),
    an exception is raised. Visible time signatures are ok.

    This method creates a copy of the part element and returns that
    modified copy. The input part element is left unmodified.

    :param part_element: The `<part>` MusicXML element to be normalized.
    :param desired_time: The `<time>` element that should replace
        the existing invisible time. It's `print-object="no"` attribute
        will be set if not provided. None means the `<time>` element 
        will be removed, instead of replaced.
    :param when_time_visible: Specifies how to behave, when the
        header time is visible (which is unexpected). Select behaviour
        that best matches your usecase.
    """
    assert desired_time is None or desired_time.tag == "time"

    # create a copy of the input before we start modifying it
    part_element = copy.deepcopy(part_element)

    class MyVisitor(OnsetVisitor):
        def __init__(self):
            super().__init__(record_onsets=False)
        
        def visit_attributes(self, attributes_element: ET.Element):
            is_header_attributes = self.part_onset == 0

            # for header attributes, remove all <time> tags and
            # then optionally re-insert them
            if is_header_attributes:
                # remove them (and check they are invisible)
                for time_element in attributes_element.findall("time"):
                    # the <time> element should NOT have a staff number
                    if "number" in time_element.attrib:
                        raise ValueError(
                            "This function supports only full-part time signatures, " +
                            "not per-staff time signatures."
                        )
                    
                    # handle visible header times
                    if not time_element.attrib.get("print-object", "yes") == "no":
                        if when_time_visible == "dont-normalize":
                            return # skip normalization for these header attributes
                        elif when_time_visible == "raise-exception":
                            raise ValueError(
                                f"The header time is visible, but this function " +
                                "expects header time to be invisible."
                            )
                    # remove
                    attributes_element.remove(time_element)

                # re-insert them
                if desired_time is not None:
                    time_copy = copy.deepcopy(desired_time)
                    time_copy.attrib["print-object"] = "no"
                    attributes_element.append(
                        time_copy
                    )
                    sort_attributes(attributes_element)

            # for non-header attributes
            if not is_header_attributes:
                for time_element in attributes_element.findall("time"):
                    # raise on invisible ones
                    if time_element.attrib.get("print-object", "yes") == "no":
                        raise ValueError(
                            f"The input <part> element contains an invisible " +
                            f"time change at part onset of {self.part_onset}. Invisible " +
                            f"time signatures are only allowed at onset 0 (header time signature)."
                        )

    MyVisitor().run(part_element)

    return part_element
