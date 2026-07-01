from ..pitch.Pitch import Pitch, Step
from ..pitch.Clef import Clef, ClefSign


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


def _clef_pitch_at_line(clef: Clef, line: int) -> int:
    ref_step, ref_octave = CLEF_REFERENCE[clef.sign]
    ref_diatonic = Pitch(
        step=ref_step,
        octave=ref_octave,
        alter=0
    ).diatonic_index
    return ref_diatonic + (line - clef.line) * 2 + 7 * clef.octave_change


def _note_to_visual_line(pitch: Pitch, clef: Clef) -> int:
    """
    Returns note `pitch` represented as a line number
    based on `clef`.
    """
    ref_diatonic = _clef_pitch_at_line(clef, 1)
    return pitch.diatonic_index - ref_diatonic


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
    visual_position = _note_to_visual_line(
        Pitch(step=pitch.step, octave=pitch.octave, alter=0),
        old_clef
    )

    # Apply same visual position in new clef
    new_diatonic_index = _clef_pitch_at_line(new_clef, 1) + visual_position
    new_pitch = Pitch.from_diatonic_index(new_diatonic_index)

    return Pitch(
        step=new_pitch.step,
        octave=new_pitch.octave,
        alter=pitch.alter,
    )
