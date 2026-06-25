import xml.etree.ElementTree as ET
import copy
from typing import Literal
from .Clef import Clef
from .Pitch import Pitch
from .map_part_pitches import map_part_pitches
from ..attributes.get_head_attributes import get_head_attributes
from .transpose_pitch_given_clef_change \
    import transpose_pitch_given_clef_change


def normalize_invisible_header_clef(
        part_element: ET.Element,
        desired_clef: Clef | list[Clef],
        when_clef_visible: Literal[
            "dont-normalize",
            "normalize-keep-visible",
            "normalize-set-invisible",
            "raise-exception",
        ],
) -> ET.Element:
    """
    Takes in a `<part>` element with invisible header clef and changes
    that clef to the desired clef, while transposing all following notes
    in a way that preserves their visual appearance (staffline positions
    and accidentals). Notes are transposed for until a new visible clef
    is reached. The given `<part>` element typically contains only
    one system, but it isn't required. The '<part>' may contain multiple
    staves (e.g. piano part), in which case each staff behaves
    independently and the desired clef can be specified as a list of clefs
    if each staff is to have a different clef (e.g. [G, F] for piano).
    If during transposition of a staff we hit another invisible clef,
    we throw an exception as there should be no invisible clefs
    in the middle of the `<part>` (if you do need to handle these edge
    cases, preprocess the part accordingly, e.g. slice it into systems).

    This method creates a copy of the part element and returns that
    modified copy. The input part element is left unmodified.

    :param part_element: The `<part>` MusicXML element to be normalized.
    :param desired_clef: The clef that should replace the existing
        invisible clef. A list of clefs can be provided for multi-staff
        parts, ordered top to bottom. So for a piano part, you can
        specify desired clefs to be [G, F].
    :param when_clef_visible: Specifies how to behave, when the
        header clef is visible (which is unexpected). Select behaviour
        that best matches your usecase.
    """

    # create a copy of the input before we start modifying it
    part_element = copy.deepcopy(part_element)

    # check that the input is not empty
    if len(part_element.findall("measure")) == 0:
        raise ValueError("Given part element does not contain any measures")

    # extract the header <attributes> element
    header_attributes = get_head_attributes(
        part_element.find("measure"), # first measure
        create_if_missing=False
    )
    if header_attributes is None:
        raise ValueError(
            "Given <part> element does not have the header <attributes> " + \
            "element that defines header clefs."
        )

    # Get the header clef for each (defined) staff
    # staff number -> clef element
    header_clef_elements: dict[int, ET.Element] = {
        int(clef_element.get("number", "1")): clef_element
        for clef_element in header_attributes.findall("clef")
    }
    if len(header_clef_elements) == 0:
        raise ValueError(
            "Given <part> element does not have a single defined header clef"
        )
    
    # staff number -> Clef
    # Which clef is the original clef we're normalizing away from for each staff
    original_header_clefs: dict[int, Clef] = {
        staff_number: Clef.from_clef_element(clef_element)
        for staff_number, clef_element in header_clef_elements.items()
    }

    # check that there are enough desired clef arguments for the clefs in part
    if not isinstance(desired_clef, Clef):
        for staff_number in original_header_clefs.keys():
            if staff_number < 1:
                raise ValueError(
                    "The <part> contains a header clef with " +
                    "staff number lower than 1"
                )
            if staff_number > len(desired_clef):
                raise ValueError(
                    f"The <part> contains a header clef on " +
                    f"staff {staff_number}, but there were " +
                    f"only {len(desired_clef)} desired clefs specified."
                )

    # For each staff, define which clef should we normalize to
    # staff number -> Clef
    target_header_clefs: dict[int, Clef] = {
        staff_number: desired_clef if isinstance(desired_clef, Clef)
            else desired_clef[staff_number - 1]
        for staff_number in original_header_clefs.keys()
    }

    # check that header clefs are invisible and if not, handle that
    # TODO ...
    
    ##############################
    # Phase 1 - get onset ranges #
    ##############################

    # staff number -> part onset
    # The first onset, where a (visible) clef change occurs, for each staff
    # (not specified if no clef change exists for the staff)
    clef_change_onset: dict[int, int] = {}

    # track onset relative to the start of the part
    part_onset = 0

    for measure_element in part_element.findall("measure"):
        for child in measure_element:
            
            # visit all <attributes>
            if child.tag == "attributes":
                # visit all <clef> elements
                for clef_element in child.findall("clef"):
                    staff_number = int(clef_element.get("number", "1"))
                    
                    # clef at onset 0 is not a clef change, skip
                    if part_onset != 0:

                        # check that this clef is visible
                        if not Clef.is_element_visible(clef_element):
                            raise ValueError(
                                f"The input <part> element contains an invisible " +
                                f"clef at part onset of {part_onset}. Invisible " +
                                f"clefs are only allowed at onset 0 (header clefs)."
                            )
                        
                        # insert or decrease the currently known onset for the staff
                        if staff_number not in clef_change_onset:
                            clef_change_onset[staff_number] = part_onset
                        elif part_onset < clef_change_onset[staff_number]:
                            clef_change_onset[staff_number] = part_onset

            # update onset (always)
            duration = int(child.findtext("duration", "0"))
            if child.tag == "backup":
                duration = -duration
            part_onset += duration
    
    #################################
    # Phase 2 - change header clefs #
    #################################

    for staff_number in original_header_clefs.keys():
        target_header_clefs[staff_number].populate_clef_element(
            header_clef_elements[staff_number],
            set_visibility="invisible" # ensure invisible (TODO respect args)
        )
    
    ###############################
    # Phase 3 - transpose pitches #
    ###############################

    def pitch_mapper(
            note_element: ET.Element,
            pitch: Pitch,
            part_onset: int,
            staff_number: int
    ) -> Pitch:
        nonlocal clef_change_onset

        # no mapping after a clef change
        if part_onset >= clef_change_onset.get(staff_number, float("inf")):
            return pitch
        
        # skip notes on staves for which there are no header clefs
        # (this signals a faulty MusicXML, but we silently let it pass)
        if staff_number not in original_header_clefs:
            return pitch
        
        assert staff_number in target_header_clefs, \
            "target_header_clefs must have the same keys as original_header_clefs"

        # transpose the pitch based on the clef change
        return transpose_pitch_given_clef_change(
            pitch=pitch,
            old_clef=original_header_clefs[staff_number],
            new_clef=target_header_clefs[staff_number]
        )

    map_part_pitches(part_element, pitch_mapper)

    return part_element
