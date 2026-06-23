from pathlib import Path


def read_lmx_string_from_file(file_path: Path | str) -> str:
    """Reads the given .lmx file and returns the string content of it
    
    This function currently does very little, but is present to make the LMX
    IO API consistent with the MusicXML's and also, it explicitly specifies
    the UTF-8 encoding when reading the string.
    """

    # Note to the future:
    # This method is NOT the place to process the content (e.g. remove possible
    # future LMX comments), rather it is to deal with various container file
    # formats, like the analogous compressed .mxl files of MusicXML.

    # just read the file...
    return Path(file_path).read_text("utf-8")
