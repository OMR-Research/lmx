import xml.etree.ElementTree as ET
import copy
from .MeasureAsTracks import MeasureAsTracks


class ContainsTruePianoformMusicException(Exception):
    """Thrown by the splitting method when the piano part cannot
    be split without breaking the music notation"""
    def __init__(
            self,
            message: str,
            measure_number: str | None,
            measure_index: int,
            track_index: int
    ):
        self.message = message
        self.metadata = {
            "measure_number": measure_number,
            "measure_index": measure_index,
            "track_index": track_index
        }
    
    def __str__(self):
        return "Piano part cannot be split because it contains " + \
            "true pianoform music. Use force=True to split anyways. " + \
            "Details: " + self.message + " " + repr(self.metadata)


def split_piano_part_staves(
        piano_part: ET.Element,
        upper_part_id: str,
        lower_part_id: str,
        force_split=False
) -> tuple[ET.Element, ET.Element]:
    """
    Given a `<part>` element containing a two-staff piano music,
    this method tries splitting that part into two new `<part>`
    elements, each containing one of the two staves. If the part
    contains truly pianoform music that cannot be losslessly
    separated, this method results in an exception. This method
    returns a tuple of two parts, first the upper staff part
    and second the lower staff part.

    This method assumes the input MusicXML has been canonicalized
    by MuseScore, i.e. the part has voices 1-8 where 1-4 are upper
    staff and 5-8 are lower staff. Moreover, backup elements are
    only present in between voices when rewinding back to the
    start of the measure.

    This method works by splitting the part up into separate voices,
    then checking that each voice stays within its staff (based
    on the MuseScore voice numbering) and then duplicating the part,
    and erasing voices that belong to the other staff, while leaving
    all the attributes and directions in place. Since beams and
    slurs in MuseScore can't cross voices, they are handled gracefully.

    Then, it post-processes copies and erases `<staff>` tags and
    other-staff clefs and renames voices 5-8 back to 1-4.
    """
    assert piano_part.tag == "part"

    staves_element = piano_part.find("measure/attributes/staves")
    assert staves_element is not None, "Given part lacks <staves> element"
    assert staves_element.text == "2", "Given part is not a 2-staff part"

    # do the split
    upper_part = ET.Element("part", {"id": upper_part_id})
    lower_part = ET.Element("part", {"id": lower_part_id})

    for measure_index, measure_element in enumerate(piano_part):
        # run checks that there is no track that crosses staves
        if not force_split:
            _check_voice_staff_correspondence(
                measure_element=measure_element,
                measure_index=measure_index
            )
        
        # upper part measure
        measure = MeasureAsTracks.from_element(
            copy.deepcopy(measure_element)
        )
        for voice in ["5", "6", "7", "8"]:
            measure.remove_track_with_voice(voice)
        measure.remove_staff_from_head(
            staff_to_remove=2,
            collapse_to_single_staff=True
        )
        measure.remove_staff_tags_from_tracks()
        upper_part.append(measure.to_element())

        # lower part measure
        measure = MeasureAsTracks.from_element(
            copy.deepcopy(measure_element)
        )
        for voice in ["1", "2", "3", "4"]:
            measure.remove_track_with_voice(voice)
        measure.remove_staff_from_head(
            staff_to_remove=1,
            collapse_to_single_staff=True
        )
        measure.remove_staff_tags_from_tracks()
        measure.rename_voices({
            "5": "1",
            "6": "2",
            "7": "3",
            "8": "4"
        })
        # TODO: convert first-voice forwards to invisible rests
        lower_part.append(measure.to_element())

    return (upper_part, lower_part)


def _check_voice_staff_correspondence(
        measure_element: ET.Element,
        measure_index: int
):
    """
    Makes sure that each `<note>` has `<staff>` value that matches
    its `<voice>` value. Specifically: Staff 1 has voices 1-4 and
    staff 2 has voices 5-8. Also makes sure that each `<note>`
    has a staff specified. It also checks that each `<clef>`
    has staff number specified.
    """
    measure = MeasureAsTracks.from_element(measure_element)

    measure_number = measure_element.get("number", None)

    for track_index, track in enumerate(measure.tracks):
        # each track should belong to exactly one staff
        if len(track.staff_set) != 1:
            raise ContainsTruePianoformMusicException(
                message="A track belongs to more than one staff: " + repr(track.staff_set),
                measure_number=measure_number,
                measure_index=measure_index,
                track_index=track_index
            )
        
        # each track should have exactly one voice
        # (this invariant is asserted when parsing MeasureAsTracks)

        # get the voice and staff
        voice = track.voice
        staff = next(iter(track.staff_set))

        # check that the voice belongs to the correct staff
        if staff == 1:
            if voice not in ["1", "2", "3", "4"]:
                raise ContainsTruePianoformMusicException(
                    message=f"First staff should have voices 1-4, " + \
                        f"track has voice {voice}",
                    measure_number=measure_number,
                    measure_index=measure_index,
                    track_index=track_index
                )
        elif staff == 2:
            if voice not in ["5", "6", "7", "8"]:
                raise ContainsTruePianoformMusicException(
                    message=f"Second staff should have voices 5-8, " + \
                        f"track has voice {voice}",
                    measure_number=measure_number,
                    measure_index=measure_index,
                    track_index=track_index
                )
