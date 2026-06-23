from dataclasses import dataclass
import xml.etree.ElementTree as ET
from collections import defaultdict
from enum import Enum
from typing import Optional


class ClefSign(str, Enum):
    C = "C"
    F = "F"
    G = "G"


class Step(str, Enum):
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    A = "A"
    B = "B"


# Diatonic steps above C4 (middle C) for each note name
DIATONIC_STEPS: dict[str, int] = {
    Step.C: 0,
    Step.D: 1,
    Step.E: 2,
    Step.F: 3,
    Step.G: 4,
    Step.A: 5,
    Step.B: 6,
}
STEP_FROM_DIATONIC: list[Step] = [t for t in Step]

# Semitones above C (within an octave) for each diatonic note
SEMITONES_IN_OCTAVE: dict[str, int] = {
    Step.C: 0,
    Step.D: 2,
    Step.E: 4,
    Step.F: 5,
    Step.G: 7,
    Step.A: 9,
    Step.B: 11,
}

# Clef reference: (step, octave) of the pitch that sits on `staff_line`
# These are the canonical pitches each clef sign anchors.
CLEF_REFERENCE: dict[ClefSign, tuple[str, int]] = {
    ClefSign.G: (Step.G, 4),  # G4 on line 2
    ClefSign.F: (Step.F, 3),  # F3 on line 4
    ClefSign.C: (Step.C, 4),  # C4 on line 3
}


@dataclass(frozen=True)
class StaffNumber:
    value: int

    def __post_init__(self) -> None:
        assert self.value in {1, 2}

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, StaffNumber)
        return self.value == other.value


def print_object(tree: ET.Element) -> bool:
    """
    Returns `True`, if the given element has
    print set to `yes` or the `print-object`
    attribute is missing.
    """
    po = tree.get("print-object")
    if po is None:
        return True
    if po == "no":
        return False
    return True


def clef_staff_number(tree: ET.Element) -> StaffNumber:
    sn = tree.get("number", "1")
    return StaffNumber(int(sn))


def note_staff_number(note_el: ET.Element) -> StaffNumber:
    sn = note_el.findtext("staff", "1")
    return StaffNumber(int(sn))


@dataclass
class ClefRepre:
    print_object: bool
    staff_number: StaffNumber
    staff_line: int
    sign: ClefSign
    octave_change: int = 0

    @classmethod
    def from_et(cls, clef_tree: ET.Element) -> "ClefRepre":
        def _line(tree: ET.Element) -> int:
            line = tree.findtext("line")
            assert line is not None
            return int(line)

        def _oc(tree: ET.Element) -> int:
            oc = tree.findtext("clef-octave-change")
            if oc is not None:
                return int(oc)
            return 0

        return cls(
            print_object=print_object(clef_tree),
            staff_number=clef_staff_number(clef_tree),
            staff_line=_line(clef_tree),
            sign=ClefSign(clef_tree.findtext("sign")),
            octave_change=_oc(clef_tree),
        )


TREBLE_CLEF_1 = ClefRepre(print_object=True, staff_number=StaffNumber(1), staff_line=2, sign=ClefSign.G)
TREBLE_CLEF_2 = ClefRepre(print_object=True, staff_number=StaffNumber(2), staff_line=2, sign=ClefSign.G)
BASS_CLEF_2 = ClefRepre(print_object=True, staff_number=StaffNumber(2), staff_line=4, sign=ClefSign.F)

CLEF_BOTH_TREBLE = [TREBLE_CLEF_1, TREBLE_CLEF_2]

@dataclass
class Pitch:
    step: Step
    alter: int
    octave: int

    @classmethod
    def from_et(cls, pitch_tree: ET.Element) -> "Pitch":
        alter = pitch_tree.findtext("alter")
        if alter is None:
            alter = 0
        else:
            alter = int(alter)

        return cls(Step(pitch_tree.findtext("step")), alter, int(pitch_tree.findtext("octave")))


def diatonic_index(step: str, octave: int) -> int:
    """
    Absolute diatonic index (0 = C0, 7 = C1, ...).
    """
    return octave * 7 + DIATONIC_STEPS[step]


def clef_pitch_at_line(clef: ClefRepre, line: int) -> int:
    ref_step, ref_octave = CLEF_REFERENCE[clef.sign]
    ref_diatonic = diatonic_index(ref_step, ref_octave)
    return ref_diatonic + (line - clef.staff_line) * 2 + 7 * clef.octave_change


def note_to_visual_line(pitch: Pitch, clef: ClefRepre) -> int:
    """
    Returns note `pitch` represented as a line number
    based on `clef`.
    """
    ref_diatonic = clef_pitch_at_line(clef, 1)
    return diatonic_index(pitch.step, pitch.octave) - ref_diatonic


