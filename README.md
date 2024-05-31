# Linearized MusicXML (LMX)

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
