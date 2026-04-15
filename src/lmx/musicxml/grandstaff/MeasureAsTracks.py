import xml.etree.ElementTree as ET


class Track:
    def __init__(self) -> None:
        self.elements: list[ET.Element] = []
        """XML elements within this track (does not include the `<backup>` element)"""

        self.backup_element: ET.Element | None = None
        """The `<backup>` element at the end of the track; None for the last track"""
    
        self.voice_set: set[str] = set()
        """Voices present in this track - taken from `<voice>` elements"""

        self.staff_set: set[int] = set()
        """Staves present in this track - taken from `<staff>` elements"""

        self.total_duration: int = 0
        """Total duration in divisions used within the measure.
        Should match the duration of the final backup element if present."""

    def recompute_statistics(self):
        """Computes voice set, staff set and total duration"""
        self.voice_set = set()
        self.staff_set = set()
        self.total_duration = 0

        def _extract_duration(child: ET.Element) -> int:
            duration_element = child.find("duration")
            chord_element = child.find("chord")
            if duration_element is None:
                return 0
            if chord_element is not None:
                return 0
            return int(duration_element.text or "0")

        def _extract_voice(child: ET.Element, required: bool):
            voice_element = child.find("voice")
            if required:
                assert voice_element is not None, \
                    f"This class expects each <{child.tag}> to have a <voice>"
            if voice_element is not None:
                self.voice_set.add(voice_element.text or "None")

        def _extract_staff(child: ET.Element, first_if_missing: bool):
            staff_element = child.find("staff")
            if staff_element is not None:
                self.staff_set.add(int(staff_element.text or "1"))
            elif first_if_missing:
                self.staff_set.add(1)

        for child in self.elements:
            if child.tag == "note":
                self.total_duration += _extract_duration(child)
                _extract_voice(child, required=True)
                _extract_staff(child, first_if_missing=True)
            elif child.tag == "forward":
                self.total_duration += _extract_duration(child)
                _extract_voice(child, required=False)
                _extract_staff(child, first_if_missing=False)
            elif child.tag == "direction":
                _extract_voice(child, required=False)
                _extract_staff(child, first_if_missing=False)
            elif child.tag == "attributes":
                for key_element in child.findall("key"):
                    if "number" in key_element.attrib:
                        self.staff_set.add(int(key_element.attrib["number"]))
                for clef_element in child.findall("clef"):
                    if "number" in clef_element.attrib:
                        self.staff_set.add(int(clef_element.attrib["number"]))

    def run_assertions(self):
        """Runs checks to make sure the track is consistent"""
        assert len(self.voice_set) <= 1, \
            "There should at most one voice per track, " + \
                "voices: " + repr(self.voice_set)
        if self.backup_element is not None:
            assert self.backup_element.find("duration").text == str(self.total_duration), \
                "Backup element should have duration equal to the " + \
                    "track duration " + repr({
                        "backup_duration": self.backup_element.find("duration").text,
                        "track_duration": str(self.total_duration)
                    })
    
    @property
    def voice(self) -> str:
        """Returns the voice name for this track"""
        return next(iter(self.voice_set))
    
    def remove_staff_tags(self):
        """Removes all `<staff>` and number="X" tags from the track"""
        for child in self.elements:
            if child.tag in ["note", "forward", "direction"]:
                staff_element = child.find("staff")
                if staff_element is not None:
                    child.remove(staff_element)
            elif child.tag == "attributes":
                for subchild in child:
                    if subchild.tag in ["key", "clef", "staff-details", "measure-style"]:
                        subchild.attrib.pop("number", None)
            elif child.tag == "print":
                for subchild in child:
                    if subchild.tag in ["staff-layout"]:
                        subchild.attrib.pop("number", None)
        
        self.recompute_statistics()
        self.run_assertions()
    
    def add_staff_tags(self, staff: int):
        """Adds `<staff>` and number="X" tags to all elements,
        all set to the same staff number. Overwrites existing tags."""
        for child in self.elements:
            if child.tag in ["note", "forward", "direction"]:
                staff_element = child.find("staff")
                if staff_element is None:
                    staff_element = ET.Element("staff")
                    child.append(staff_element)
                staff_element.text = str(staff)
            elif child.tag == "attributes":
                for subchild in child:
                    if subchild.tag in ["key", "clef", "staff-details", "measure-style"]:
                        subchild.attrib["number"] = str(staff)
            elif child.tag == "print":
                for subchild in child:
                    if subchild.tag in ["staff-layout"]:
                        subchild.attrib["number"] = str(staff)
        
        self.recompute_statistics()
        self.run_assertions()
    
    def rename_voices(self, voice_map: dict[str, str]):
        """Change names of voices according to the given map"""
        for child in self.elements:
            if child.tag in ["note", "forward", "direction"]:
                voice_element = child.find("voice")
                if voice_element is not None:
                    if voice_element.text in voice_map:
                        voice_element.text = voice_map[voice_element.text]
        
        self.recompute_statistics()
        self.run_assertions()
    
    def add_computed_backup_element(self):
        """Adds a backup element to the end of the track with the
        duration taken from the computed duration."""
        assert self.backup_element is None, \
            "Cannot add backup element, one already present"
        self.recompute_statistics()

        backup_element = ET.Element("backup")
        duration_element = ET.Element("duration")
        duration_element.text = str(self.total_duration)
        backup_element.append(duration_element)
        
        self.backup_element = backup_element