def transpose_pitch_for_clef_change(
    pitch: Pitch,
    old_clef: ClefRepre,
    new_clef: ClefRepre,
) -> Pitch:
    # How many diatonic steps is this note above old clef's line 1?
    visual_position = note_to_visual_line(pitch, old_clef)

    # Apply same visual position in new clef
    new_abs_diatonic = clef_pitch_at_line(new_clef, 1) + visual_position

    new_octave, new_step_index = divmod(new_abs_diatonic, 7)
    new_step = STEP_FROM_DIATONIC[new_step_index]
    return Pitch(step=new_step, alter=pitch.alter, octave=new_octave)


def transpose_pitch_for_score_part(
    part_element: ET.Element, staff_count: int, transpose_to: Optional[list[ClefRepre]] = None
) -> ET.Element:
    """
    Goes through the whole score in two passes. In the first pass, the first (lowest onset)
    visible clefs are found for each staff and the invisible clefs at the starts of the staffs
    are updated to match the final clefs given as `transpose_to`.
    
    In the second pass, every element with a pitch is updated to match with the updated invisible
    clefs. Only those elements, whose onset is the lower than the onset of the first visible clef
    on the same staff, are updated. Elements with pitch played after a visible clef are not affected
    by the invisible ones.

    Modification are done to the given `part_element`.

    If `transpose_to` is `None`, both staffs are assumed to have treble clef.
    """
    if transpose_to is None:
        transpose_to = [TREBLE_CLEF_1, TREBLE_CLEF_2]

    # suppose that hidden clefs are only at the start of the score
    assert staff_count in {1, 2}

    first_shown_clef_onset: defaultdict[StaffNumber, float] = defaultdict(lambda: float("inf"))
    hidden_clefs: dict[StaffNumber, ClefRepre] = {}

    # transpose_to = ClefRepre(print_object=True, staff_number=StaffNumber(1), staff_line=4, sign=ClefSign.F)
    new_clef_by_staff: dict[StaffNumber, ClefRepre] = {c.staff_number: c for c in transpose_to}


    def update_hidden_clef(old_clef_el: ET.Element, new_clef: ClefRepre) -> None:
        assert old_clef_el.get("number", "1") == str(new_clef.staff_number.value)

        old_clef_el.find("sign").text = new_clef.sign.value
        old_clef_el.find("line").text = str(new_clef.staff_line)

    # first, find the first shown clef
    onset = 0
    for measure in part_element.findall(".//measure"):
        for child in measure:
            if child.tag == "attributes":
                # find shown clefs
                for clef_el in child.findall("clef"):
                    # process shown clef
                    if print_object(clef_el):
                        sn = clef_staff_number(clef_el)
                        first_shown_clef_onset[sn] = min(first_shown_clef_onset[sn], onset)
                    # process hidden clef
                    else:
                        assert onset == 0, (f"Hidden clef has onset not equal to 0, {onset}")
                        h_clef = ClefRepre.from_et(clef_el)
                        hidden_clefs[h_clef.staff_number] = h_clef

                        update_hidden_clef(clef_el, new_clef_by_staff[h_clef.staff_number])

            else:
                duration = child.findtext("duration")

                if duration is not None:
                    if child.tag == "backup":
                        onset -= int(duration)
                    else:
                        onset += int(duration)

    if all(first_shown_clef_onset[StaffNumber(s)] == 0 for s in range(1, staff_count + 1)):
        # print("Skipping, all first visible clefs have onset 0")

        return part_element

    if not all(hidden_clefs.get(StaffNumber(s)) is not None for s in range(1, staff_count + 1)):
        raise ValueError(f"Missing hidden clef for one or more staffs, found clefs: {hidden_clefs}, expected {staff_count}")

    def compute_new_pitch_and_update(
        pitch_el: ET.Element, old_clef: ClefRepre, new_clef: ClefRepre
    ) -> None:
        """
        Updates given pitch.
        """
        old_pitch = Pitch.from_et(pitch_el)
        new_pitch = transpose_pitch_for_clef_change(old_pitch, old_clef, new_clef)
        pitch_el.find("step").text = new_pitch.step.value  # type: ignore
        pitch_el.find("octave").text = str(new_pitch.octave)  # type: ignore

    # second iteration, change pitch for affected notes
    onset = 0
    for measure in part_element.findall(".//measure"):
        for child in measure:
            # if it has pitch, update
            if child.tag == "note":
                p = child.find("pitch")
                if p is None:
                    pass
                else:
                    sn = note_staff_number(child)
                    if onset < first_shown_clef_onset[sn]:
                        compute_new_pitch_and_update(p, hidden_clefs[sn], new_clef_by_staff[sn])

            # update onset
            duration = child.findtext("duration")
            if duration is not None:
                if child.tag == "backup":
                    onset -= int(duration)
                else:
                    onset += int(duration)

    return part_element