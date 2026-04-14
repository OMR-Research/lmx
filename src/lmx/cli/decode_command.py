import sys
import argparse
from pathlib import Path
from ..tokenization.Decoder import Decoder
import xml.etree.ElementTree as ET
from ..musicxml.io.serialize_musicxml_tree_to_string \
    import serialize_musicxml_tree_to_string
from ..musicxml.io.write_musicxml_tree_to_file \
    import write_musicxml_tree_to_file
from ..musicxml.part_to_score import part_to_score


def define_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input LMX file (.lmx), " +
        "if not provided the standard input is read instead"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output MusicXML file (.musicxml, .xml), if not provided, " +
        "the standard output is used instead. Compression is not supported."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forces an overwrite of the output file"
    )


def execute(parser: argparse.ArgumentParser, args: argparse.Namespace):
    input_path = None if args.input is None else Path(args.input)
    output_path = None if args.output is None else Path(args.output)
    force = bool(args.force)

    # do not overwrite the output file unless forced to
    if output_path is not None and output_path.exists() and not force:
        print(
            "The output file already exists. Use --force to overwrite it.",
            file=sys.stderr
        )
        exit(2)

    # read the input LMX string
    if input_path is None:
        lmx_string = sys.stdin.read()
    else:
        lmx_string = input_path.read_text(
            encoding="utf-8"
        )

    # decode LMX into MusicXML ElementTree
    decoder = Decoder(
        errout=sys.stderr
    )
    decoder.process_text(lmx_string)
    musicxml_tree = part_to_score(decoder.part_element)

    # write the MusicXML tree to output
    if output_path is None:
        musicxml_string = serialize_musicxml_tree_to_string(
            musicxml_tree
        )
        print(musicxml_string)
    else:
        write_musicxml_tree_to_file(
            file_path=output_path,
            musicxml_tree=musicxml_tree,
            make_parent_folder=False
        )
