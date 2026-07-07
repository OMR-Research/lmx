import xml.etree.ElementTree as ET
from typing import Literal
import copy
from ..time.OnsetVisitor import OnsetVisitor
from ..pitch.repair_alters import repair_alters


def normalize_invisible_key_signature(
        part_element: ET.Element,
        desired_key: int,
        when_key_visible: Literal[
            "dont-normalize",
            "raise-exception",
        ],
) -> ET.Element:
    """
    Takes in a `<part>` element with invisible header key signature
    and changes that signature to the desired key signature,
    while adjusting alter values and accidental cautionary values
    for the part content up until a key change. The `<part>` may
    contain multiple staves (e.g. piano part), but all of them
    must have the same key. While MusicXML support per-staff keys,
    MuseScore does not and we primarily target MuseScore.
    If the <part> contains invisible key signature anywhere other
    than the head (onset zero), an exception is raised. Visible
    key signatures are ok.

    This method creates a copy of the part element and returns that
    modified copy. The input part element is left unmodified.

    :param part_element: The `<part>` MusicXML element to be normalized.
    :param desired_key: The key that should replace the existing
        invisible key. The key signature will remain invisible,
        unless it's the null signature, which is set to visible,
        since it makes no sense for null signature to be invisible
        (it sort-of already is). The value is the fifths value
        from the MusicXML standard, positive being sharps and negative
        being flats.
    :param when_key_visible: Specifies how to behave, when the
        header key is visible (which is unexpected). Select behaviour
        that best matches your usecase.
    """
    assert desired_key >= -7 and desired_key <= 7

    # create a copy of the input before we start modifying it
    part_element = copy.deepcopy(part_element)

    class MyVisitor(OnsetVisitor):
        def __init__(self):
            super().__init__(record_onsets=False)
        
        def visit_attributes(self, attributes_element: ET.Element):
            # visit all <key> elements (should be only one)
            for key_element in attributes_element.findall("key"):
                # the <key> element should NOT have a staff number
                if "number" in key_element.attrib:
                    raise ValueError(
                        "This function supports only full-part key signatures, " +
                        "not per-staff key signatures."
                    )
                
                # extract key signature parameters
                is_header_key = self.part_onset == 0
                is_invisible = key_element.attrib.get("print-object", "yes") == "no"
                is_null_signature = key_element.findtext("fifths") == "0"
                
                # a) handle header keys
                if is_header_key:
                    # handle visible header keys
                    if not is_invisible and not is_null_signature:
                        if when_key_visible == "dont-normalize":
                            continue # just skip the <key> element
                        elif when_key_visible == "raise-exception":
                            raise ValueError(
                                f"The header key is visible, but this function " +
                                "expects header key to be invisible."
                            )
                    
                    # handle invisible header keys
                    else:
                        _update_header_key(key_element, desired_key)
                
                # b) handle non-header keys
                else:
                    # raise on invisible ones
                    if is_invisible:
                        raise ValueError(
                            f"The input <part> element contains an invisible " +
                            f"key change at part onset of {self.part_onset}. Invisible " +
                            f"keys are only allowed at onset 0 (header key signature)."
                        )

    MyVisitor().run(part_element)

    repair_alters(part_element)

    return part_element


def _update_header_key(
        key_element: ET.Element,
        desired_key: int
):
    fifths_element = key_element.find("fifths")
    assert fifths_element is not None
    fifths_element.text = str(desired_key)
    if desired_key == 0:
        key_element.attrib.pop("print-object", None)
    else:
        key_element.attrib["print-object"] = "no"
