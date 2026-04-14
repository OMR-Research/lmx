import argparse
from typing import Callable

parser = argparse.ArgumentParser(
    prog="lmx",
    description="CLI for the Linearized MusicXML python package"
)

subparsers = parser.add_subparsers(
    title="available commands",
    dest="root_command_name"
)

root_command_handlers: dict[
    str,
    Callable[[argparse.ArgumentParser, argparse.Namespace], None]
] = {}


############################
# Define all root commands #
############################


# === encode ===

import lmx.cli.encode_command
lmx.cli.encode_command.define_parser(
    subparsers.add_parser(
        "encode",
        aliases=[],
        description=
            "Encodes a MusicXML file into an LMX token sequence"
    )
)
root_command_handlers["encode"] = lmx.cli.encode_command.execute

# === decode ===

import lmx.cli.decode_command
lmx.cli.decode_command.define_parser(
    subparsers.add_parser(
        "decode",
        aliases=[],
        description=
            "Decodes an LMX token sequence into a MusicXML file"
    )
)
root_command_handlers["decode"] = lmx.cli.decode_command.execute


######################
# Execute the parser #
######################


def run():
    """
    This method is called from all the places
    that need a method reference to invoke this CLI
    """
    args = parser.parse_args()

    if args.root_command_name is None:
        parser.print_help()
        exit(2)

    root_command_handlers[str(args.root_command_name)](parser, args)


if __name__ == "__main__":
    run()
