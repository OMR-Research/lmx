import sys
import argparse
from pathlib import Path
from ..musescore.MuseScore import MuseScore
from ..musescore.render_staff import render_staff
from ..musicxml.io.read_musicxml_tree_from_file \
    import read_musicxml_tree_from_file


def define_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input MusicXML file (.xml, .musicxml, .mxl)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output PNG file",
    )
    parser.add_argument(
        "--render_invisible",
        action="store_true",
        help="Renders invisible attributes as gray"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="The DPI at which to rasterize the PNG image",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forces an overwrite of the output file"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enables all debug logging"
    )


def execute(parser: argparse.ArgumentParser, args: argparse.Namespace):
    input_path = None if args.input is None else Path(args.input)
    output_path = None if args.output is None else Path(args.output)
    render_invisible = bool(args.render_invisible)
    dpi = int(args.dpi)
    force = bool(args.force)
    debug = bool(args.debug)

    # do not overwrite the output file unless forced to
    if output_path is not None and output_path.exists() and not force:
        print(
            "The output file already exists. Use --force to overwrite it.",
            file=sys.stderr
        )
        exit(2)

    # parse the MusicXML into an ElementTree
    musicxml_tree = read_musicxml_tree_from_file(input_path)
    
    # get the proper <part> XML element
    if len(musicxml_tree.findall("part")) != 1:
        print(
            "Input MusicXML does not have only one <part> element.",
            file=sys.stderr
        )
        exit(1)
    
    # render the staff
    ms = MuseScore.resolve_linux_default()
    render_staff(
        ms=ms,
        part_element=musicxml_tree.find("part"),
        output_png_file=output_path,
        render_invisible_attributes=render_invisible,
        dpi=dpi,
        print_musescore_output=debug,
        print_tmpfolder_before_exitting=debug,
    )
