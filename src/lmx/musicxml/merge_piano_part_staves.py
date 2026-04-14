import xml.etree.ElementTree as ET
import copy
from .MeasureAsTracks import MeasureAsTracks


def merge_piano_part_staves(
        upper_part: ET.Element,
        lower_part: ET.Element,
        output_part_id: str
) -> ET.Element:
    """
    Combines two single-staff parts into one double-staff piano part.
    Works with `<part>` elements as inputs and as output.

    This method assumes the input MusicXML has been canonicalized
    by MuseScore, i.e. the input parts have voices 1-4. Moreover,
    backup elements are only present in between voices when rewinding
    back to the start of the measure. The output part has voices 1-8
    where 1-4 are the upper staff and 5-8 are the lower staff.

    This method works by splitting both parts into voices, renaming
    the second set of voices and merging them into a new part.
    """
    assert upper_part.tag == "part"
    assert lower_part.tag == "part"

    assert len(upper_part) == len(lower_part), \
        "Both input parts must have the same number of measures"
    
    output_part = ET.Element("part", {"id": output_part_id})

    # do the merger measure-by-measure
    # (merge the lower-measure contents into the upper-measure instance)
    first_measure = True
    for upper_measure_element, lower_measure_element in zip(
        upper_part, lower_part
    ):
        # parse both measures into tracks
        upper_measure = MeasureAsTracks.from_element(
            copy.deepcopy(upper_measure_element)
        )
        lower_measure = MeasureAsTracks.from_element(
            copy.deepcopy(lower_measure_element)
        )

        # rename voices in the lower measure
        lower_measure.rename_voices({
            "1": "5",
            "2": "6",
            "3": "7",
            "4": "8"
        })

        # add staff numbers to both measures
        upper_measure.add_staff_tags_to_head(1)
        upper_measure.add_staff_tags_to_tracks(1)
        lower_measure.add_staff_tags_to_head(2)
        lower_measure.add_staff_tags_to_tracks(2)

        # merge heads
        # (ignore print, we'll use the first part's one)
        # (merge only clefs and key signatures)
        if lower_measure.head_attributes_element is not None:
            if upper_measure.head_attributes_element is None:
                # transfer instead of merging
                upper_measure.head_attributes_element = lower_measure.head_attributes_element
            elif upper_measure.head_attributes_element is not None:
                # do the merge
                for clef in lower_measure.head_attributes_element.findall("clef"):
                    upper_measure.head_attributes_element.append(clef)
                for key in lower_measure.head_attributes_element.findall("key"):
                    upper_measure.head_attributes_element.append(key)

        # merge tails
        # (nothing, barlines will likely be in both input parts)

        # make sure <staves> element is only present in the
        # first measure and it has proper value of 2
        if first_measure:
            # ensure <staves> is 2
            if upper_measure.head_attributes_element is None:
                upper_measure.head_attributes_element = ET.Element("attributes")
            staves_element = upper_measure.head_attributes_element.find("staves")
            if staves_element is None:
                staves_element = ET.Element("staves")
                upper_measure.head_attributes_element.append(staves_element)
            staves_element.text = "2"
        else:
            # delete any <staves> elements
            if upper_measure.head_attributes_element is not None:
                for e in list(upper_measure.head_attributes_element.findall("staves")):
                    upper_measure.head_attributes_element.remove(e)

        # merge tracks
        upper_measure.tracks[-1].add_computed_backup_element()
        for track in lower_measure.tracks:
            upper_measure.tracks.append(track)
        
        # export the merged measure
        output_part.append(upper_measure.to_element())

        # we are no longer processing the first measure
        first_measure = False

    return output_part
