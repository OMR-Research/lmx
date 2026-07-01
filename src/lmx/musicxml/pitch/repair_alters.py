import xml.etree.ElementTree as ET
from ..time.MeasureOnset import MeasureOnset
from ..time.OnsetVisitor import OnsetVisitor
from .accidental_to_alter import accidental_to_alter
from .AccidentalPitch import AccidentalPitch
from .Pitch import Pitch, Step
from dataclasses import dataclass
from typing import Literal
import bisect
import copy


def repair_alters(
        part_element: ET.Element,
        repair_cautionaries=True,
) -> None:
    """Sets pitch `<alter>` values to match the visual `<accidental>` values,
    while respecting key signatures and other complications.
    
    MusicXML encodes both visual (`<accidental>`) and semantic
    (`<alter>`) data. In a correct document, these two layers are in sync.
    However, often times during MusicXML processing, we might get them
    out of sync. Especially in LMX where we put stress on visual appearance.
    This method takes all the visual data and repairs the semantic data
    corresponding to pitch alters and accidentals to match. This is needed,
    because while we focus on visual and ignore semantic in LMX,
    MuseScore does the opposite - parsing semantic and mostly ignoring
    visual. Therefore to make out MusicXML documents readable by MuseScore,
    we need to get these two representation layers in sync.

    This method sets `<alter>` values on all notes of a `<part>`,
    plus it sets `<accidental>` attribute `cautionary="yes"` accordingly.

    This method modifies the given `<part>` element in-place.
    If you need to preserve it, pass in a copy via copy.deepcopy(...).

    :param part_element: The `<part>` element whoose contents to repair.
    :param repair_cautionaries: Whether the fuction should repair
        the accidental cautionary attribute as well.
    """

    if part_element.tag != "part":
        raise ValueError("The given MusicXML element is not a <part>")

    visitor = RepairAltersVisitor(
        repair_alters=True,
        repair_cautionaries=repair_cautionaries,
    )
    visitor.run(part_element)


@dataclass(frozen=True, eq=True)
class AccidentalOccurrence:
    """An occurrence of a note-bound accidental in the score"""
    
    accidental_pitch: AccidentalPitch
    """On which line/space of which staff the accidental occurs"""
    
    onset: MeasureOnset
    """When in the measure the accidental occurs"""
    
    accidental: str
    """Which accidental is present"""

    def __post_init__(self):
        assert self.accidental in [
            "sharp", "flat", "natural", "double-sharp",
            "flat-flat", "natural-sharp", "natural-flat"
        ], f"Invalid accidental type: {self.accidental}"


class AccidentalMap:
    """
    A map of note-bound accidentals within a measure.
    Can be used to query accidentals defined and carried
    at a specific pitch and onset. Does not track key
    signature accidentals.
    """
    def __init__(self) -> None:
        self._accidentals: dict[AccidentalPitch, list[AccidentalOccurrence]] = {}
        """For each accidental pitch, remembers the list of
        accidentals defined there together with their onset,
        sorted by the onset."""
    
    def insert_accidental(self, occurrence: AccidentalOccurrence):
        """Inserts an accidental occurrence into the map"""
        if occurrence.accidental_pitch not in self._accidentals:
            self._accidentals[occurrence.accidental_pitch] = []
        
        occurrences = self._accidentals[occurrence.accidental_pitch]
        bisect.insort(occurrences, occurrence, key=lambda o: o.onset)
    
    @staticmethod
    def empty() -> "AccidentalMap":
        """Creates an empty accidental map (corresponds to an empty measure)"""
        return AccidentalMap()

    @staticmethod
    def create_for(
        measure_element: ET.Element,
        divisions: int | Literal["fractional"]
    ) -> "AccidentalMap":
        class _MyVisitor(OnsetVisitor):
            def __init__(self):
                super().__init__(record_onsets=False)
                self.map = AccidentalMap()
            
            def visit_note(self, note_element: ET.Element):
                accidental_element = note_element.find("accidental")
                if accidental_element is None or accidental_element.text is None:
                    return # skip notes without accidentals
                
                self.map.insert_accidental(AccidentalOccurrence(
                    accidental_pitch=AccidentalPitch.from_note_element(note_element),
                    onset=self.measure_onset,
                    accidental=accidental_element.text
                ))
        
        visitor = _MyVisitor()
        visitor.run(
            element=measure_element,
            divisions=divisions
        )
        return visitor.map

    def get_carried_accidental(
            self,
            accidental_pitch: AccidentalPitch,
            onset: MeasureOnset
    ) -> str | None:
        """Returns the latest accidental at the given pitch
        that occurs before the current onset, but not on it (
        does not return the local accidental)"""
        preceeding_occurrences = [
            occurrence
            for occurrence in self._accidentals.get(accidental_pitch, [])
            if occurrence.onset < onset
        ]
        if len(preceeding_occurrences) == 0:
            return None
        return preceeding_occurrences[-1].accidental


