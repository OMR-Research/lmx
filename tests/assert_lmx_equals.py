from pathlib import Path, PurePath
from lmx.tokenization.io.parse_lmx_tokens_from_string import parse_lmx_tokens_from_string
from lmx.tokenization.io.read_lmx_tokens_from_file import read_lmx_tokens_from_file


def assert_lmx_equals(
        given: str | list[str] | Path,
        expected: str | list[str] | Path,
):
    expected = prepare_lmx_value(expected)
    given = prepare_lmx_value(given)
    
    # pytest with -vv flag will show you exactly what's missing or added
    assert given == expected, "Given LMX is incorrect ('+' contains unexpected, '-' is missing)"


def prepare_lmx_value(value: str | list[str] | Path) -> list[str]:
    # parse string
    if type(value) is str:
        lmx_tokens = parse_lmx_tokens_from_string(
            lmx_string=value,
            check_with_vocabulary=True,
        )
    # load file
    elif isinstance(value, PurePath):
        lmx_tokens = read_lmx_tokens_from_file(
            file_path=value,
            check_with_vocabulary=True,
        )
    # nothing necessary
    elif type(value) is list:
        lmx_tokens = value
    else:
        raise ValueError(
            f"Given 'value' argument is of invalid type {type(value)}"
        )

    return lmx_tokens
