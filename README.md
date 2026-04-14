# Linearized MusicXML (LMX)

[![License Apache 2.0](https://badgen.net/badge/license/mit/blue)](https://github.com/OMR-Research/lmx/blob/main/LICENSE)
[![PyPI version](https://badge.fury.io/py/linearized-musicxml.svg)](https://pypi.org/project/linearized-musicxml/)
[![Downloads](https://static.pepy.tech/badge/linearized-musicxml)](https://pepy.tech/project/linearized-musicxml)
![Python Version](https://badgen.net/badge/python/3.8+/cyan)

<div align="center">
    <br/>
    <img src="docs/assets/lmx-logo.svg" width="400px">
    <br/>
    <br/>
    <br/>
</div>

> **🚨 `v2-development` branch:** This branch is where the v2.0.0 of the LMX package is being developed.

The ultimate, zero-dependency toolkit for image-to-sequence models and MusicXML.

Provides:

- **Robust tokenization of MusicXML (encoding & decoding)**
- Utilities for reading and manipulating MusicXML documents

What it looks like:

```xml
<!-- This MusicXML: -->
<measure>
    ...
    <note>
        <pitch>
            <step>C</step>
            <alter>1</alter>
            <octave>4</aoctave>
        </pitch>
        <duration>15</duration>
        <voice>1</voice>
        <type>eighth</duration>
        <stem>up</stem>
        <staff>1</staff>
        <beam number="1">end</beam>
    </note>
    <backup>
        <duration>120</duration>
    </backup>
    ...
</measure>

<!-- Corresponds to these LMX tokens: -->
measure
    ...
    C4 voice:1 eighth stem:up staff:1 beam:end
    backup whole
    ...

<!-- (whitespace separates tokens) -->
```


## Usage

Install via:

```
pip3 install linearized-musicxml
```

This registers a CLI called `lmx` that now can be used:

```bash
# MusicXML -> LMX (accepts both .musicxml and .mxl)
lmx encode --input gold.musicxml --output gold.lmx
lmx encode --input gold.mxl # prints to standard output
cat gold.musicxml | lmx encode # also prints to stdout

# LMX -> MusicXML (only uncompressed MusicXML output available)
lmx decode --input prediction.lmx --output prediction.musicxml
lmx decode --input prediction.lmx # prints to standard output
cat prediction.lmx | lmx decode # also prints to stdout
```

The CLI can also be called this way:

```bash
python3 -m lmx [arguments...]
```

TODO: how to use from python?


## Documentation

- [Design process notes](docs/design-process-notes/design-process-notes.md)
    - [Reference documentation](docs/design-process-notes/design-process-notes.md#reference-documentation)
    - [Pseudo grammar](docs/design-process-notes/design-process-notes.md#pseudo-grammar)
    - [MusicXML element reference](docs/design-process-notes/design-process-notes.md#musicxml-element-reference-with-implementation-notes)


## Acknowledgement

This package is derived from code first developed for an ICDAR 2024 paper by Mayer et al. If you use it for your research, please cite this paper:

Jiří Mayer, Milan Straka, Jan Hajič jr., Pavel Pecina. Practical End-to-End Optical Music Recognition for Pianoform Music. 18th International Conference on Document Analysis and Recognition, ICDAR 2024. Athens, Greece, August 30 - September 4, pp. 55-73, 2024.
**DOI:** https://doi.org/10.1007/978-3-031-70552-6_4
**GitHub:** https://github.com/ufal/olimpic-icdar24
