import xml.etree.ElementTree as ET
from .PartOnset import PartOnset
from .MeasureOnset import MeasureOnset
from .ActualDuration import ActualDuration
from .Duration import Duration
from .FractionalDuration import FractionalDuration


MEASURE_ELEMENT_CHILDREN: list[str] = [
    "note", "backup", "forward", "directions",
    "attributes", "harmony", "figured-bass",
    "print", "sound", "listening", "barline",
    "grouping", "link", "bookmark"
]
"""Lists element names that may appear inside a `<measure>` element"""


class OnsetVisitor:
    def __init__(self, divisions: int | None, record_onsets: bool):
        """Creates a new onset visitor instance.

        The expected usecase is to create a child class and override
        needed visit_... methods, however, the provided onset recording
        logic may be useful on its own so this class is not abstract.
        
        :param divisions: Divisions value to use for duration
            and onset representation. If None, fractional duration
            is used instead.
        :param record_onsets: Whether to remember measure child element
            onsets on the onset tape for later querying.
        """

        self._divisions = divisions
        """Divisions used for duration representation.
        None means use fractional representation."""

        self._finished: bool = False
        """Has the visitor ran already and finished without throwing?"""
        
        self._part_onset: PartOnset = PartOnset.zero(divisions)
        """Backing field for the 'part_onset' to make it read-only"""

        self._chord_durations: list[Duration] = []
        """Tracks durations of notes in a chord to determine the
        correct onset advancement off of them."""

        self._record_onsets = record_onsets
        """Whether onset tape recording is enabled"""

        self._onset_tape: dict[int, PartOnset] = {}
        """Remembers onsets for individual measure child elements.
        Keys are memory locations of ET.Element instances, obtained
        via the Python's id(...) function."""

    @property
    def part_onset(self) -> PartOnset:
        """Current onset within the `<part>`"""
        return self._part_onset
    
    @property
    def measure_index(self) -> MeasureOnset:
        """Zero-based index of the currently visited `<measure>` element"""
        return self.part_onset.measure_index
    
    @property
    def measure_onset(self) -> MeasureOnset:
        """Current onset within the current `<measure>`"""
        return self.part_onset.measure_onset
    
    def onset_of(self, element: ET.Element):
        """Returns the onset of a child element of a `<measure>`.
        
        This method may only be called after the visitor has run
        (otherwise the tape will not be fully built up)
        and only if tape recording was enabled.
        """
        if element.tag not in MEASURE_ELEMENT_CHILDREN:
            raise ValueError(
                f"Given <{element.tag}> element is not a possible " +
                "direct child of a <measure> so it isn't recorded."
            )
        
        if not self._record_onsets:
            raise RuntimeError(
                "Cannot query onsets, tape recording was disabled."
            )
        
        if not self._finished:
            raise RuntimeError(
                "Cannot query onsets, visitor has not yet finished running"
            )
        
        address = id(element)

        if address not in self._onset_tape:
            raise KeyError("Given element is not recorded on the tape")
        
        return self._onset_tape[address]
    
    def _advance_measure_onset(
            self,
            child_element: ET.Element,
            look_ahead: ET.Element | None
    ):
        # only these elements may contain <duration> element
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/duration/
        if child_element.tag not in [
            "backup", "figured-bass", "forward", "note"
        ]: return
        
        # get the <duration> element
        duration_element = child_element.find("duration")
        if duration_element is None:
            return # grace notes end up here

        # parse out the duration based on the selected representation
        if self._divisions is None:
            duration = FractionalDuration.from_fractional_xml_element(
                duration_element
            )
        else:
            duration = ActualDuration.from_xml_element(
                duration_element=duration_element,
                divisions=self._divisions,
            )
        
        # For <note> elements, onset is advanced only
        # after the last note of a <chord> is processed
        # (i.e. all notes in the chord have the same onset)
        # The duration of a chord is the maximum duration
        # of all the notes, which must be aggregated here.
        # The last note of a chord is encountered, when the
        # next measure element (look ahead) is NOT a <chord/> note.
        if child_element.tag == "note":
            is_last_note_of_chord = look_ahead is None \
                or look_ahead.tag != "note" \
                or look_ahead.find("chord") is None
            
            # this is the first note of a chord, reset durations
            if child_element.find("chord") is None:
                self._chord_durations = []
            
            # accumulate chord durations
            self._chord_durations.append(duration)

            # if this ISN'T the last note of a chord,
            # then we don't advance onset (we just accumulated duration)
            if not is_last_note_of_chord:
                return
            
            # if this IS the last note of a chord,
            # then we advance duration by the maximum chord note duration
            else:
                self._part_onset += max(self._chord_durations)
                self._chord_durations = [] # (not necessary, but just in case)
                return
        
        # backup element decreases onset
        if child_element.tag == "backup":
            self._part_onset += -duration
            return
        
        # I don't understand what the duration element means
        # on a figured bass element. If needed, must be implemented here.
        if child_element.tag == "figured-bass":
            raise NotImplementedError(
                "Duration element for figured-bass is not implemented"
            )
        
        # advance onset in any other case
        self._part_onset += duration

    def run(self, element: ET.Element):
        """Executes the visitor on given `<part>` or `<measure>`."""
        if element.tag not in ["measure", "part"]:
            raise ValueError(
                "Visitor may be run only on <part> or <measure> elements."
            )
        
        if self._finished:
            raise RuntimeError("An OnsetVisitor can only be run once")

        if element.tag == "part":
            self.visit_part(element)
        elif element.tag == "measure":
            self.visit_measure(element)

        self._finished = True
    
    #############################################################
    # These must be overriden with care, super() must be called #
    #############################################################
    # vvvv
    
    def visit_part(self, part_element: ET.Element):
        assert part_element.tag == "part"

        for measure_element in part_element:
            self.visit_measure(measure_element)

            # advance onset
            self._part_onset = self._part_onset.next_measure()

    def visit_measure(self, measure_element: ET.Element):
        assert measure_element.tag == "measure"
        
        for i, child_element in enumerate(measure_element):
            # record item on the tape
            if self._record_onsets:
                self._onset_tape[id(child_element)] = self.part_onset

            # visit the child            
            self.visit_measure_child(child_element)

            # advance measure onset
            look_ahead = None if i >= len(measure_element) - 1 \
                else measure_element[i + 1]
            self._advance_measure_onset(child_element, look_ahead)
    
    def visit_measure_child(self, child_element: ET.Element):
        assert child_element.tag in MEASURE_ELEMENT_CHILDREN

        # call visitor methods (overridable)
        if child_element.tag == "note":
            self.visit_note(child_element)
        elif child_element.tag == "attributes":
            self.visit_attributes(child_element)
        elif child_element.tag == "directions":
            self.visit_directions(child_element)
        elif child_element.tag == "forward":
            self.visit_forward(child_element)
        elif child_element.tag == "backup":
            self.visit_backup(child_element)
        elif child_element.tag == "harmony":
            self.visit_harmony(child_element)
        elif child_element.tag == "barline":
            self.visit_barline(child_element)
        elif child_element.tag == "figured-bass":
            self.visit_figured_bass(child_element)
        else:
            pass # ignore other elements
    
    #####################################
    # These may be overriden in any way #
    #####################################
    # vvvv

    def visit_note(self, note_element: ET.Element):
        assert note_element.tag == "note"
    
    def visit_attributes(self, attributes_element: ET.Element):
        assert attributes_element.tag == "attributes"
    
    def visit_directions(self, directions_element: ET.Element):
        assert directions_element.tag == "directions"
    
    def visit_forward(self, forward_element: ET.Element):
        assert forward_element.tag == "forward"
    
    def visit_backup(self, backup_element: ET.Element):
        assert backup_element.tag == "backup"
    
    def visit_harmony(self, harmony_element: ET.Element):
        assert harmony_element.tag == "harmony"
    
    def visit_barline(self, barline_element: ET.Element):
        assert barline_element.tag == "barline"
    
    def visit_figured_bass(self, figured_bass_element: ET.Element):
        assert figured_bass_element.tag == "figured-bass"
