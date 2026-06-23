from pathlib import Path
from .serialize_lmx_tokens_to_string import serialize_lmx_tokens_to_string


def write_lmx_tokens_to_file(
        file_path: Path | str,
        lmx_tokens: list[str],
        make_parent_folder=True
):
    """Writes LMX tokens to an .lmx file"""
    
    # TODO: add an option for pretty-printing

    if make_parent_folder:
        Path(str(file_path)).parent.mkdir(exist_ok=True, parents=True)
    
    lmx_string = serialize_lmx_tokens_to_string(
        lmx_tokens=lmx_tokens
    )

    file_path.write_text(lmx_string, encoding="utf-8")
