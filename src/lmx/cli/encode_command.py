import sys
import argparse
from pathlib import Path
from ..tokenization.Encoder import Encoder
import xml.etree.ElementTree as ET
from ..musicxml.io.read_musicxml_tree_from_file \
    import read_musicxml_tree_from_file
from ..musicxml.io.parse_musicxml_tree_from_string \
    import parse_musicxml_tree_from_string


def define_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input MusicXML file (.xml, .musicxml, .mxl), " +
        "if not provided the standard input is read instead"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output LMX file (.lmx), if not provided, " +
        "the standard output is used instead"
    )
    parser.add_argument(
        "--part",
        type=str,
        required=True,
        help="XML ID of the <part> element to encode, e.g. 'P1'"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forces an overwrite of the output file"
    )


def execute(parser: argparse.ArgumentParser, args: argparse.Namespace):
    input_path = None if args.input is None else Path(args.input)
    output_path = None if args.output is None else Path(args.output)
    part_id = str(args.part)
    force = bool(args.force)

    # do not overwrite the output file unless forced to
    if output_path is not None and output_path.exists() and not force:
        print(
            "The output file already exists. Use --force to overwrite it.",
            file=sys.stderr
        )
        exit(2)

    # parse the MusicXML into an ElementTree
    if input_path is None:
        musicxml_string = sys.stdin.read()
        musicxml_tree = parse_musicxml_tree_from_string(musicxml_string)
    else:
        musicxml_tree = read_musicxml_tree_from_file(input_path)
    
    # get the proper <part> XML element
    part_element = musicxml_tree.find("part#" + part_id)
    if part_element is None:
        all_part_ids = [
            p.attrib.get("id")
            for p in musicxml_tree.findall("part")
        ]
        print(
            f"No <part> element with ID '{part_id}' found.",
            file=sys.stderr
        )
        print(
            f"These are the available parts in the file: {repr(all_part_ids)}",
            file=sys.stderr
        )
        exit(3)
    
    # encode the MusicXML into LMX
    encoder = Encoder(
        errout=sys.stderr
    )
    encoder.process_part(part_element)
    lmx_string = " ".join(encoder.output_tokens)
    
    # write the LMX string to output
    if output_path is None:
        print(lmx_string)
    else:
        output_path.write_text(
            data=lmx_string,
            encoding="utf-8"
        )
