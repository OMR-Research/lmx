from pathlib import Path
import zipfile


def load_musicxml_string(path_without_suffix: Path) -> str:
    """Loads MusicXML as string from compressed and uncompressed
    MusicXML files with various extensions (xml, musicxml, mxl)."""
    for suffix in [".xml", ".musicxml", ".mxl"]:
        path = path_without_suffix.with_suffix(suffix)
        if path.exists():
            break
    if not path.exists():
        raise Exception("Cannot find MusicXML file.")

    # load compressed file
    if path.suffix == ".mxl":
        return _load_mxl(path)
    
    # load uncompressed file
    with open(path, "r") as f:
        return f.read()


def _load_mxl(path: Path) -> str:
    # open the zip archive
    with zipfile.ZipFile(path, "r") as archive:
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
