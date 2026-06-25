# Omitted staff header normalization

In old handwritten music it is often the case that clefs and key signatures are omitted on new systems and sometimes even new pages (especially in particella). The reader is expected to know them from the previous page:

<img src="omitted-header-scan.jpg" width="600">

> **Note:** Example taken from the `CVC.Dolores` dataset, page `CEDOC_CMM_1.5.1_0082.015`, downloadable from [here](http://hdl.handle.net/20.500.12800/1-6147).

This poses problems for MusicXML transcription of these pages (or individual staves), since MusicXML requires these symbols to be present:

<img src="omitted-header-transcription.png" width="600">

The solution for annotators is to look up the correct clef, key signature and time signature from previous pages (to preserve replayability) and put them into the transcription while flagging them as invisible (to preserve the same appearance).

However, annotators are inconsistent and forget to look up everything. The example above should also have a hidden key signature (because there is a natural accidental in the third measure) but the annotator did not note it down in MusicXML.

All of this variability and inconsistency makes it difficult to train an OMR model, because the gold MusicXML's note pitches depend on clefs and key signatures. If the model guesses the invisible clef incorrectly, then even though it recognizes notes properly, they would not align with the gold annotation and a phantom error would appear.

The solution is to normalize all invisible clefs to G clef, and invisible key signatures to null key signature, so that the OMR model learns one consistent behaviour. Note pitches have to be adjusted appropriately to preserve the visual appearance of the rendered MusicXML. Accidentals are not an issue, since they are encoded explicitly (`<accidental>` element) regardless of the actual pitch shift (`<alter>` element).

The `lmx.musicxml.omitted_staff_header` module provides utility functions for this normalization.

> **Note:** The *staff header* refers collectively to clefs, key signatures and time signatures at the beginning of staves. To our best knowledge, there is no well-known musical term for this collection of symbols.


## Clefs

Clef normalization means converting any wild clefs that may be in the data:

<img src="wild-clefs.png" width="600">

To the clefs expected by the OMR model (say G-F clefs for a piano model):

<img src="normalized-clefs.png" width="600">

This process requires us to change the clefs themselves, but then also transposing all notes that follow these clefs to preserve their visual appearance on the staff. Notice that the first two notes in the top image are `D3`, while after normalization to G and F clef they become `C4` and `E2` respectively. This transposition must happen for all notes up until a clef change in the respective staff (see clef changes in the second measure).

This transposition is NOT a typical harmonic transposition, because music notation is visually represented as a diatonic scale with two semitones. These two semitones would introduce two accidentals if a naive "fixed-number-of-semitones" transposition was used.

Because the transposition preserves visual appearance, existing accidentals in the score do not pose a problem. Notes that had an accidental originally will have that same accidental after the transposition (which will correspond to the same `<alter>` pitch value). In other words, only the pitch `<step>` and `<octave>` values change.

To perform the normalization visualized above, use the following code:

```py
from lmx.musicxml.omitted_staff_header.normalize_invisible_header_clef \
    import normalize_invisible_header_clef, Clef
from lmx.musicxml.omitted_staff_header.Clef \
    import G_CLEF, F_CLEF

normalized_part = normalize_invisible_header_clef(
    part_element=my_part, # MusicXML <part> element as ET.Element
    desired_clef=[G_CLEF, F_CLEF], # default piano clefs
    when_clef_visible="raise-exception", # be careful
)
```

The function returns a modified copy of the input `<part>` element.

The `desired_clef` argument may be one `Clef` or a list of `Clefs` if the part has multiple staves (e.g. piano).

The `when_clef_visible` option controls the function's behaviour when the header clef(s) is not invisible. This is unexpected behaviour, since we call this function precisely to handle invisible header clefs. You can choose from these options:

- `raise-exception`: The careful variant where the function raises a `ValueError`.
- `dont-normalize`: The staff is completely ignored, leaving everything as it is.
- `normalize-keep-visible`: Performs the clef change and note transposition, while keeping the header clef visible.
- `normalize-set-invisible`: Performs the clef change and note transposition, while forcing the header clef to become invisible.

This option applies to each staff independently (except for the exception of course), so if only one clef is visible, that clef's staff will be treated according to these rules, while the other invisible clefs are normalized as usual.

The option you choose depends on what you know about the data you process:

- If you don't know why header clefs should be visible, use `raise-exception`.
- If you know the clef is not visible (some external human annotation) and the MusicXML may be in unknown state, use `normalize-set-invisible`.
- If you transform data, where the MusicXML definitely has invisible clefs in places where there really are omitted clefs in the image, but some of the data has perfectly normal visible clefs that you want to skip, use `dont-normalize`.
- The `normalize-keep-visible` option is present only for completeness, I'm unsure about when it might be needed.


## Key signatures

TODO: how key signatures behave and how are normalized


## Time signatures

TODO: how time signatures behave and how are normalized (they aren't)


## Forcing invisible staff header

Sometimes you know that the image has omitted staff header, yet the MusicXML has the header transcribed as visible. You can explicitly set header symbols as visible or invisible using these function:

Setting header clef visibility:

```py
from lmx.musicxml.omitted_staff_header.set_header_clef_visibility \
    import set_header_clef_visibility

set_header_clef_visibility(
    part_element=my_part, # modifies the <part> in-place
    set_visibility="visible", # or "invisible"
)
```

Setting header key signature visibility:

```py
TODO
```

Setting header time signature visibility:

```py
TODO
```

These functions only work by adding or removing the `print-object="no"` XML attribute.
