import xml.etree.ElementTree as ET
from lmx.tokenization.io.parse_lmx_tokens_from_string import parse_lmx_tokens_from_string
from lmx.tokenization.io.read_lmx_tokens_from_file import read_lmx_tokens_from_file
from lmx.tokenization.io.serialize_lmx_tokens_to_string import serialize_lmx_tokens_to_string
from pathlib import Path, PurePath
from lmx.tokenization.Decoder import Decoder
from typing import TextIO
from io import StringIO


def lmx_decode_part(
        lmx: str | list[str] | Path,
        error_tape: TextIO | None = None,
        keep_fractional_durations = False,
) -> ET.Element:
    """Decodes given LMX string/tokens/file to a MusicXML element tree with
    a single `<part>` element, containing the decoded musical content.
    
    This function is supposed to be used in decoding tests,
    as it supports file path arguments and provides a single
    point of refactoring if the decoder API changes.

    :params lmx: The raw LMX string, parsed LMX tokens,
        or a path to a file that contains LMX.
    :params error_tape: Output towards which decoder errors will be directed.
        If left empty, then an assertion is run after decoding, that no errors
        were in fact emitted.
    :params keep_fractional_durations: Instead of computing divisions as
        the lowest common multiple of durations, the output MusicXML
        `<duration>` elements are left with fractional representations.
    """

    # parse lmx string
    if type(lmx) is str:
        lmx_tokens = parse_lmx_tokens_from_string(
            lmx_string=lmx,
            check_with_vocabulary=True,
        )
    # read file
    elif isinstance(lmx, PurePath):
        lmx_tokens = read_lmx_tokens_from_file(
            file_path=lmx,
            check_with_vocabulary=True,
        )
    # nothing necessary
    elif type(lmx) is list:
        lmx_tokens = lmx
    else:
        raise ValueError(
            f"Given 'lmx' argument is of invalid type {type(lmx)}"
        )
    
    # prepare default error tape
    # (used only if the user did not provide one)
    default_error_tape = StringIO()

    # build the decoder
    decoder = Decoder(
        errout=default_error_tape if error_tape is None else error_tape,
        keep_fractional_durations=keep_fractional_durations,
    )

    # run decoding
    decoder.process_text(
        # TODO: the decoder API should be refactored
        serialize_lmx_tokens_to_string(lmx_tokens)
    )

    # check the default error tape, that it's empty
    if error_tape is None:
        errors = default_error_tape.getvalue()
        if errors != "":
            raise RuntimeError(
                f"LMX decoder produced unexpected errors. Provide custom " +
                f"error tape argument if you expect these errors to occur. " +
                f"The errors:\n{repr(errors)}"
            )

    return decoder.part_element
