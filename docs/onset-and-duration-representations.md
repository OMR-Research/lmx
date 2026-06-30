# `Onset` and `Duration` representations

Many elements in MusicXML define a `<duration>` value (an integer) that specifies how much musical time that element takes up. The duration is expressed in *divisions* units, meaning if a `<note>` has `<duration>` of 5, then that note takes up 5 time divisions. What one division means is encoded by the `<divisions>` element, which defines the number of divisions in a single quarter note (as an integer again). The `<divisions>` element must be present at the beginning of a `<part>` in its first `<attributes>` element.

This alone is already quite a complex logic and keeping everything as python `int` values could lead to mistakes where durations with different divisions units may be combined unknowingly without an exception being raised.

Moreover, these duration values exist in MusicXML for MIDI playback functionality and it does not impact visual appearance. For that, note `<type>` should be used. When the LMX decoder runs, it does not yet know all the `<type>` values it will encounter in all of its combinations in tuplets and tremolos, so it cannot decide a `<divisions>` value upfront. Instead, the decoder works with so-called *fractional duration* representation.

This representation is only present in this package (it's not a MusicXML standard), however, it simplifies much of this package's codebase. It represents `<duration>` values with python `fraction.Fraction` objects directly as a fraction of a quarter note. This lets us work without having explicit `<divisions>` (each value has its own denominator) and at the end of decoding, these values can be in-bulk converted to MusicXML *actual* durations.

So apart from the MusicXML complexity, we also have to handle two types of duration representations:

- `ActualDuration` - this is what MusicXML defines
- `FractionalDuration` - an LMX internal construct to ease decoding

These two representation may not be mixed - you choose one for your processing and use it throughout the code. Also, since `ActualDuration` depends on the `<divisions>` value, two actual durations of different divisions also cannot be mixed. Again, you choose the divisions you work with and you use them everywhere. Conversions may only be done at the level of an entire `<part>`.

Moreover, music has the concept of an *onset* - meaning the moment in time, when some event occurs (a note starts playing). Onset can be consturcted by adding up note durations as they are played. Because onset is built on top of duration, this also yields two different implementations of it - *actual onset* and *fractional onset*, depending on which `Duration` representation is used internally.

Onset is only meaningful if you specify what the onset zero means. You could specify the start of a `<part>` to be onset 0, but that causes issues with measures. Not all measures have the same length, not all measures are error-free (some complex tuplets exported from MuseScore break some invariants) plus MusicXML itself does not have a concept of "measure duration". A measure is as long as its content and the time signature is only a cue, not a hard rule.

For this reason it is better to define onset only from the beginning of a measure, so that errors in one measure do not spread to the following measures. However, when processing an entire `<part>`, you still need to orient yourself globally. That's why distinguish between `MeasureOnset` and `PartOnset`. Measure onset is simply the duration since the start of the measure. Part onset consists of two values: the index of curent measure, and the onset within that measure. Together they uniquely identify any semantic onset within a MusicXML document, while handling underfull and overfull measures well.


## Python value objects

The domain model described above is implemented in code in the `lmx.musicxml.time` module. These are the relevant classes:

- `ActualDuration`: Duration integer and divisions integer as defined by MusicXML, packed together as a single object, with strict checks that prohibit illegal operations (e.g. adding durations of different divisions).
- `FractionalDuration`: Same semantic concept of duration, only expressed as a python `Fraction` of quarter notes. Does away with divisions.
- `Duration`: Abstract base class for the two types above, for writing code that does not care about the chosen representation, only about its semantics.

> **Note:** This inheritance is very similar to Python `pathlib`'s `Path`, `PosixPath`, `WindowsPath` types.

- `MeasureOnset`: Onset within a `<measure>`, internally represented by a `Duration`, which may be either actual or fractional.
- `PartOnset`: Onset within a `<part>`, internally represented by a zero-based measure index and a `MeasureOnset` within that measure. Again, it may be either actual or fractional.


### Arithmetics

Both `Duration` types support adition, subtraction and unary minus (duration may be negative, e.g. for the `<backup>` element). These operations check that both operands have the same representation (fractionality or divisions number).

```py
from lmx.musicxml.time.ActualDuration import ActualDuration

half_note = ActualDuration(value=2, divisions=1)
quarter_note = ActualDuration(value=1, divisions=1)

assert quarter_note + quarter_note == half_note
```

Onset types also support arithmetics, but with different conditions:

- Duration can be added to onset to produce another onset
- Two onsets cannot be added (it does not make sene)
- Two onsets may be subtracted to produce a duration

Additionaly, `PartOnset` arithmetics only works on two operands that point to the same measure index (otherwise their relative distance spans a measure boundary which cannot be represented as a `Duration`).


### Fractional duration in XML

Short durations (less than a quarter note) are represented in `FractionalDuration` by a fraction with non-one denominator. This means when they are serialized to string, you get two numbers with a slash, e.g. `1/2` for an eighth note. But long durations become integers (have denominator equal to one), which means they are serialized as a number, e.g. `2` for a half note.

Seeing this in the XML does not communicate, which representation is used:

```xml
<duration>2<duration>
```

It may be a half note in fractional representation, or it may be almost anything in actual representation.

For this reason, fractional durations (if serialized) have a `fractional="yes"` attribute:

```xml
<duration fractional="yes">2<duration>
```

If this attribute is missing, the duration is actual.

However, in practise, you have very little reason to serialize fractional MusicXML to XML, since MuseScore does not understand it. It is mainly defined in this way to handle unit tests and make asserts more explicit.
