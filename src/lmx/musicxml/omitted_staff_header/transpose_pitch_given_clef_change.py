from .Pitch import Pitch, Step
from .Clef import Clef, ClefSign


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
    "G": (Step.G, 4),  # G4 on line 2
    "F": (Step.F, 3),  # F3 on line 4
    "C": (Step.C, 4),  # C4 on line 3
}


def _diatonic_index(step: str, octave: int) -> int:
    """
    Absolute diatonic index (0 = C0, 7 = C1, ...).
    """
    return octave * 7 + DIATONIC_STEPS[step]


def _clef_pitch_at_line(clef: Clef, line: int) -> int:
    ref_step, ref_octave = CLEF_REFERENCE[clef.sign]
    ref_diatonic = _diatonic_index(ref_step, ref_octave)
    return ref_diatonic + (line - clef.line) * 2 + 7 * clef.octave_change


def _note_to_visual_line(pitch: Pitch, clef: Clef) -> int:
    """
    Returns note `pitch` represented as a line number
    based on `clef`.
    """
    ref_diatonic = _clef_pitch_at_line(clef, 1)
    return _diatonic_index(pitch.step, pitch.octave) - ref_diatonic


def transpose_pitch_given_clef_change(
    pitch: Pitch,
    old_clef: Clef,
    new_clef: Clef,
) -> Pitch:
    """
    Transposes pitch of a note when a clef is being replaced
    so that the visual position of the note does not change.

    :param pitch: The current pitch of the note.
    :param old_clef: The old clef for which the note was written down.
    :param new_clef: The new clef that replaces the old clef.
    """
    # How many diatonic steps is this note above old clef's line 1?
    visual_position = _note_to_visual_line(pitch, old_clef)

    # Apply same visual position in new clef
    new_abs_diatonic = _clef_pitch_at_line(new_clef, 1) + visual_position

    new_octave, new_step_index = divmod(new_abs_diatonic, 7)
    new_step = STEP_FROM_DIATONIC[new_step_index]
    return Pitch(step=new_step, alter=pitch.alter, octave=new_octave)
