from ..vocabulary import ALL_TOKENS


def parse_lmx_tokens_from_string(
        lmx_string: str,
        check_with_vocabulary=True,
) -> list[str]:
    """Given an LMX string, it parses out the LMX token sequence

    The process is:
    1) split string by whitespace (space, newline, tab)
    2) check tokens against vocabulary
    3) return
    
    :param lmx_string: The raw string from which LMX tokens should be parsed.
    :param check_with_vocabulary: Raises an error when
        an unknown token is encountered.
    """
    
    # split by whitespace
    tokens = lmx_string.split()

    # check vocabulary
    if check_with_vocabulary:
        for token in tokens:
            if token not in ALL_TOKENS:
                raise ValueError(f"Encountered unknown token: {token}")
    
    # return
    return tokens
