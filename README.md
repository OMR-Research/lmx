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

A python package for linearizing and de-linearizing MusicXML into a sequential format so that it can be used for training img2seq machine learning models.

Install via:

```
pip3 install linearized-musicxml
```

Use from the command line:

```bash
# MusicXML -> LMX (accepts both XML and MXL)
python3 -m lmx linearize example.musicxml # produces example.lmx
python3 -m lmx linearize example.mxl # produces example.lmx
cat example.musicxml | python3 -m lmx linearize - # prints to stdout (only uncompressed XML input)

# LMX -> MusicXML (only uncompressed XML output available)
python3 -m lmx delinearize example.lmx # produces example.musicxml
cat example.lmx | python3 -m lmx delinearize - # prints to stdout
```

## Acknowledgement

This package uses code first developed for an ICDAR 2024 paper by Mayer et al. See the acknowledgement there: https://github.com/ufal/olimpic-icdar24
