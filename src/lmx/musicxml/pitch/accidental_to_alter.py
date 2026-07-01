def accidental_to_alter(accidental: str | None) -> int:
    """Given the contents of the `<accidental>` element,
    returns the pitch `<alter>` value. None input is understood as
    a missing accidental, meaning alter of zero. This method does not
    handle carried accidentals and key signatures, it only implements the
    simple mapping from names to numbers.
    """
    if accidental is None:
        return 0

    if accidental == "sharp":
        return 1
    elif accidental == "flat":
        return -1
    elif accidental == "natural":
        return 0
    elif accidental == "double-sharp":
        return 2
    elif accidental == "flat-flat":
        return -2
    elif accidental == "natural-sharp":
        return 1
    elif accidental == "natural-flat":
        return -1

    raise ValueError("Unknown accidental: " + str(accidental))
