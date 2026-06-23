from .read_lmx_string_from_file import read_lmx_string_from_file
from .parse_lmx_tokens_from_string import parse_lmx_tokens_from_string
from pathlib import Path


def read_lmx_tokens_from_file(
        file_path: Path | str,
        check_with_vocabulary=True,
) -> list[str]:
    """Reads the given .lmx file and returns its content as a parsed
    sequence of LMX tokens.
    
    :param file_path: Path to the file to be read.
    :param check_with_vocabulary: Raises an error when
        an unknown token is encountered.
    """
    lmx_string = read_lmx_string_from_file(
        file_path=file_path
    )
    lmx_tokens = parse_lmx_tokens_from_string(
        lmx_string=lmx_string,
        check_with_vocabulary=check_with_vocabulary,
    )
    return lmx_tokens