class MeasureAsTracks:
    """
    Parsed representation of MusicXML `<measure>` element, where its
    content is split into head, tail and tracks. Head contains the
    leading `<print>` and `<attributes>` that occur at onset 0.
    Tail contains the `<barline>` definition at the very end of the
    `<measure>` element. Tracks are then created from the remaining
    middle content, splitting it by the `<backup>` element. One
    track is therefore roughly a single voice, but it also contains
    clef changes, key changes, directions and other elements that are
    often present within the first voice.
    """
    
    def __init__(self) -> None:
        self.measure_element_attributes: dict[str, str] = {}
        """The XML attributes on the `<measure>` element"""

        self.head_print_element: ET.Element | None = None
        """The `<print>` element that may be present at the measure head"""

        self.head_barline_element: ET.Element | None = None
        """The `<barline>` element that may be present at the measure head"""

        self.head_attributes_element: ET.Element | None = None
        """The `<attributes>` element that may be present at the measure head"""

        self.tail_barline_element: ET.Element | None = None
        """The `<barline>` element that may be present at the measure tail"""

        self.tracks: list[Track] = []
        """List of tracks in the measure, in the same order as in MXL"""

    def recompute_track_statistics(self):
        """Computes voice set and staff set for each track"""
        for track in self.tracks:
            track.recompute_statistics()
    
    def run_track_assertions(self):
        """Runs checks to make sure the track is consistent"""
        for track in self.tracks:
            track.run_assertions()
        
        # check that each track has a backup, except the last one
        for i, track in enumerate(self.tracks):
            is_last = (i == len(self.tracks) - 1)
            if is_last:
                assert track.backup_element is None, \
                    "The last track musn't have a backup element"
            else:
                assert track.backup_element is not None, \
                    "Tracks must have backup elements, except the last one"

    @staticmethod
    def from_element(measure_element: ET.Element) -> "MeasureAsTracks":
        """Constructs the measure with tracks from a measure element"""
        measure = MeasureAsTracks()
        measure.measure_element_attributes = measure_element.attrib
        
        # take all child elements in the measure
        children = list(measure_element)

        # chop off the head
        while len(children) > 0:
            child = children.pop(0)
            
            if child.tag == "print":
                assert measure.head_print_element is None, \
                    "There are multiple <print> head elements in the measure"
                measure.head_print_element = child
                continue
            elif child.tag == "barline":
                assert measure.head_barline_element is None, \
                    "There are multiple <barline> head elements in the measure"
                measure.head_barline_element = child
                continue
            elif child.tag == "attributes":
                assert measure.head_attributes_element is None, \
                    "There are multiple <attributes> head elements in the measure"
                measure.head_attributes_element = child
                continue

            children.insert(0, child)
            break

        # chop off the tail
        while len(children) > 0:
            child = children.pop(-1)

            if child.tag == "barline":
                assert measure.tail_barline_element is None, \
                    "There are multiple <barline> tail elements in the measure"
                measure.tail_barline_element = child
                continue

            children.append(child)
            break

        assert len(children) > 0, "The measure has no musical content"

        # parse out tracks by breaking at the <backup> elements
        current_track = Track()
        
        for child in children:
            if child.tag == "backup":
                current_track.backup_element = child
                measure.tracks.append(current_track)
                current_track = Track()
            else:
                current_track.elements.append(child)
        
        if len(current_track.elements) > 0:
            measure.tracks.append(current_track)
        
        # check invariants
        measure.recompute_track_statistics()
        measure.run_track_assertions()

        # parsing is complete
        return measure

    def to_element(self) -> ET.Element:
        """Exports contents packaged up in a new `<measure>` element"""
        # before we produce any output, check invariants
        self.recompute_track_statistics()
        self.run_track_assertions()
        
        # create the output XML element
        measure_element = ET.Element(
            "measure",
            self.measure_element_attributes
        )

        # head
        if self.head_print_element is not None:
            measure_element.append(self.head_print_element)
        if self.head_barline_element is not None:
            measure_element.append(self.head_barline_element)
        if self.head_attributes_element is not None:
            measure_element.append(self.head_attributes_element)

        # tracks
        for track in self.tracks:
            for e in track.elements:
                measure_element.append(e)
            if track.backup_element is not None:
                measure_element.append(track.backup_element)

        # tail
        if self.tail_barline_element is not None:
            measure_element.append(self.tail_barline_element)
        
        return measure_element
    
    def remove_track_with_voice(self, voice: str) -> bool:
        """Removes the track with the given voice name. If there is
        not such track, it does nothing and returns false. If it succeeds,
        it returns true."""
        # find the track to be removed by its voice name
        for track_index, track in enumerate(self.tracks):
            if track.voice == voice:

                # remove the track
                del self.tracks[track_index]

                # make sure the last track lacks the backup element
                # to keep an invariant in place
                self.tracks[-1].backup_element = None

                # success
                return True
        
        # failure
        return False

    def remove_staff_from_head(
            self,
            staff_to_remove: int,
            collapse_to_single_staff: bool
    ):
        """
        In head elements, removes all clefs and signatures
        that belong to the given staff. If specified, it also removes
        the number="X" attribute from the remaining elements as well
        as removing the <staves> element.
        """
        # <attributes> element
        if self.head_attributes_element is not None:
            children_to_remove: list[ET.Element] = []

            for child in self.head_attributes_element:
                if child.tag in ["key", "clef", "staff-details", "measure-style"]:
                    if child.attrib.get("number", "1") == str(staff_to_remove):
                        children_to_remove.append(child)
                    elif collapse_to_single_staff:
                        child.attrib.pop("number", None)
                elif child.tag == "staves":
                    child.text = str(int(child.text or "1") - 1)
                    if collapse_to_single_staff:
                        children_to_remove.append(child)
            
            for child in children_to_remove:
                self.head_attributes_element.remove(child)

            if len(self.head_attributes_element) == 0:
                self.head_attributes_element = None
        
        # <print> element
        if self.head_print_element is not None:
            children_to_remove = []

            for child in self.head_print_element:
                if child.tag in ["staff-layout"]:
                    if child.attrib.get("number", "1") == str(staff_to_remove):
                        children_to_remove.append(child)
                    elif collapse_to_single_staff:
                        child.attrib.pop("number", None)
            
            for child in children_to_remove:
                self.head_print_element.remove(child)

            if len(self.head_print_element) == 0:
                self.head_print_element = None

    def add_staff_tags_to_head(self, staff: int):
        """Adds number="X" tags to head elements."""
        # <attributes> element
        if self.head_attributes_element is not None:
            for child in self.head_attributes_element:
                if child.tag in ["key", "clef", "staff-details", "measure-style"]:
                    child.attrib["number"] = str(staff)
        
        # <print> element
        if self.head_print_element is not None:
            for child in self.head_print_element:
                if child.tag in ["staff-layout"]:
                    child.attrib["number"] = str(staff)

    def remove_staff_tags_from_tracks(self) -> None:
        """Removes all `<staff>` and number="X" tags from tracks,
        makes sure that only one staff is being used by all tracks."""
        all_staves: set[int] = set()
        for track in self.tracks:
            for s in track.staff_set:
                all_staves.add(s)
        assert len(all_staves) == 1, \
            "Staff tags can only be removed if there is only one remaining staff"
        
        for track in self.tracks:
            track.remove_staff_tags()

        self.recompute_track_statistics()
        self.run_track_assertions()
    
    def add_staff_tags_to_tracks(self, staff: int):
        """Adds `<staff>` and number="X" tags to all tracks,
        all set to the same staff number."""
        all_staves: set[int] = set()
        for track in self.tracks:
            for s in track.staff_set:
                all_staves.add(s)
        assert len(all_staves) <= 1, \
            "Staff tags can only be set if there is only (at most) " + \
            "one (implicit) staff"
        
        for track in self.tracks:
            track.add_staff_tags(staff)

        self.recompute_track_statistics()
        self.run_track_assertions()
    
    def rename_voices(self, voice_map: dict[str, str]):
        """Change names of voices according to the given map"""
        for track in self.tracks:
            track.rename_voices(voice_map)

        self.recompute_track_statistics()
        self.run_track_assertions()
