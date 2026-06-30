from pathlib import Path, PurePath
from .MuseScore import MuseScore
import xml.etree.ElementTree as ET
import tempfile
from ..musicxml.part_to_score import part_to_score
from ..musicxml.io.write_musicxml_tree_to_file \
    import write_musicxml_tree_to_file
import shutil
import subprocess
import json
import os
import copy


def render_staff(
        ms: MuseScore,
        part_element: ET.Element | list[ET.Element],
        output_png_file: Path | list[Path],
        render_invisible_attributes=False,
        dpi=300,
        page_width_tenths=4000,
        print_musescore_output=False,
        print_tmpfolder_before_exitting=False,
):
    """Renders a single staff (or grandstaff) as a single wide PNG image.

    The height of the image is not fixed as it depends on the MusicXML content,
    but it is very stable. The musical content is cropped with padding
    corresponding to the height of a single staff, however it is not cropped
    around the staff but around the black pixels in the image (cropping is
    done inside MuseScore via the --trim-image option). Resolution may be
    controlled via DPI.
    
    It also operates in batch mode, when a list of inputs and outputs is given,
    invoking MuseScore only once.

    The function was debugged against MuseScore 4.6.5

    :param ms: The MuseScore executable to do the rendering with.
    :param part_element: The `<part>` MusicXML element to render (or a list).
        Any page or system breaks it may include are IGNORED during render,
        since this method aims at single-staff rendering.
    :param output_png_file: Path to the output PNG file to create (or a list).
    :param render_invisible_attributes: Makes invisible clefs/signatures
        visible as gray. Useful for debugging.
    :param dpi: DPI at which to rasterize the image.
    :param page_width_tenths: What page width to use for rendering. If the staff
        is too long and gets wrapped to multiple lines, increase this number.
        This number does NOT correspond to output image width, since the output
        image is cropped to content. It only exists, because MuseScore has to
        render to a physical page. The unit used is "tenths", where 40 is
        one staff height, also corresponding to 7 millimeters. So the
        default of 4_000 corresponds to 100x the staff height.
    :param print_musescore_output: Used for debugging, lets the MuseScore
        standard output and error be printed to console.
    :param print_tmpfolder_before_exitting: Used for debugging,
        prints the contents of the temporary folder, within which
        MuseScore is executed.
    """
    # check arguments
    if type(part_element) is list:
        if type(output_png_file) is not list:
            raise ValueError(
                "When providing multiple input <part> elements, " +
                "you must also provide multiple output PNG paths."
            )
        if len(part_element) != len(output_png_file):
            raise ValueError(
                "The number of input <part> elements does not match " +
                "the number of output PNG paths."
            )
    
    # normalize arguments to lists
    if isinstance(part_element, ET.Element):
        part_elements = [part_element]
    else:
        part_elements = part_element
    
    if isinstance(output_png_file, PurePath):
        output_png_files = [output_png_file]
    else:
        output_png_files = output_png_file
    
    # number of input-output sample pairs
    sample_count = len(part_elements)

    # prepare MusicXML files for MuseScore
    musicxml_trees = [
        _prepare_part_as_musicxml_tree(
            part_element=pe,
            render_invisible_attributes=render_invisible_attributes,
            page_width_tenths=page_width_tenths,
        )
        for pe in part_elements
    ]

    # Setup the MuseScore machinery in a tmp folder
    with tempfile.TemporaryDirectory() as tmpdir:
        directory_path = Path(tmpdir)

        # each input-output sample gets a folder
        samples_folder = directory_path / "samples"
        samples_folder.mkdir()

        # write the MusicXML input file for each sample
        for sample in range(sample_count):
            (samples_folder / str(sample)).mkdir()
            write_musicxml_tree_to_file(
                samples_folder / str(sample) / "input.musicxml",
                musicxml_trees[sample],
                make_parent_folder=False
            )

        # prepare the batch conversion job file
        # (convert to both a PNG and another MusicXML file
        # to detect overflow line breaks)
        job_file_content = [
            {
                "in": str(samples_folder / str(sample) / "input.musicxml"),
                "out": [
                    str(samples_folder / str(sample) / "output.png"),
                    str(samples_folder / str(sample) / "output.musicxml"),
                ],
            }
            for sample in range(sample_count)
        ]
        with open(str(directory_path / "job.json"), "w") as f:
            json.dump(job_file_content, f)

        # run MuseScore
        subprocess.run(
            args=[
                str(ms.executable_path),
                "--job", str(directory_path / "job.json"),
                "--style", str(Path(__file__).parent / "render-staff-style.mss"),
                "--trim-image", str(int((7 / 24.4) * dpi)), # 7mm at given DPI
                "--image-resolution", str(int(dpi)),
            ],
            capture_output=not print_musescore_output,
            check=True, # fail on non-0 exit code
            env={
                **os.environ,
                "SKIP_LIBJACK": "", # we don't need audio
                "XDG_CONFIG_HOME": str(directory_path), # use default config values
                "XDG_DATA_HOME": str(directory_path), # isolate
            }
        )

        # print tmp folder
        if print_tmpfolder_before_exitting:
            print()
            print("Printing temporary folder:")
            print("--------------------------")
            for item in directory_path.rglob("*"):
                print(item)
            print()
        
        # handle output sample by sample
        for sample in range(sample_count):
            # get the list of generated PNG files
            sample_png_files = list((samples_folder / str(sample)).glob("*.png"))
            assert len(sample_png_files) > 0, "MuseScore didn't produce an image"
            if len(sample_png_files) > 1:
                raise RuntimeError(
                    "There was a page-width overflow which resulted in" +
                    " multiple PNG files being generated. Either " +
                    "shorten the input <part> element, or increase " +
                    "the page_width_tenths argument value."
                )

            # move the png file to desired destination
            shutil.move(sample_png_files[0], output_png_files[sample])


