import xml.etree.ElementTree as ET
from pathlib import Path, PurePath
from typing import TextIO
from io import StringIO
from lmx.tokenization.Encoder import Encoder
from lmx.musicxml.io.parse_musicxml_tree_from_string import parse_musicxml_tree_from_string
from lmx.musicxml.io.read_musicxml_tree_from_file import read_musicxml_tree_from_file


def lmx_encode_part(
        musicxml: str | ET.ElementTree | ET.Element | Path,
        error_tape: TextIO | None = None,
) -> list[str]:
    """Encodes a given MusicXML string or file with a single `<part>`
    element, or a given `<part>` element into LMX tokens.
    
    This function is supposed to be used in decoding tests,
    as it supports file path arguments and provides a single
    point of refactoring if the encoder API changes.
    
    :params musicxml: The raw MusicXML string, parsed XML file or
        `<part>` element, or a path to a file that contains MusicXML.
    :params error_tape: Output towards which encoder errors will be directed.
        If left empty, then an assertion is run after encoding, that no errors
        were in fact emitted.
    """
    # parse a string and find the <part> element
    if type(musicxml) is str:
        part_element = _find_the_part_element(
            parse_musicxml_tree_from_string(musicxml)
        )
    # load the file and find <part> element
    elif isinstance(musicxml, PurePath):
        part_element = _find_the_part_element(
            read_musicxml_tree_from_file(musicxml)
        )
    # find the <part> element
    elif type(musicxml) is ET.ElementTree:
        part_element = _find_the_part_element(musicxml)
    # nothing necessary
    elif type(musicxml) is ET.Element:
        if musicxml.tag != "part":
            raise ValueError("Given ET.Element is not a `<part>` element.")
        part_element = musicxml
    else:
        raise ValueError(
            f"Given 'musicxml' argument is of invalid type {type(musicxml)}"
        )
    
    # prepare default error tape
    # (used only if the user did not provide one)
    default_error_tape = StringIO()
    
    # build the encoder
    encoder = Encoder(
        errout=default_error_tape if error_tape is None else error_tape,
        
        # check against vocabulary, what tokens are being emitted
        # (because some tokens are built dynamically from XML values)
        fail_on_unknown_tokens=True
    )

    # run encoding
    encoder.process_part(part_element)

    return encoder.output_tokens


def _find_the_part_element(musicxml_tree: ET.ElementTree) -> ET.Element:
    """
    Finds the only `<part>` element in the parsed MusicXML file.
    If there are multiple (or no) parts, raises an error.
    """
    part_elements = musicxml_tree.findall("part")

    if len(part_elements) == 1:
        return part_elements[0]
    
    raise ValueError(
        f"Given MusicXML tree is expected to contain exactly one `<part>` " +
        f"element, but it contains {len(part_elements)} instead."
    )
