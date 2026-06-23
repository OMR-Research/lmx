from pathlib import Path
import zipfile


def read_musicxml_string_from_file(
        file_path: Path | str
) -> str:
    """Reads the given .musicxml, .xml, or .mxl file and returns
    the string representation of its MusicXML content.
    The compressed file variant is automatically deflated.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise Exception(f"Cannot find MusicXML file at {file_path}")

    # read compressed file
    if file_path.suffix == ".mxl":
        return _read_mxl(file_path)
    
    # read uncompressed file
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def _read_mxl(file_path: Path) -> str:
    # open the zip archive
    with zipfile.ZipFile(file_path, "r") as archive:
        # find the inner_file_name with the XML data
        for record in archive.infolist():
            # skip META-INF folder contents
            if record.filename.startswith("META-INF"):
                continue
            # accept any files with .xml or .musicxml suffixes
            if record.filename.endswith(".xml") \
                    or record.filename.endswith(".musicxml"):
                inner_file_name = record.filename
                break
        
        # open the XML file and read it
        with archive.open(inner_file_name) as file:
            return file.read().decode("utf-8")
