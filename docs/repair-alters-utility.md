# `repair_alters` utility

MusicXML represents semitone pitch adjustments both visually via the `<accidental>` element, as well as semantically via the pitch `<alter>` element. These two values should correspond to each other according to the rules of music notation (e.g. key signature accidentals, accidental carrying within a measure, etc.). However, there's a mismatch:

- LMX only cares about the visual part and ignores the semantic
- MuseScore only cares about the semantic part and ignores the visual (with an exception for cautionary accidentals)

This poses a challenge. In this LMX codebase, we often manipulate the visual part (i.e. during LMX decoding or clef normalization transpositions) and the semantic part is missing or gets desynchronized. In these situations we need to build or repair the semantic part, so the resulting MusicXML document renders properly when loaded by MuseScore. This is exactly, what the `repair_alters` function does.

Given a `<part>` element, it goes over all notes and updates their pitch `<alter>` values to match visible accidentals, plus also marks unnecessary accidentals as cautionary:

```py
import xml.etree.ElementTree as ET
from lmx.musicxml.pitch.repair_alters import repair_alters

my_part = ET.Element("part") # some loaded/decoded part

repair_alters(my_part)

# my_part now has its alters and cautionaries repaired
```