def _prepare_part_as_musicxml_tree(
        part_element: ET.Element,
        render_invisible_attributes=False,
        page_width_tenths=4000,
):
    # make a copy of the part, since we're gonna be modifying it
    part_element = copy.deepcopy(part_element)

    # remove page and system breaks
    for print_element in part_element.findall("part/measure/print"):
        if print_element.attrib.get("new-page", "no") == "yes":
            del print_element.attrib["new-page"]
        if print_element.attrib.get("new-system", "no") == "yes":
            del print_element.attrib["new-system"]
    
    # wrap part in musicxml
    musicxml_tree = part_to_score(
        part=part_element,
        part_id="P1",
        part_name="", # empty so that it doesn't render
        musicxml_version="4.0"
    )

    # add the defaults element which defines page size and margins
    # Page height is set such that when a staff or grandstaff
    # overflows, it creates a new page (instead of a new system),
    # which will manifest as another output PNG file, which gets
    # detected and an error is raised.
    defaults_element = ET.fromstring(f"""
        <defaults>
            <scaling>
                <millimeters>7</millimeters>
                <tenths>40</tenths>
            </scaling>
            <page-layout>
                <page-height>450</page-height>
                <page-width>{page_width_tenths}</page-width>
                <page-margins type="both">
                    <left-margin>40</left-margin>
                    <right-margin>40</right-margin>
                    <top-margin>40</top-margin>
                    <bottom-margin>40</bottom-margin>
                </page-margins>
            </page-layout>
            <system-layout>
                <top-system-distance>0</top-system-distance>
            </system-layout>
        </defaults>
    """)
    musicxml_tree.getroot().insert(0, defaults_element)

    # render invisible attributes in gray
    if render_invisible_attributes:
        for element in [
            *musicxml_tree.findall("//clef"),
            *musicxml_tree.findall("//key"),
            *musicxml_tree.findall("//time")
        ]:
            if element.attrib.get("print-object", "yes") == "no":
                del element.attrib["print-object"]
                element.attrib["color"] = "#888888"

    return musicxml_tree