class RepairAltersVisitor(OnsetVisitor):
    def __init__(self, repair_alters: bool, repair_cautionaries: bool):
        super().__init__(record_onsets=False)

        # configuration
        self.repair_alters = repair_alters
        self.repair_cautionaries = repair_cautionaries

        # per-part state
        # (MuseScore does not allow mid-measure changes, so we don't
        # need to create complex maps, just hold the context
        # for the entire measure)
        self._key_signature: int = 0

        # per-measure state
        self._accidental_map = AccidentalMap.empty()
        self._tie_starts: dict[AccidentalPitch, ET.Element] = {}
        self._previous_tie_starts: dict[AccidentalPitch, ET.Element] = {}
    
    def visit_measure(
            self,
            measure_element: ET.Element,
    ):
        # reset per-measure state
        self._accidental_map = AccidentalMap.create_for(
            measure_element=measure_element,
            divisions=self.divisions
        )
        self._previous_tie_starts = self._tie_starts
        self._tie_starts = {}

        super().visit_measure(measure_element)
    
    def visit_attributes(self, attributes_element: ET.Element):
        fifths_element = attributes_element.find("key/fifths")
        if fifths_element is not None:
            self._key_signature = int(fifths_element.text or "0")
    
    def visit_note(self, note_element: ET.Element):
        pitch_element = note_element.find("pitch")
        if pitch_element is None:
            return # skip rests and other notes without pitch
        
        # compute proper alter and accidental cautionarity value
        new_alter, is_cautionary = self.determine_alter_and_cautionarity(
            note_element=note_element,
            note_onset=self.measure_onset,
        )

        # update the pitch (if alter changed)
        pitch = Pitch.from_pitch_element(pitch_element)
        if new_alter != pitch.alter:
            new_pitch = Pitch(
                step=pitch.step,
                octave=pitch.octave,
                alter=new_alter
            )
            new_pitch.populate_pitch_element(pitch_element)
        
        # if there is an accidental, adjust its cautionarity
        if is_cautionary is not None:
            accidental_element = note_element.find("accidental")
            assert accidental_element is not None
            if is_cautionary:
                accidental_element.attrib["cautionary"] = "yes"
                accidental_element.attrib["parentheses"] = "no"
            else:
                accidental_element.attrib.pop("cautionary", None)
                accidental_element.attrib.pop("parentheses", None)
        
        # replace the <pitch> element completely if this
        # note is an end of a tie
        self.process_ties(note_element)

    def process_ties(self, note_element: ET.Element):
        accidental_pitch = AccidentalPitch.from_note_element(note_element)

        has_start = False  # can be both!
        has_stop = False
        for tie in note_element.iterfind("tie"):
            if tie.get("type") == "start":
                has_start = True
            if tie.get("type") == "stop":
                has_stop = True

        if has_stop:
            if accidental_pitch in self._tie_starts:
                # within-measure match, fire event
                start_note = self._tie_starts[accidental_pitch]
                del self._tie_starts[accidental_pitch]
                self.handle_tie(start_note, note_element)
            elif accidental_pitch in self._previous_tie_starts:
                # cross-measure match, fire event
                start_note = self._previous_tie_starts[accidental_pitch]
                del self._previous_tie_starts[accidental_pitch]
                self.handle_tie(start_note, note_element)
        
        if has_start:
            self._tie_starts[accidental_pitch] = note_element
    
    def handle_tie(self, start_note: ET.Element, stop_note: ET.Element):
        # copy the pitch element children over, so that any <alter> element is set as well
        start_pitch = start_note.find("pitch")
        stop_pitch = stop_note.find("pitch")
        assert stop_pitch is not None
        assert start_pitch is not None
        stop_pitch[:] = copy.deepcopy(list(start_pitch[:]))

    def determine_alter_and_cautionarity(
            self,
            note_element: ET.Element,
            note_onset: MeasureOnset,
    ) -> tuple[int, bool | None]:
        """Determines the alter and cautionarity for a `<note>` element.
        
        Returns a tuple, where first comes the alter value as int
        and second comes the cautionarity, which is bool or None
        if this node does not have a local accidental.
        """
        assert note_element.tag == "note"
        accidental_pitch = AccidentalPitch.from_note_element(note_element)
        
        # accidental that is locally defined at this <note>
        local_accidental = note_element.findtext("accidental")
        
        # accidental carried from previous notes in the measure
        carried_accidental = self._accidental_map.get_carried_accidental(
            accidental_pitch=accidental_pitch,
            onset=note_onset
        )

        # accidental carried from key signature
        key_signature_accidental = self.get_key_signature_accidental(
            step=Pitch.from_diatonic_index(accidental_pitch.diatonic_index).step
        )

        # go from least-specific to most-specific accidentals
        # and update values accordingly
        actual_accidental: str | None = None
        is_cautionary: bool | None = None

        # key signatures are most general
        if key_signature_accidental is not None:
            actual_accidental = key_signature_accidental
        
        # then carried accidentals are second-most specific
        if carried_accidental is not None:
            actual_accidental = carried_accidental
        
        # finally, local accidentals are most-specific
        if local_accidental is not None:
            # cautionary accidental is a local accidental that
            # would not change the actual accidental if it was missing
            # (natural is special since it sort of "equals" None)
            is_cautionary = (
                actual_accidental == local_accidental
                or (actual_accidental == None and local_accidental == "natural")
            )

            # and regardless of cautionarity, we use the local
            # accidental as the most-specific one
            actual_accidental = local_accidental

        # return both found values
        return accidental_to_alter(actual_accidental), is_cautionary
    
    def get_key_signature_accidental(self, step: Step) -> str | None:
        """Returns the accidental comming from the currently active
        key signature at the specified pitch step"""
        _SHARPS = ["F", "C", "G", "D", "A", "E", "B"] # fis, cis, gis, ...
        _FLATS = ["B", "E", "A", "D", "G", "C", "F"] # b, es, as, des, ...
        
        # sharp key signatures
        if self._key_signature > 0:
            if step.value in _SHARPS[0:self._key_signature]:
                return "sharp"
        
        # flat key signatures
        elif self._key_signature < 0:
            if step.value in _FLATS[0:-self._key_signature]:
                return "flat"

        # no accidental from key signature
        return None
