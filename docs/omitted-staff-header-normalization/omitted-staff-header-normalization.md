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

TODO: how clefs behave and how are normalized


## Key signatures

TODO: how key signatures behave and how are normalized


## Time signatures

TODO: how time signatures behave and how are normalized (they aren't)


## Normalization functions

TODO: what can you call to do the normalization for you?


## Forcing invisible staff header

TODO: when the annotation is missing the "is invisible" value, but we know it should be invisible (and vice-versa?)
